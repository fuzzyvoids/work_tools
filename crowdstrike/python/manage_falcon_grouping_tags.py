#!/usr/bin/env python3
"""
Add or remove CrowdStrike FalconGroupingTags for hosts.

This script uses FalconPy's Hosts service collection. The update call behind
Hosts.update_device_tags maps to the CrowdStrike Hosts tag update API and
changes cloud-side FalconGroupingTags. It does not change endpoint-local
SensorGroupingTags.

Credential lookup order:
    1. Explicit CLI arguments
    2. FALCON_CLIENT_ID, FALCON_CLIENT_SECRET, FALCON_BASE_URL
    3. FALCON_CLIENT_ID, FALCON_CLIENT_SECRET, FALCON_BASE_URL
    4. The configured profile section in FALCON_API_MD or API.md

Input options:
    - Positional hostnames
    - --device-id for known Falcon AIDs
    - --input-file path/to/hosts.txt, one hostname or AID per line
    - --input-file path/to/hosts.csv --csv-column hostname
    - Piped stdin

Examples:
    ./manage_falcon_grouping_tags.py --action add --tag example-tag host001 --dry-run
    ./manage_falcon_grouping_tags.py --action remove --tag example-tag --input-file hosts.txt
    ./manage_falcon_grouping_tags.py --action add --tag example-tag --device-id <aid> --force
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_API_MD = Path(os.environ.get("FALCON_API_MD", "API.md"))
DEFAULT_API_PROFILE = os.environ.get("FALCON_API_PROFILE", "default")
DEFAULT_GOV1_BASE_URL = os.environ.get("FALCON_DEFAULT_BASE_URL", "https://api.example.crowdstrike.com")
DEFAULT_BATCH_SIZE = 100
HOST_LOOKUP_LIMIT = 500


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Show default values while preserving example line breaks in --help."""


@dataclass(frozen=True)
class FalconConfig:
    """Resolved Falcon API connection settings."""

    client_id: str
    client_secret: str
    base_url: str


@dataclass(frozen=True)
class HostMatch:
    """A resolved Falcon host record used for confirmation and reporting."""

    requested_value: str
    device_id: str
    hostname: str
    platform_name: str
    status: str
    last_seen: str
    existing_tags: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    """Parse command-line options for lookup and tag management."""
    help_text = """Typical workflow:
  1. Verify read access: ./manage_falcon_grouping_tags.py --check-only
  2. Preview a change: ./manage_falcon_grouping_tags.py --action add --tag TAG --input-file hosts.txt --dry-run
  3. Apply the change: ./manage_falcon_grouping_tags.py --action add --tag TAG --input-file hosts.txt

Input examples:
  ./manage_falcon_grouping_tags.py --action add --tag example-tag host001 host002 --dry-run
  ./manage_falcon_grouping_tags.py --action remove --tag example-tag --input-file hosts.txt --dry-run
  ./manage_falcon_grouping_tags.py --action add --tag example-tag --input-file hosts.csv --csv-column hostname --dry-run
  printf '%s\n' host001 host002 | ./manage_falcon_grouping_tags.py --action add --tag example-tag --dry-run
"""
    parser = argparse.ArgumentParser(
        description="Add or remove CrowdStrike FalconGroupingTags for hosts.",
        epilog=help_text,
        formatter_class=HelpFormatter,
    )
    parser.add_argument("hostnames", nargs="*", help="Hostnames to resolve and tag.")
    parser.add_argument("--action", choices=("add", "remove"), default="add", help="Tag operation to perform.")
    parser.add_argument("--tag", help="FalconGroupingTag value, with or without the FalconGroupingTags/ prefix.")
    parser.add_argument(
        "--tag-type",
        choices=("falcon", "sensor"),
        default="falcon",
        help="Tag family. Only falcon is supported by this direct API workflow.",
    )
    parser.add_argument(
        "--device-id",
        action="append",
        default=[],
        help="Falcon device ID/AID to tag. May be repeated. Skips hostname lookup for that value.",
    )
    parser.add_argument("--input-file", type=Path, help="Text or CSV file containing hostnames or device IDs.")
    parser.add_argument(
        "--csv-column",
        help="CSV column containing hostnames or device IDs. Common names are auto-detected when omitted.",
    )
    parser.add_argument(
        "--input-is-device-id",
        action="store_true",
        help="Treat values from positional args, stdin, or --input-file as Falcon device IDs instead of hostnames.",
    )
    parser.add_argument("--api-md", type=Path, default=DEFAULT_API_MD, help="Path to local API.md credential file.")
    parser.add_argument("--api-profile", default=DEFAULT_API_PROFILE, help="API.md profile section to read.")
    parser.add_argument("--client-id", help="Falcon API client ID. Overrides environment variables and API.md.")
    parser.add_argument("--client-secret", help="Falcon API client secret. Overrides environment variables and API.md.")
    parser.add_argument("--base-url", help="Falcon API base URL. Defaults to CrowdStrike when omitted.")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Host IDs per tag update call.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve hosts and print planned changes without tagging.")
    parser.add_argument("--check-only", action="store_true", help="Authenticate and perform a read-only Hosts API check.")
    parser.add_argument("--include-inactive", action="store_true", help="Include non-normal host records when resolving hostnames.")
    parser.add_argument("--force", action="store_true", help="Skip the interactive confirmation prompt before changing tags.")
    return parser.parse_args()


