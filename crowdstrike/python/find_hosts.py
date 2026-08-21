#!/usr/bin/env python3
"""
List CrowdStrike hosts that have one or more grouping tags.

The script performs read-only host searches against the Falcon Hosts API. It can
query either FalconGroupingTags or SensorGroupingTags, depending on the tag value
or --tag-type option supplied at runtime.

Credential lookup order:
    1. Explicit CLI arguments
    2. CS_GOV_CLIENT_ID, CS_GOV_CLIENT_SECRET, CS_GOV_BASE_URL
    3. FALCON_CLIENT_ID, FALCON_CLIENT_SECRET, FALCON_BASE_URL
    4. The RobF_Host_Management section in ~/devel/work_repo/crowdstrike/API.md
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_API_MD = Path.home() / "devel/work_repo/crowdstrike/API.md"
DEFAULT_API_PROFILE = "RobF_Host_Management"
DEFAULT_BASE_URL = "https://api.laggar.gcw.crowdstrike.com"
DEFAULT_OUTPUT_FILE = Path("hosts.json")
DEFAULT_QUERY_LIMIT = 500
DEFAULT_DETAIL_BATCH_SIZE = 100


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Show default values while preserving example formatting in --help."""


@dataclass(frozen=True)
class FalconConfig:
    """Resolved Falcon API connection settings."""

    client_id: str
    client_secret: str
    base_url: str


def parse_args() -> argparse.Namespace:
    """Parse command-line options for tag search, output, and credentials."""
    examples = """Examples:
  ./find_hosts.py --tag FalconGroupingTags/Janteq
  ./find_hosts.py --tag Janteq --tag-type falcon --output janteq-hosts.json
  ./find_hosts.py --tag Enterprise-Workstations --tag-type sensor --output enterprise-workstations.csv --format csv
  ./find_hosts.py --tag-file tags.txt --include-inactive
  ./find_hosts.py --tag SensorGroupingTags/LAA-Isci-10293-BOI --diagnose
"""
    parser = argparse.ArgumentParser(
        description="List CrowdStrike hosts that have one or more grouping tags.",
        epilog=examples,
        formatter_class=HelpFormatter,
    )
    parser.add_argument("--tag", action="append", default=[], help="Grouping tag to query. May be repeated.")
    parser.add_argument("--tag-file", type=Path, help="Text or CSV file containing one tag per line or row.")
    parser.add_argument("--csv-column", help="CSV column containing tags when --tag-file is a CSV file.")
    parser.add_argument(
        "--tag-type",
        choices=("falcon", "sensor"),
        default="falcon",
        help="Prefix to apply when a tag is supplied without FalconGroupingTags/ or SensorGroupingTags/.",
    )
    parser.add_argument(
        "--include-inactive",
        action="store_true",
        help="Include hosts whose Falcon status is not normal.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "csv"),
        default="json",
        help="Output format for host results.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_FILE, help="Output file path.")
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Run read-only diagnostic checks before the main tag query.",
    )
    parser.add_argument("--api-md", type=Path, default=DEFAULT_API_MD, help="Path to local API.md credential file.")
    parser.add_argument("--api-profile", default=DEFAULT_API_PROFILE, help="API.md profile section to read.")
    parser.add_argument("--client-id", help="Falcon API client ID. Overrides environment variables and API.md.")
    parser.add_argument("--client-secret", help="Falcon API client secret. Overrides environment variables and API.md.")
    parser.add_argument("--base-url", help="Falcon API base URL. Defaults to CrowdStrike GOV-1 when omitted.")
    parser.add_argument("--query-limit", type=int, default=DEFAULT_QUERY_LIMIT, help="Device IDs per host search page.")
    parser.add_argument("--detail-batch-size", type=int, default=DEFAULT_DETAIL_BATCH_SIZE, help="Device IDs per detail lookup.")
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

    # Some local profiles keep Base URL in a shared section. Reuse the first
    # visible Base URL if the selected profile does not include one.
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
    base_url = base_url or DEFAULT_BASE_URL

    missing = []
    if not client_id:
        missing.append("client ID")
    if not client_secret:
        missing.append("client secret")
    if missing:
        raise ValueError(
            "Missing "
            + " and ".join(missing)
            + ". Set CS_GOV_CLIENT_ID/CS_GOV_CLIENT_SECRET, "
            + "FALCON_CLIENT_ID/FALCON_CLIENT_SECRET, or update API.md."
        )

    return FalconConfig(client_id=client_id, client_secret=client_secret, base_url=base_url.rstrip("/"))


