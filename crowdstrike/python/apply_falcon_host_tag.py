#!/usr/bin/env python3
"""
Apply a CrowdStrike Falcon host grouping tag to hosts selected by hostname.

This script uses the FalconPy Hosts service collection. The API endpoint behind
Hosts.update_device_tags manages cloud-side Falcon grouping tags. It does not
modify endpoint-local SensorGroupingTags that were set during sensor install.

Credential lookup order:
    1. Explicit CLI arguments
    2. FALCON_CLIENT_ID, FALCON_CLIENT_SECRET, FALCON_BASE_URL
    3. The configured profile section in FALCON_API_MD or API.md

Input options:
    - Positional hostnames
    - --input-file path/to/hosts.txt, one hostname per line
    - --input-file path/to/hosts.csv --csv-column hostname
    - Piped stdin
    - Interactive terminal input when no hostnames or file are provided

Examples:
    ./apply_falcon_host_tag.py --tag my_tag host001 host002 --dry-run
    ./apply_falcon_host_tag.py --tag my_tag --input-file hosts.txt
    ./apply_falcon_host_tag.py --tag my_tag --input-file hosts.csv --csv-column hostname
    printf 'host001\nhost002\n' | ./apply_falcon_host_tag.py --tag my_tag
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
DEFAULT_GOV1_BASE_URL = os.environ.get("FALCON_DEFAULT_BASE_URL", "https://api.example.crowdstrike.com")
DEFAULT_API_PROFILE = os.environ.get("FALCON_API_PROFILE", "default")
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
    """A resolved Falcon host record needed for tagging and reporting."""

    requested_hostname: str
    device_id: str
    hostname: str
    platform_name: str
    status: str
    last_seen: str
    existing_tags: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    """Parse CLI options for credential selection, input, lookup, and tagging."""
    help_text = """Simple workflow:
  1. Install dependencies: python3 -m pip install -r requirements.txt
  2. Test API read access: ./apply_falcon_host_tag.py --tag test --check-only
  3. Preview a change: ./apply_falcon_host_tag.py --tag my_tag --input-file hosts.txt --dry-run
  4. Apply the tag: ./apply_falcon_host_tag.py --tag my_tag --input-file hosts.txt

Input examples:
  ./apply_falcon_host_tag.py --tag my_tag host001 host002 --dry-run
  ./apply_falcon_host_tag.py --tag my_tag --input-file hosts.txt --dry-run
  ./apply_falcon_host_tag.py --tag my_tag --input-file hosts.csv --csv-column hostname --dry-run
  printf '%s\\n' host001 host002 | ./apply_falcon_host_tag.py --tag my_tag --dry-run