def extract_key_values(text: str) -> dict[str, str]:
    """Extract Markdown bullet lines in the form '- Key: Value' or '* Key: Value'."""
    values: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"\s*[-*]\s*([^:]+):\s*(.+?)\s*$", line)
        if match:
            values[match.group(1).strip()] = match.group(2).strip()
    return values


def read_api_profile(api_md_path: Path, profile_name: str) -> dict[str, str]:
    """Read simple key/value entries from a named section in API.md."""
    expanded_path = api_md_path.expanduser()
    if not expanded_path.exists():
        return {}

    text = expanded_path.read_text(encoding="utf-8")
    profile_match = re.search(
        rf"^##\s+{re.escape(profile_name)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        text,
        flags=re.MULTILINE,
    )

    values: dict[str, str] = {}
    if profile_match:
        values.update(extract_key_values(profile_match.group(1)))

    # Some local profiles omit Base URL, so reuse the first Base URL in API.md.
    if "Base URL" not in values:
        all_values = extract_key_values(text)
        if "Base URL" in all_values:
            values["Base URL"] = all_values["Base URL"]

    return values


def env_first(*names: str) -> str | None:
    """Return the first non-empty environment variable from a preference list."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def build_config(args: argparse.Namespace) -> FalconConfig:
    """Resolve Falcon credentials from CLI, environment, then API.md."""
    api_values = read_api_profile(args.api_md, args.api_profile)
    client_id = args.client_id or env_first("CS_GOV_CLIENT_ID", "FALCON_CLIENT_ID") or api_values.get("Client ID")
    client_secret = (
        args.client_secret
        or env_first("CS_GOV_CLIENT_SECRET", "FALCON_CLIENT_SECRET")
        or api_values.get("Secret")
    )
    base_url = args.base_url or env_first("CS_GOV_BASE_URL", "FALCON_BASE_URL") or api_values.get("Base URL")
    base_url = base_url or DEFAULT_GOV1_BASE_URL

    missing = []
    if not client_id:
        missing.append("client ID")
    if not client_secret:
        missing.append("client secret")
    if missing:
        raise ValueError(
            "Missing "
            + " and ".join(missing)
            + ". Set CS_GOV_CLIENT_ID/CS_GOV_CLIENT_SECRET, FALCON_CLIENT_ID/FALCON_CLIENT_SECRET, "
            + "or update API.md."
        )

    return FalconConfig(client_id=client_id, client_secret=client_secret, base_url=base_url.rstrip("/"))


def normalize_falcon_tag(tag: str | None, tag_type: str) -> str:
    """Return the FalconGroupingTag value expected by the tag update API."""
    if tag_type == "sensor":
        raise ValueError(
            "SensorGroupingTags are not supported by the Hosts tag update API. "
            "Use endpoint-local tooling, configuration management, or an owner-approved RTR workflow."
        )
    if not tag:
        raise ValueError("--tag is required unless --check-only is used.")

    cleaned = tag.strip()
    for prefix in ("FalconGroupingTags/", "SensorGroupingTags/"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]

    if not cleaned:
        raise ValueError("Tag cannot be blank.")
    if "," in cleaned:
        raise ValueError("Manage one tag per run. Commas are not accepted in --tag.")
    return cleaned


def clean_value(value: str) -> str:
    """Normalize one hostname or device ID string and remove common quotes."""
    return value.strip().strip('"').strip("'")


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    """Return non-empty values once, preserving first-seen order."""
    seen: set[str] = set()
    cleaned_values: list[str] = []
    for value in values:
        cleaned = clean_value(value)
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            cleaned_values.append(cleaned)
    return cleaned_values


def split_text_values(text: str) -> list[str]:
    """Split text input on lines, commas, or whitespace."""
    return dedupe_preserve_order(re.split(r"[\s,]+", text))


def csv_has_header(path: Path) -> bool:
    """Return True when the first CSV row appears to contain column names."""
    sample = path.read_text(encoding="utf-8-sig")[:4096]
    try:
        return csv.Sniffer().has_header(sample)
    except csv.Error:
        return True


def detect_input_column(fieldnames: list[str]) -> str:
    """Choose a hostname or device ID column from a CSV header."""
    preferred_names = (
        "hostname",
        "host",
        "computername",
        "computer_name",
        "name",
        "device_id",
        "device id",
        "aid",
    )
    lower_to_actual = {name.lower().strip(): name for name in fieldnames}
    for preferred in preferred_names:
        if preferred in lower_to_actual:
            return lower_to_actual[preferred]
    raise ValueError(
        "Could not detect an input column. Use --csv-column. "
        f"Available columns: {', '.join(fieldnames)}"
    )


def read_csv_values(path: Path, csv_column: str | None) -> list[str]:
    """Read hostnames or device IDs from a CSV file."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        if csv_column or csv_has_header(path):
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            if not fieldnames:
                return []
            column = csv_column or detect_input_column(fieldnames)
            if column not in fieldnames:
                raise ValueError(f"CSV column {column!r} was not found. Available columns: {', '.join(fieldnames)}")
            return dedupe_preserve_order(row.get(column, "") for row in reader)

        reader = csv.reader(handle)
        return dedupe_preserve_order(row[0] for row in reader if row)