def clean_value(value: str) -> str:
    """Normalize one CLI, text, or CSV value and remove common quotes."""
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


def csv_has_header(path: Path) -> bool:
    """Return True when the first CSV row appears to contain column names."""
    sample = path.read_text(encoding="utf-8-sig")[:4096]
    try:
        return csv.Sniffer().has_header(sample)
    except csv.Error:
        return True


def detect_tag_column(fieldnames: list[str]) -> str:
    """Choose a tag column from a CSV header."""
    preferred_names = ("tag", "tags", "grouping_tag", "grouping tag", "sensor_tag", "falcon_tag")
    lower_to_actual = {name.lower().strip(): name for name in fieldnames}
    for preferred in preferred_names:
        if preferred in lower_to_actual:
            return lower_to_actual[preferred]
    raise ValueError(
        "Could not detect a tag column. Use --csv-column. "
        f"Available columns: {', '.join(fieldnames)}"
    )


def read_csv_tags(path: Path, csv_column: str | None) -> list[str]:
    """Read tag values from a CSV file."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        if csv_column or csv_has_header(path):
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            if not fieldnames:
                return []
            column = csv_column or detect_tag_column(fieldnames)
            if column not in fieldnames:
                raise ValueError(f"CSV column {column!r} was not found. Available columns: {', '.join(fieldnames)}")
            return dedupe_preserve_order(row.get(column, "") for row in reader)

        reader = csv.reader(handle)
        return dedupe_preserve_order(row[0] for row in reader if row)


def read_tag_file(path: Path, csv_column: str | None) -> list[str]:
    """Read grouping tags from a text or CSV file."""
    expanded_path = path.expanduser()
    if not expanded_path.exists():
        raise FileNotFoundError(f"Tag file not found: {expanded_path}")
    if expanded_path.suffix.lower() == ".csv" or csv_column:
        return read_csv_tags(expanded_path, csv_column)
    return dedupe_preserve_order(expanded_path.read_text(encoding="utf-8").splitlines())


def normalize_tag(tag: str, tag_type: str) -> str:
    """Return the exact Falcon host tags[] value to use in the FQL query."""
    cleaned = clean_value(tag)
    if cleaned.startswith(("FalconGroupingTags/", "SensorGroupingTags/")):
        return cleaned

    prefix = "FalconGroupingTags" if tag_type == "falcon" else "SensorGroupingTags"
    return f"{prefix}/{cleaned}"


def collect_tags(args: argparse.Namespace) -> list[str]:
    """Collect and normalize all tag values from CLI arguments and optional file input."""
    tag_values: list[str] = []
    tag_values.extend(args.tag)
    if args.tag_file:
        tag_values.extend(read_tag_file(args.tag_file, args.csv_column))
    tags = [normalize_tag(tag, args.tag_type) for tag in dedupe_preserve_order(tag_values)]
    if not tags:
        raise ValueError("At least one --tag or --tag-file value is required.")
    return tags


def require_success(response: dict[str, Any], action: str) -> dict[str, Any]:
    """Raise a readable error when FalconPy returns a non-success response."""
    status_code = response.get("status_code")
    if isinstance(status_code, int) and 200 <= status_code < 300:
        return response

    body = response.get("body", {})
    errors = body.get("errors") if isinstance(body, dict) else None
    role_hint = ""
    if status_code in (401, 403):
        role_hint = " Check that the API client has Hosts read permissions."
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


def get_hosts_for_tag(hosts_api: Any, tag: str, include_inactive: bool, limit: int) -> list[str]:
    """Return all Falcon device IDs matching one grouping tag."""
    if limit <= 0:
        raise ValueError("Query limit must be greater than zero.")

    device_ids: list[str] = []
    offset = 0
    filter_parts = [f"tags:'{fql_escape(tag)}'"]
    if not include_inactive:
        filter_parts.append("status:'normal'")
    filter_expr = "+".join(filter_parts)

    while True:
        response = require_success(
            hosts_api.query_devices_by_filter(filter=filter_expr, limit=limit, offset=offset),
            f"Host lookup for tag {tag}",
        )
        resources = [str(device_id) for device_id in response_resources(response)]
        device_ids.extend(resources)

        pagination = response.get("body", {}).get("meta", {}).get("pagination", {})
        total = int(pagination.get("total", len(device_ids)))
        offset += len(resources)
        if offset >= total or not resources:
            break

    return device_ids


def get_host_details(hosts_api: Any, device_ids: list[str], batch_size: int) -> list[dict[str, Any]]:
    """Fetch full device details for device IDs in API-safe batches."""
    details: list[dict[str, Any]] = []
    for batch in chunked(device_ids, batch_size):
        response = require_success(hosts_api.get_device_details(ids=batch), "Host detail lookup")
        details.extend(host for host in response_resources(response) if isinstance(host, dict))
    return details


def diagnose(hosts_api: Any, tags: list[str]) -> None:
    """Run read-only checks to help validate connectivity and tag formatting."""
    print("=" * 60)
    print("DIAGNOSTIC MODE")
    print("=" * 60)

    print("\n[1] Unfiltered query (limit=2):")
    response = require_success(hosts_api.query_devices_by_filter(limit=2), "Diagnostic host sample")
    sample_ids = [str(device_id) for device_id in response_resources(response)]
    total = response.get("body", {}).get("meta", {}).get("pagination", {}).get("total", "?")
    print(f"    total hosts visible: {total}")
    print(f"    sample ids: {sample_ids}")

    if sample_ids:
        print(f"\n[2] Tags on sample host {sample_ids[0]}:")
        details = get_host_details(hosts_api, [sample_ids[0]], DEFAULT_DETAIL_BATCH_SIZE)
        tags_on_sample = details[0].get("tags", []) if details else []
        print(json.dumps(tags_on_sample, indent=6))

    print("\n[3] Target tag filters:")
    for tag in tags:
        response = require_success(
            hosts_api.query_devices_by_filter(filter=f"tags:'{fql_escape(tag)}'", limit=5),
            f"Diagnostic tag lookup for {tag}",
        )
        returned = len(response_resources(response))
        total = response.get("body", {}).get("meta", {}).get("pagination", {}).get("total", "?")
        print(f"    {tag}: total={total} returned={returned}")

    print("\n" + "=" * 60)
    print("END DIAGNOSTICS")
    print("=" * 60 + "\n")


def build_output(host_details: list[dict[str, Any]], tag_by_device_id: dict[str, list[str]]) -> list[dict[str, Any]]:
    """Build the compact output record used by this tool and add_site.py."""
    output: list[dict[str, Any]] = []
    for host in sorted(host_details, key=lambda item: str(item.get("hostname", "")).lower()):
        device_id = str(host.get("device_id", ""))
        output.append(
            {
                "device_id": device_id,
                "hostname": host.get("hostname", ""),
                "platform_name": host.get("platform_name", ""),
                "status": host.get("status", ""),
                "last_seen": host.get("last_seen", ""),
                "matched_tags": tag_by_device_id.get(device_id, []),
                "tags": host.get("tags", []),
            }
        )
    return output


def write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write host results as pretty JSON."""
    with path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write host results as CSV with list fields joined by semicolons."""
    fieldnames = ("device_id", "hostname", "platform_name", "status", "last_seen", "matched_tags", "tags")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            csv_row["matched_tags"] = ";".join(row.get("matched_tags", []))
            csv_row["tags"] = ";".join(row.get("tags", []))
            writer.writerow(csv_row)


def main() -> int:
    """Run the tag search and write host results."""
    args = parse_args()

    try:
        from falconpy import Hosts
    except ImportError:
        print("ERROR: falconpy is not installed. Install it with: python3 -m pip install crowdstrike-falconpy", file=sys.stderr)
        return 1

    try:
        config = build_config(args)
        tags = collect_tags(args)
    except (FileNotFoundError, ValueError) as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 2

    hosts_api = Hosts(client_id=config.client_id, client_secret=config.client_secret, base_url=config.base_url)

    try:
        if args.diagnose:
            diagnose(hosts_api, tags)

        all_device_ids: set[str] = set()
        tag_by_device_id: dict[str, list[str]] = {}
        for tag in tags:
            print(f"Querying hosts with tag: {tag}")
            ids = get_hosts_for_tag(hosts_api, tag, args.include_inactive, args.query_limit)
            print(f"  Found {len(ids)} host(s)")
            all_device_ids.update(ids)
            for device_id in ids:
                tag_by_device_id.setdefault(device_id, []).append(tag)

        print(f"\nTotal unique hosts: {len(all_device_ids)}")
        host_details = get_host_details(hosts_api, sorted(all_device_ids), args.detail_batch_size) if all_device_ids else []
        output = build_output(host_details, tag_by_device_id)

        output_path = args.output.expanduser()
        if args.format == "json":
            write_json(output_path, output)
        else:
            write_csv(output_path, output)

        print(f"Wrote {len(output)} host(s) to {output_path}")
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted. No further queries attempted.", file=sys.stderr)
        return 130
    except (RuntimeError, ValueError) as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