"""
    parser = argparse.ArgumentParser(
        description="Apply a Falcon host grouping tag to hosts selected by hostname.",
        epilog=help_text,
        formatter_class=HelpFormatter,
    )
    parser.add_argument("hostnames", nargs="*", help="Hostnames to tag.")
    parser.add_argument("--tag", required=True, help="Falcon grouping tag to add, for example: my_tag")
    parser.add_argument("--input-file", type=Path, help="Text or CSV file containing hostnames.")
    parser.add_argument(
        "--csv-column",
        help="CSV column containing hostnames. If omitted, common hostname column names are auto-detected.",
    )
    parser.add_argument("--api-md", type=Path, default=DEFAULT_API_MD, help="Path to local API.md credential file.")
    parser.add_argument("--api-profile", default=DEFAULT_API_PROFILE, help="API.md profile section to read.")
    parser.add_argument("--client-id", default=os.environ.get("FALCON_CLIENT_ID"), help="Falcon API client ID.")
    parser.add_argument(
        "--client-secret",
        default=os.environ.get("FALCON_CLIENT_SECRET"),
        help="Falcon API client secret.",
    )
    parser.add_argument("--base-url", default=os.environ.get("FALCON_BASE_URL"), help="Falcon API base URL.")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Host IDs per tag update call.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve hosts and print planned changes without tagging.")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Authenticate and perform a read-only Hosts API check without resolving input or tagging.",
    )
    parser.add_argument(
        "--include-inactive",
        action="store_true",
        help="Include non-normal host records when resolving hostnames.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip the interactive confirmation prompt before applying the tag.",
    )
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

    # Several local scripts keep the base URL outside the selected profile, so
    # reuse the first Base URL in the file if the profile does not include one.
    if "Base URL" not in values:
        all_values = extract_key_values(text)
        if "Base URL" in all_values:
            values["Base URL"] = all_values["Base URL"]

    return values


def build_config(args: argparse.Namespace) -> FalconConfig:
    """Resolve Falcon credentials from CLI/env first, then the API.md profile."""
    api_values = read_api_profile(args.api_md, args.api_profile)
    client_id = args.client_id or api_values.get("Client ID")
    client_secret = args.client_secret or api_values.get("Secret")
    base_url = args.base_url or api_values.get("Base URL") or DEFAULT_GOV1_BASE_URL

    missing = []
    if not client_id:
        missing.append("client ID")
    if not client_secret:
        missing.append("client secret")
    if missing:
        raise ValueError(
            "Missing "
            + " and ".join(missing)
            + ". Set FALCON_CLIENT_ID/FALCON_CLIENT_SECRET or update API.md."
        )

    return FalconConfig(client_id=client_id, client_secret=client_secret, base_url=base_url)


def normalize_tag(tag: str) -> str:
    """Return the tag value expected by Hosts.update_device_tags.

    FalconPy examples pass only the tag name. If a copied tag includes a known
    grouping prefix, strip the prefix before sending it to the update endpoint.
    """
    cleaned = tag.strip()
    for prefix in ("FalconGroupingTags/", "SensorGroupingTags/"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]

    if not cleaned:
        raise ValueError("Tag cannot be blank.")
    return cleaned


def clean_hostname(value: str) -> str:
    """Normalize one hostname string and remove common quoting artifacts."""
    return value.strip().strip('"').strip("'")


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    """Return non-empty values once, preserving the first-seen order."""
    seen: set[str] = set()
    cleaned_values: list[str] = []
    for value in values:
        cleaned = clean_hostname(value)
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            cleaned_values.append(cleaned)
    return cleaned_values


def split_text_hostnames(text: str) -> list[str]:
    """Split text input on lines, commas, or whitespace."""
    return dedupe_preserve_order(re.split(r"[\s,]+", text))


def csv_has_header(path: Path) -> bool:
    """Return True when the first CSV row appears to contain column names."""
    sample = path.read_text(encoding="utf-8-sig")[:4096]
    try:
        return csv.Sniffer().has_header(sample)
    except csv.Error:
        return True


def detect_hostname_column(fieldnames: list[str]) -> str:
    """Choose the hostname column from a CSV header."""
    preferred_names = ("hostname", "host", "computername", "computer_name", "name")
    lower_to_actual = {name.lower().strip(): name for name in fieldnames}
    for preferred in preferred_names:
        if preferred in lower_to_actual:
            return lower_to_actual[preferred]
    raise ValueError(
        "Could not detect a hostname column. Use --csv-column. "
        f"Available columns: {', '.join(fieldnames)}"
    )


def read_csv_hostnames(path: Path, csv_column: str | None) -> list[str]:
    """Read hostnames from a CSV file, using a named column or the first column."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        if csv_column or csv_has_header(path):
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            if not fieldnames:
                return []
            column = csv_column or detect_hostname_column(fieldnames)
            if column not in fieldnames:
                raise ValueError(f"CSV column {column!r} was not found. Available columns: {', '.join(fieldnames)}")
            return dedupe_preserve_order(row.get(column, "") for row in reader)

        reader = csv.reader(handle)
        return dedupe_preserve_order(row[0] for row in reader if row)


def read_hostnames(args: argparse.Namespace) -> list[str]:
    """Collect hostnames from CLI args, a file, stdin, or an interactive prompt."""
    sources: list[str] = []

    if args.hostnames:
        sources.extend(args.hostnames)

    if args.input_file:
        input_path = args.input_file.expanduser()
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        if input_path.suffix.lower() == ".csv" or args.csv_column:
            sources.extend(read_csv_hostnames(input_path, args.csv_column))
        else:
            sources.extend(split_text_hostnames(input_path.read_text(encoding="utf-8")))

    if not sources and not sys.stdin.isatty():
        sources.extend(split_text_hostnames(sys.stdin.read()))

    if not sources:
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
        role_hint = " The configured API profile likely needs Hosts read/write permissions for this endpoint."
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