def read_input_values(args: argparse.Namespace) -> list[str]:
    """Collect hostnames or device IDs from CLI args, a file, stdin, or prompt."""
    sources: list[str] = []
    sources.extend(args.hostnames)

    if args.input_file:
        input_path = args.input_file.expanduser()
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        if input_path.suffix.lower() == ".csv" or args.csv_column:
            sources.extend(read_csv_values(input_path, args.csv_column))
        else:
            sources.extend(split_text_values(input_path.read_text(encoding="utf-8")))

    if not sources and not sys.stdin.isatty():
        sources.extend(split_text_values(sys.stdin.read()))

    if not sources and not args.device_id:
        print("Enter hostnames, one per line. Submit a blank line when finished.")
        while True:
            value = input("hostname> ").strip()
            if not value:
                break
            sources.append(value)

    return dedupe_preserve_order(sources)


def require_success(response: dict[str, Any], action: str) -> dict[str, Any]:
    """Raise a readable error when FalconPy returns a non-success response."""
    status_code = response.get("status_code")
    if isinstance(status_code, int) and 200 <= status_code < 300:
        return response

    body = response.get("body", {})
    errors = body.get("errors") if isinstance(body, dict) else None
    role_hint = ""
    if status_code in (401, 403):
        role_hint = " Check that the API client has Hosts read/write permissions."
    raise RuntimeError(f"{action} failed with status {status_code}: {errors or body}.{role_hint}")


def response_resources(response: dict[str, Any]) -> list[Any]:
    """Return the resources list from a FalconPy response body."""
    body = response.get("body", {})
    resources = body.get("resources", []) if isinstance(body, dict) else []
    return resources if isinstance(resources, list) else []


