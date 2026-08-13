#!/usr/bin/env python3
"""
CrowdStrike Falcon new host reporter.

Given one or more sensor grouping tags, queries the Falcon Hosts API for devices
whose first_seen timestamp falls within the specified lookback window and writes
a Markdown report to the output directory.

Usage:
    python new-host-detection.py [options]

Environment variables (alternative to CLI flags):
    FALCON_CLIENT_ID      - API client ID
    FALCON_CLIENT_SECRET  - API client secret
    FALCON_BASE_URL       - API base URL (default: https://api.example.crowdstrike.com)
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from falconpy import Hosts
except ImportError:
    print("ERROR: falconpy is not installed. Run: pip install crowdstrike-falconpy")
    sys.exit(1)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
log = logging.getLogger(__name__)

_HOST_QUERY_LIMIT = 500
_DETAIL_BATCH_SIZE = 10


_PLATFORM_MAP = {
    "mac": "Mac",
    "windows": "Windows",
    "linux": "Linux",
}


def query_new_host_ids(hosts_svc: Hosts, tags: list[str], since: datetime, platform: str | None = None) -> list[str]:
    """Return device IDs matching the given tags whose first_seen is >= since."""
    since_str = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    all_ids: list[str] = []

    platform_clause = f"+platform_name:'{_PLATFORM_MAP[platform]}'" if platform else ""

    queries = [(tag, f"tags:'{tag}'+first_seen:>='{since_str}'{platform_clause}") for tag in tags] if tags \
        else [(None, f"first_seen:>='{since_str}'{platform_clause}")]

    for label, fql in queries:
        offset = 0
        tag_count = 0
        while True:
            resp = hosts_svc.query_devices_by_filter(
                filter=fql,
                limit=_HOST_QUERY_LIMIT,
                offset=offset,
                sort="first_seen|asc",
            )
            if resp["status_code"] != 200:
                log.warning("Host query %r returned %d: %s", fql, resp["status_code"], resp.get("body"))
                break
            resources = resp["body"].get("resources", [])
            all_ids.extend(resources)
            tag_count += len(resources)
            total = resp["body"].get("meta", {}).get("pagination", {}).get("total", 0)
            offset += len(resources)
            if offset >= total or not resources:
                break
        log.info("Tag %r: found %d new host ID(s) since %s", label or "(all)", tag_count, since_str)

    # Deduplicate while preserving order (a host may match multiple tags)
    return list(dict.fromkeys(all_ids))


def fetch_host_details(hosts_svc: Hosts, device_ids: list[str]) -> list[dict]:
    """Fetch full host detail records for a list of device IDs (batched)."""
    details: list[dict] = []
    for i in range(0, len(device_ids), _DETAIL_BATCH_SIZE):
        batch = device_ids[i : i + _DETAIL_BATCH_SIZE]
        resp = hosts_svc.get_device_details(ids=batch)
        if resp["status_code"] != 200:
            log.error("Host detail fetch failed (%d): %s", resp["status_code"], resp.get("body"))
            continue
        details.extend(resp["body"].get("resources", []))
    return details


def _val(host: dict, *keys: str, default: str = "—") -> str:
    """Safely retrieve a nested value from a host dict."""
    obj = host
    for k in keys:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(k)
        if obj is None:
            return default
    return str(obj) if obj != "" else default


def render_markdown(
    hosts: list[dict],
    tags: list[str],
    since: datetime,
    generated_at: datetime,
    platform: str | None = None,
) -> str:
    lines: list[str] = []

    lines.append("# New Host Detection Report")
    lines.append("")
    lines.append(f"**Generated:** {generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}  ")
    lines.append(f"**Lookback window:** Since {since.strftime('%Y-%m-%d %H:%M:%S UTC')}  ")
    lines.append(f"**Sensor grouping tags:** {', '.join(f'`{t}`' for t in tags) if tags else '*(all)*'}  ")
    if platform:
        lines.append(f"**Platform filter:** {_PLATFORM_MAP[platform]}  ")
    lines.append(f"**New hosts found:** {len(hosts)}")
    lines.append("")

    if not hosts:
        lines.append("No new hosts were found within the specified time window and tags.")
        return "\n".join(lines)

    lines.append("---")
    lines.append("")

    for host in hosts:
        hostname = _val(host, "hostname")
        device_id = _val(host, "device_id")
        first_seen = _val(host, "first_seen")
        last_seen = _val(host, "last_seen")
        os_version = _val(host, "os_version")
        platform = _val(host, "platform_name")
        local_ip = _val(host, "local_ip")
        external_ip = _val(host, "external_ip")
        mac = _val(host, "mac_address")
        manufacturer = _val(host, "system_manufacturer")
        model = _val(host, "system_product_name")
        agent_version = _val(host, "agent_version")
        status = _val(host, "status")
        site = _val(host, "site_name")
        domain = _val(host, "machine_domain")
        ou_list = host.get("ou") or []
        ou = " > ".join(ou_list) if ou_list else "—"
        host_tags = host.get("tags") or []
        tag_str = ", ".join(f"`{t}`" for t in host_tags) if host_tags else "—"
        groups = host.get("groups") or []
        group_str = ", ".join(f"`{g}`" for g in groups) if groups else "—"
        prevention_policy = _val(host, "device_policies", "prevention", "policy_id")
        prevention_policy_name = _val(host, "device_policies", "prevention", "applied_date")

        lines.append(f"## {hostname}")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|---|---|")
        lines.append(f"| Device ID | `{device_id}` |")
        lines.append(f"| First Seen | {first_seen} |")
        lines.append(f"| Last Seen | {last_seen} |")
        lines.append(f"| Status | {status} |")
        lines.append(f"| Platform | {platform} |")
        lines.append(f"| OS Version | {os_version} |")
        lines.append(f"| Local IP | {local_ip} |")
        lines.append(f"| External IP | {external_ip} |")
        lines.append(f"| MAC Address | {mac} |")
        lines.append(f"| Manufacturer | {manufacturer} |")
        lines.append(f"| Model | {model} |")
        lines.append(f"| Agent Version | {agent_version} |")
        lines.append(f"| Domain | {domain} |")
        lines.append(f"| Site | {site} |")
        lines.append(f"| OU | {ou} |")
        lines.append(f"| Sensor Tags | {tag_str} |")
        lines.append(f"| Groups | {group_str} |")
        lines.append("")

    return "\n".join(lines)


def write_report(content: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"new_hosts_{timestamp}.md"
    path.write_text(content, encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report new CrowdStrike Falcon hosts by sensor grouping tag within a lookback window.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--client-id",
        default=os.environ.get("FALCON_CLIENT_ID"),
        help="Falcon API client ID (or set FALCON_CLIENT_ID env var)",
    )
    parser.add_argument(
        "--client-secret",
        default=os.environ.get("FALCON_CLIENT_SECRET"),
        help="Falcon API client secret (or set FALCON_CLIENT_SECRET env var)",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("FALCON_BASE_URL", "https://api.example.crowdstrike.com"),
        help="Falcon API base URL",
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        default=[],
        metavar="TAG",
        help='Sensor grouping tags to filter by. Each tag must be enclosed in double quotes, '
             'separated by spaces (e.g. "env:production" "team:platform"). Omit to report across all hosts.',
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=24.0,
        metavar="HOURS",
        help="Lookback window in hours. Hosts first seen within this window are included.",
    )
    parser.add_argument(
        "--frequency",
        type=int,
        default=0,
        metavar="SECONDS",
        help="How often (in seconds) to run the report. Set to 0 to run once and exit.",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=None,
        metavar="N",
        help="Maximum number of report cycles to run before exiting. Unlimited by default.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./reports"),
        help="Directory where report files are written.",
    )
    parser.add_argument(
        "--platform",
        choices=["mac", "windows", "linux"],
        default=None,
        metavar="PLATFORM",
        help="Limit results to a specific platform: 'mac', 'windows', or 'linux'. Omit to include all platforms.",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity.",
    )
    return parser.parse_args()


def run_report(args: argparse.Namespace) -> None:
    hosts_svc = Hosts(
        client_id=args.client_id,
        client_secret=args.client_secret,
        base_url=args.base_url,
    )

    generated_at = datetime.now(timezone.utc)
    since = generated_at - timedelta(hours=args.hours)

    log.info("Querying new hosts since %s (%.1f hours)", since.strftime("%Y-%m-%dT%H:%M:%SZ"), args.hours)

    device_ids = query_new_host_ids(hosts_svc, args.tags, since, args.platform)
    log.info("Found %d unique new host(s) across all tags", len(device_ids))

    hosts = fetch_host_details(hosts_svc, device_ids) if device_ids else []
    log.info("Fetched details for %d host(s)", len(hosts))

    # Sort by first_seen ascending
    hosts.sort(key=lambda h: h.get("first_seen", ""))

    content = render_markdown(hosts, args.tags, since, generated_at, args.platform)
    path = write_report(content, args.output_dir)
    log.info("Report written: %s (%d new host(s))", path, len(hosts))


def main() -> None:
    args = parse_args()
    logging.getLogger().setLevel(args.log_level)

    if not args.client_id or not args.client_secret:
        log.error(
            "Falcon API credentials are required. "
            "Set --client-id/--client-secret or FALCON_CLIENT_ID/FALCON_CLIENT_SECRET."
        )
        sys.exit(1)

    run_once = args.frequency == 0
    max_runs = 1 if run_once else args.max_runs

    log.info(
        "Starting new host reporter | tags=%s | hours=%.1f | frequency=%s | output=%s",
        args.tags or "(all)",
        args.hours,
        "once" if run_once else f"{args.frequency}s",
        args.output_dir,
    )

    run_count = 0
    while True:
        try:
            run_report(args)
            run_count += 1
        except KeyboardInterrupt:
            log.info("Interrupted — exiting.")
            break
        except Exception:
            log.exception("Unexpected error during report cycle")
            run_count += 1

        if run_once or (max_runs is not None and run_count >= max_runs):
            if max_runs is not None and run_count >= max_runs:
                log.info("Reached maximum run limit (%d) — exiting.", max_runs)
            break

        log.info("Sleeping %d seconds until next run …", args.frequency)
        try:
            time.sleep(args.frequency)
        except KeyboardInterrupt:
            log.info("Interrupted during sleep — exiting.")
            break


if __name__ == "__main__":
    main()