def get_device_details(falcon: Any, device_ids: list[str]) -> dict[str, dict[str, Any]]:
    """Fetch host details for device IDs in API-safe batches."""
    details: dict[str, dict[str, Any]] = {}
    for batch in chunked(device_ids, DEFAULT_BATCH_SIZE):
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


def resolve_hostnames(falcon: Any, hostnames: list[str], include_inactive: bool) -> tuple[list[HostMatch], list[str]]:
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

    details = get_device_details(falcon, list(requested_by_id)) if requested_by_id else {}
    matches: list[HostMatch] = []
    for device_id, requested_hostname in requested_by_id.items():
        detail = details.get(device_id, {})
        matches.append(
            HostMatch(
                requested_hostname=requested_hostname,
                device_id=device_id,
                hostname=str(detail.get("hostname") or requested_hostname),
                platform_name=str(detail.get("platform_name") or "-"),
                status=str(detail.get("status") or "-"),
                last_seen=str(detail.get("last_seen") or "-"),
                existing_tags=tuple(str(tag) for tag in detail.get("tags", []) if tag),
            )
        )

    return matches, missing


def print_resolution(matches: list[HostMatch], missing: list[str], tag: str) -> None:
    """Print the lookup results before a dry run or update."""
    print(f"\nTag to add: {tag}")
    print(f"Resolved host records: {len(matches)}")
    print(f"Missing hostnames: {len(missing)}")

    if matches:
        print("\nResolved hosts:")
        print(f"{'Requested':<30}  {'Falcon hostname':<30}  {'Status':<10}  {'Platform':<12}  {'Last seen':<24}  Device ID")
        print("-" * 140)
        for match in matches:
            print(
                f"{match.requested_hostname[:30]:<30}  "
                f"{match.hostname[:30]:<30}  "
                f"{match.status[:10]:<10}  "
                f"{match.platform_name[:12]:<12}  "
                f"{match.last_seen[:24]:<24}  "
                f"{match.device_id}"
            )

    if missing:
        print("\nNo matching Falcon host was found for:")
        for hostname in missing:
            print(f"  - {hostname}")


def confirm_update(matches: list[HostMatch], tag: str) -> bool:
    """Prompt before making a write operation."""
    response = input(f"\nApply tag {tag!r} to {len(matches)} resolved host record(s)? Type y or yes to continue: ")
    return response.strip().lower() in {"y", "yes"}


def apply_tag(falcon: Any, device_ids: list[str], tag: str, batch_size: int) -> None:
    """Apply one Falcon grouping tag to device IDs in batches."""
    for index, batch in enumerate(chunked(device_ids, batch_size), start=1):
        response = require_success(
            falcon.update_device_tags(action_name="add", ids=batch, tags=[tag]),
            f"Tag update batch {index}",
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
        print(
            "ERROR: falconpy is not installed. Install it with: "
            "python3 -m pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    try:
        config = build_config(args)
        tag = normalize_tag(args.tag)
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 2

    falcon = Hosts(
        client_id=config.client_id,
        client_secret=config.client_secret,
        base_url=config.base_url,
    )

    try:
        if args.check_only:
            return check_hosts_api(falcon)

        hostnames = read_hostnames(args)
        if not hostnames:
            print("ERROR: No hostnames were provided.", file=sys.stderr)
            return 2

        matches, missing = resolve_hostnames(falcon, hostnames, args.include_inactive)
        print_resolution(matches, missing, tag)

        if not matches:
            print("\nNo tag update was attempted because no hosts were resolved.")
            return 1

        if args.dry_run:
            print("\nDry run only. No tag update was attempted.")
            return 0

        if not args.force and not confirm_update(matches, tag):
            print("No changes made.")
            return 0

        apply_tag(falcon, [match.device_id for match in matches], tag, args.batch_size)
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