def fql_escape(value: str) -> str:
    """Escape a value for use inside a single-quoted Falcon Query Language string."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def chunked(values: list[str], size: int) -> Iterable[list[str]]:
    """Yield fixed-size chunks from a list."""
    if size <= 0:
        raise ValueError("Batch size must be greater than zero.")
    for index in range(0, len(values), size):
        yield values[index : index + size]


def get_device_details(falcon: Any, device_ids: list[str], batch_size: int) -> dict[str, dict[str, Any]]:
    """Fetch host details for device IDs in API-safe batches."""
    details: dict[str, dict[str, Any]] = {}
    for batch in chunked(device_ids, batch_size):
        response = require_success(falcon.get_device_details(ids=batch), "Host detail lookup")
        for host in response_resources(response):
            if isinstance(host, dict) and host.get("device_id"):
                details[str(host["device_id"])] = host
    return details


def query_host_ids(falcon: Any, hostname: str, include_inactive: bool) -> list[str]:
    """Return Falcon device IDs matching one exact hostname."""
    filter_parts = [f"hostname:'{fql_escape(hostname)}'"]
    if not include_inactive:
        filter_parts.append("status:'normal'")

    response = require_success(
        falcon.query_devices_by_filter(filter="+".join(filter_parts), limit=HOST_LOOKUP_LIMIT),
        f"Host lookup for {hostname}",
    )
    return [str(item) for item in response_resources(response)]


def match_from_detail(requested_value: str, device_id: str, detail: dict[str, Any]) -> HostMatch:
    """Build a HostMatch from one Falcon host detail object."""
    return HostMatch(
        requested_value=requested_value,
        device_id=device_id,
        hostname=str(detail.get("hostname") or requested_value),
        platform_name=str(detail.get("platform_name") or "-"),
        status=str(detail.get("status") or "-"),
        last_seen=str(detail.get("last_seen") or "-"),
        existing_tags=tuple(str(tag) for tag in detail.get("tags", []) if tag),
    )


def resolve_device_ids(falcon: Any, device_ids: list[str], batch_size: int) -> tuple[list[HostMatch], list[str]]:
    """Resolve explicit Falcon AIDs to host details."""
    details = get_device_details(falcon, device_ids, batch_size) if device_ids else {}
    matches = [match_from_detail(device_id, device_id, details[device_id]) for device_id in device_ids if device_id in details]
    missing = [device_id for device_id in device_ids if device_id not in details]
    return matches, missing


def resolve_hostnames(
    falcon: Any,
    hostnames: list[str],
    include_inactive: bool,
    batch_size: int,
) -> tuple[list[HostMatch], list[str]]:
    """Resolve hostnames to device IDs and return both matches and misses."""
    requested_by_id: dict[str, str] = {}
    missing: list[str] = []

    for hostname in hostnames:
        ids = query_host_ids(falcon, hostname, include_inactive)
        if not ids:
            missing.append(hostname)
            continue
        for device_id in ids:
            requested_by_id[device_id] = hostname

    details = get_device_details(falcon, list(requested_by_id), batch_size) if requested_by_id else {}
    matches = [
        match_from_detail(requested_hostname, device_id, details.get(device_id, {}))
        for device_id, requested_hostname in requested_by_id.items()
    ]
    return matches, missing


def display_existing_tags(tags: tuple[str, ...]) -> str:
    """Return a compact printable tag list."""
    if not tags:
        return "-"
    return ",".join(tags)[:50]


def print_resolution(matches: list[HostMatch], missing: list[str], action: str, tag: str, input_mode: str) -> None:
    """Print lookup results before a dry run or update."""
    print(f"\nTag operation: {action} FalconGroupingTags/{tag}")
    print(f"Input mode: {input_mode}")
    print(f"Resolved host records: {len(matches)}")
    print(f"Missing inputs: {len(missing)}")

    if matches:
        print("\nResolved hosts:")
        print(
            f"{'Requested':<30}  {'Falcon hostname':<30}  {'Status':<10}  "
            f"{'Platform':<12}  {'Last seen':<24}  {'Tags':<50}  Device ID"
        )
        print("-" * 205)
        for match in matches:
            print(
                f"{match.requested_value[:30]:<30}  "
                f"{match.hostname[:30]:<30}  "
                f"{match.status[:10]:<10}  "
                f"{match.platform_name[:12]:<12}  "
                f"{match.last_seen[:24]:<24}  "
                f"{display_existing_tags(match.existing_tags):<50}  "
                f"{match.device_id}"
            )

    if missing:
        print("\nNo matching Falcon host was found for:")
        for value in missing:
            print(f"  - {value}")


def confirm_update(matches: list[HostMatch], action: str, tag: str) -> bool:
    """Prompt before making a write operation."""
    response = input(
        f"\n{action.title()} FalconGroupingTags/{tag} on {len(matches)} resolved host record(s)? "
        "Type y or yes to continue: "
    )
    return response.strip().lower() in {"y", "yes"}


def update_tag(falcon: Any, device_ids: list[str], action: str, tag: str, batch_size: int) -> None:
    """Add or remove one FalconGroupingTag from device IDs in batches."""
    for index, batch in enumerate(chunked(device_ids, batch_size), start=1):
        response = require_success(
            falcon.update_device_tags(action_name=action, ids=batch, tags=[tag]),
            f"Tag {action} batch {index}",
        )
        print(f"Batch {index}: submitted {len(batch)} host record(s), status {response.get('status_code')}")


def check_hosts_api(falcon: Any) -> int:
    """Perform a read-only API check against the Hosts endpoint."""
    response = require_success(falcon.query_devices_by_filter(limit=1), "Read-only Hosts API check")
    total = response.get("body", {}).get("meta", {}).get("pagination", {}).get("total", "unknown")
    print(f"Hosts API read check succeeded. Visible host total: {total}")
    print("Write permission is not proven until update_device_tags is called against a host.")
    return 0


def main() -> int:
    """Run credential resolution, host lookup, and optional tag update."""
    args = parse_args()

    try:
        from falconpy import Hosts
    except ImportError:
        print("ERROR: falconpy is not installed. Install it with: python3 -m pip install crowdstrike-falconpy", file=sys.stderr)
        return 1

    try:
        config = build_config(args)
        tag = None if args.check_only else normalize_falcon_tag(args.tag, args.tag_type)
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 2

    falcon = Hosts(client_id=config.client_id, client_secret=config.client_secret, base_url=config.base_url)

    try:
        if args.check_only:
            return check_hosts_api(falcon)

        input_values = read_input_values(args)
        device_ids = dedupe_preserve_order(args.device_id)
        if args.input_is_device_id:
            device_ids = dedupe_preserve_order([*device_ids, *input_values])
            input_values = []

        if not input_values and not device_ids:
            print("ERROR: No hostnames or device IDs were provided.", file=sys.stderr)
            return 2

        hostname_matches, hostname_missing = resolve_hostnames(
            falcon,
            input_values,
            args.include_inactive,
            args.batch_size,
        )
        device_matches, device_missing = resolve_device_ids(falcon, device_ids, args.batch_size)
        matches = [*hostname_matches, *device_matches]
        missing = [*hostname_missing, *device_missing]
        input_mode = "device IDs" if args.input_is_device_id and not args.hostnames else "hostnames and/or device IDs"

        assert tag is not None  # For type checkers; --check-only returned above.
        print_resolution(matches, missing, args.action, tag, input_mode)

        if not matches:
            print("\nNo tag update was attempted because no hosts were resolved.")
            return 1

        if args.dry_run:
            print("\nDry run only. No tag update was attempted.")
            return 0

        if not args.force and not confirm_update(matches, args.action, tag):
            print("No changes made.")
            return 0

        update_tag(falcon, [match.device_id for match in matches], args.action, tag, args.batch_size)
        print("\nDone.")
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted. No further changes attempted.", file=sys.stderr)
        return 130
    except (FileNotFoundError, ValueError, RuntimeError) as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
