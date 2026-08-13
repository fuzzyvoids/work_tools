#!/usr/bin/env python3
"""
Query CrowdStrike Falcon Device Control activity by date range.

This script uses the Falcon NGSIEM search API, which is the practical API
surface for historical activity/events. It prompts for a start time, end time,
and optional filters, then writes the matching events to a JSON file in the
current working directory.

Environment variables:
    FALCON_CLIENT_ID       Falcon API client ID
    FALCON_CLIENT_SECRET   Falcon API client secret
    FALCON_BASE_URL        Falcon API base URL
    LOCAL_TIMEZONE         IANA timezone for local timestamp display. Defaults to UTC.
    FALCON_NGSIEM_REPO     NGSIEM repository or view name

Default API.md path:
    FALCON_API_MD or API.md

Notes:
    - The end time accepts "now".
    - The API client must have NGSIEM read and write access. Starting a
      search creates a query job, so NGSIEM read-only access is not enough.
    - Date-only values are expanded to the full local day.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, time as dt_time, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote as url_quote, urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


DEFAULT_API_MD = Path(os.environ.get("FALCON_API_MD", "API.md"))
DEFAULT_GOV1_BASE_URL = os.environ.get("FALCON_DEFAULT_BASE_URL", "https://api.example.crowdstrike.com")
DEFAULT_REPOSITORY = "search-all"
API_PROFILE_NAME = os.environ.get("FALCON_API_PROFILE", "default")
LOCAL_TIMEZONE = ZoneInfo(os.environ.get("LOCAL_TIMEZONE", "UTC"))


def parse_args() -> argparse.Namespace:
    """Parse optional CLI values. Missing values are prompted interactively."""
    parser = argparse.ArgumentParser(
        description="Query CrowdStrike Device Control activity from NGSIEM.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--api-md", type=Path, default=DEFAULT_API_MD)
    parser.add_argument("--client-id", default=os.environ.get("FALCON_CLIENT_ID"))
    parser.add_argument("--client-secret", default=os.environ.get("FALCON_CLIENT_SECRET"))
    parser.add_argument("--base-url", default=os.environ.get("FALCON_BASE_URL"))
    parser.add_argument("--repository", default=os.environ.get("FALCON_NGSIEM_REPO", DEFAULT_REPOSITORY))
    parser.add_argument("--start", help="Start time. Examples: 2026-08-01, 2026-08-01T08:00:00Z")
    parser.add_argument("--end", help='End time. Use "now" for current time.')
    parser.add_argument("--hostname", help="Optional exact hostname filter.")
    parser.add_argument("--connection-type", help="Optional comma-separated values: USB, PCIe, Bluetooth")
    parser.add_argument("--platform", help="Optional comma-separated values: Windows, macOS, Linux")
    parser.add_argument("--permission", help="Optional comma-separated values: Full Access, Blocked, Read Only, No Execute")
    parser.add_argument("--output", type=Path, help="Output JSON file. Defaults to activity_<timestamp>.json")
    parser.add_argument("--page-size", type=int, default=1000, help="Result page size for NGSIEM polling.")
    parser.add_argument("--max-results", type=int, default=10000, help="Maximum events to collect before stopping.")
    parser.add_argument("--poll-seconds", type=int, default=3, help="Seconds between search status checks.")
    parser.add_argument("--timeout-seconds", type=int, default=300, help="Maximum seconds to wait for the search.")
    parser.add_argument("--print-query", action="store_true", help="Print the generated NGSIEM query before running it.")
    return parser.parse_args()


def prompt_if_missing(value: str | None, prompt: str, default: str | None = None) -> str:
    """Return a provided value or prompt the user for one."""
    if value:
        return value.strip()
    suffix = f" [{default}]" if default else ""
    response = input(f"{prompt}{suffix}: ").strip()
    return response or (default or "")


def read_api_profile(api_md_path: Path, profile_name: str) -> dict[str, str]:
    """Read simple key/value entries from the named API.md section."""
    if not api_md_path.exists():
        return {}

    text = api_md_path.read_text(encoding="utf-8")
    profile_match = re.search(
        rf"^##\s+{re.escape(profile_name)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        text,
        flags=re.MULTILINE,
    )

    values: dict[str, str] = {}
    if profile_match:
        values.update(extract_key_values(profile_match.group(1)))

    if "Base URL" not in values:
        all_values = extract_key_values(text)
        if "Base URL" in all_values:
            values["Base URL"] = all_values["Base URL"]

    return values


def extract_key_values(text: str) -> dict[str, str]:
    """Extract Markdown bullet lines in the form '- Key: Value'."""
    values: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"\s*[-*]\s*([^:]+):\s*(.+?)\s*$", line)
        if match:
            values[match.group(1).strip()] = match.group(2).strip()
    return values


def build_config(args: argparse.Namespace) -> tuple[str, str, str]:
    """Resolve Falcon credentials from CLI/env first, then API.md."""
    api_values = read_api_profile(args.api_md.expanduser(), API_PROFILE_NAME)
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
    return client_id, client_secret, base_url


def parse_time(value: str, *, end_of_day: bool = False) -> str:
    """Convert a user-supplied time to a LogScale epoch-millisecond timestamp.

    Supported examples:
        now
        2026-08-03
        2026-08-03 13:30
        2026-08-03T13:30:00Z
    """
    cleaned = value.strip()
    if cleaned.lower() == "now":
        return str(int(datetime.now(timezone.utc).timestamp() * 1000))

    date_only = re.fullmatch(r"\d{4}-\d{2}-\d{2}", cleaned) is not None
    if date_only:
        parsed_date = datetime.strptime(cleaned, "%Y-%m-%d").date()
        local_time = dt_time.max if end_of_day else dt_time.min
        parsed = datetime.combine(parsed_date, local_time, tzinfo=LOCAL_TIMEZONE)
    else:
        normalized = cleaned.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as err:
            raise ValueError(f"Invalid date/time value: {value}") from err
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=LOCAL_TIMEZONE)

    return str(int(parsed.astimezone(timezone.utc).timestamp() * 1000))


def split_csv(value: str | None) -> list[str]:
    """Split comma-separated prompt/CLI values and drop blanks."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def quote(value: str) -> str:
    """Return a safely quoted LogScale string literal."""
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def any_clause(clauses: list[str]) -> str:
    """Join clauses with OR and wrap them for use in a larger query."""
    return "(" + " OR ".join(clauses) + ")"


def build_query(hostname: str, connection_types: list[str], platforms: list[str], permissions: list[str]) -> str:
    """Build a LogScale query for Device Control activity.

    The base query is intentionally broad because Device Control field names can
    differ between event types and connector versions. Optional filters add more
    targeted clauses without discarding fields from the returned events.
    """
    clauses = [
        any_clause([
            "#event_simpleName=/^Dc.*(Usb|Pcie|Pci|Bluetooth|Device).*$/i",
            "event_simpleName=/^Dc.*(Usb|Pcie|Pci|Bluetooth|Device).*$/i",
            "DevicePolicy=*",
            "DcPolicyId=*",
            "DeviceInstanceId=*",
        ])
    ]

    if hostname:
        clauses.append(any_clause([
            f"ComputerName={quote(hostname)}",
            f"HostName={quote(hostname)}",
            f"hostname={quote(hostname)}",
            f"aid_computer_name={quote(hostname)}",
        ]))

    if connection_types:
        connection_clauses = []
        for item in connection_types:
            normalized = item.strip().lower()
            if normalized in {"usb", "u"}:
                connection_clauses.extend([
                    "#event_simpleName=/Usb/i",
                    "event_simpleName=/Usb/i",
                    "DevicePropertyClassName=/USB/i",
                    "DeviceInstanceId=/USB/i",
                    "ConnectionType=/USB/i",
                ])
            elif normalized in {"pcie", "pci", "pci-e"}:
                connection_clauses.extend([
                    "#event_simpleName=/(Pcie|Pci)/i",
                    "event_simpleName=/(Pcie|Pci)/i",
                    "DevicePropertyClassName=/(Pcie|Pci)/i",
                    "ConnectionType=/(Pcie|Pci)/i",
                ])
            elif normalized in {"bluetooth", "bt"}:
                connection_clauses.extend([
                    "#event_simpleName=/Bluetooth/i",
                    "event_simpleName=/Bluetooth/i",
                    "DevicePropertyClassName=/Bluetooth/i",
                    "ConnectionType=/Bluetooth/i",
                ])
            else:
                connection_clauses.extend([
                    f"ConnectionType={quote(item)}",
                    f"DevicePropertyClassName={quote(item)}",
                ])
        clauses.append(any_clause(connection_clauses))

    if platforms:
        platform_aliases = {
            "windows": ["Win", "Windows"],
            "win": ["Win", "Windows"],
            "macos": ["Mac", "macOS", "Darwin"],
            "mac": ["Mac", "macOS", "Darwin"],
            "linux": ["Lin", "Linux"],
        }
        platform_clauses = []
        for item in platforms:
            aliases = platform_aliases.get(item.strip().lower(), [item])
            for alias in aliases:
                platform_clauses.extend([
                    f"event_platform={quote(alias)}",
                    f"platform={quote(alias)}",
                    f"PlatformName={quote(alias)}",
                ])
        clauses.append(any_clause(platform_clauses))

    if permissions:
        permission_clauses = []
        for item in permissions:
            normalized = item.strip().lower().replace("_", " ").replace("-", " ")
            if normalized in {"blocked", "block", "block all"}:
                permission_clauses.extend([
                    "AccessGranted=false",
                    "#event_simpleName=/Blocked/i",
                    "event_simpleName=/Blocked/i",
                    "PolicyType=/Block/i",
                    "action=/BLOCK/i",
                ])
            elif normalized in {"full access", "full", "allowed", "allow"}:
                permission_clauses.extend([
                    "AccessGranted=true",
                    "PolicyType=/Full Access/i",
                    "action=/FULL_ACCESS/i",
                    "Action=/Full Access/i",
                ])
            elif normalized in {"read only", "readonly"}:
                permission_clauses.extend([
                    "PolicyType=/Read Only/i",
                    "action=/READ_ONLY/i",
                    "Action=/Read Only/i",
                ])
            elif normalized in {"no execute", "noexec", "no execution"}:
                permission_clauses.extend([
                    "PolicyType=/No Execute/i",
                    "action=/NO_EXECUTE/i",
                    "Action=/No Execute/i",
                ])
            else:
                permission_clauses.extend([
                    f"PolicyType={quote(item)}",
                    f"action={quote(item)}",
                    f"Action={quote(item)}",
                ])
        clauses.append(any_clause(permission_clauses))

    return " AND\n".join(clauses)


def require_success(response: dict[str, Any], action: str) -> dict[str, Any]:
    """Raise a readable error for non-2xx FalconPy responses."""
    status_code = response.get("status_code")
    if isinstance(status_code, int) and 200 <= status_code < 300:
        return response
    body = response.get("body", response.get("resources", {}))
    errors = body.get("errors") if isinstance(body, dict) else None
    hint = authorization_hint(status_code, action)
    raise RuntimeError(f"{action} failed with status {status_code}: {errors or body}{hint}")


def authorization_hint(status_code: int | None, action: str) -> str:
    """Return an actionable permission hint for common CrowdStrike 403s."""
    if status_code != 403 or "NGSIEM search" not in action:
        return ""
    if action == "NGSIEM search start":
        return " Check that the API client has NGSIEM write access; starting a search creates a query job."
    return " Check that the API client has NGSIEM read access for search job status/results."


def falcon_url(base_url: str, path: str) -> str:
    """Join the Falcon base URL and an API path without duplicate slashes."""
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def decode_json_response(raw_body: bytes) -> dict[str, Any]:
    """Decode a JSON response body, preserving text when JSON is not returned."""
    if not raw_body:
        return {}
    text = raw_body.decode("utf-8", errors="replace")
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}
    return decoded if isinstance(decoded, dict) else {"resources": decoded}


def http_json_request(request: Request, action: str, timeout: int) -> dict[str, Any]:
    """Send a urllib request and convert HTTP failures to RuntimeError."""
    try:
        with urlopen(request, timeout=timeout) as response:
            return decode_json_response(response.read())
    except HTTPError as err:
        body = decode_json_response(err.read())
        errors = body.get("errors") if isinstance(body, dict) else body
        hint = authorization_hint(err.code, action)
        raise RuntimeError(f"{action} failed with status {err.code}: {errors or body}{hint}") from err
    except URLError as err:
        raise RuntimeError(f"{action} failed: {err.reason}") from err


def falcon_token(client_id: str, client_secret: str, base_url: str) -> str:
    """Request an OAuth2 token for direct NGSIEM API calls."""
    request = Request(
        falcon_url(base_url, "/oauth2/token"),
        data=urlencode({
            "client_id": client_id,
            "client_secret": client_secret,
        }).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        method="POST",
    )
    body = http_json_request(request, "Falcon OAuth token request", 30)

    token = body.get("access_token") if isinstance(body, dict) else None
    if not token:
        raise RuntimeError(f"Falcon OAuth token response did not include access_token: {body}")
    return str(token)


def ngsiem_request(
    method: str,
    base_url: str,
    token: str,
    path: str,
    action: str,
    *,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Send one direct NGSIEM API request and return its JSON body."""
    url = falcon_url(base_url, path)
    if params:
        url = f"{url}?{urlencode(params)}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method=method,
    )
    return http_json_request(request, action, 60)


def nested_find_id(value: Any) -> str | None:
    """Find a search job identifier in a FalconPy response with varied shapes."""
    if isinstance(value, dict):
        for key in ("id", "search_id", "job_id"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate:
                return candidate
        for nested in value.values():
            found = nested_find_id(nested)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = nested_find_id(item)
            if found:
                return found
    return None


def response_body(response: dict[str, Any]) -> dict[str, Any]:
    """Return the most likely response payload dictionary."""
    body = response.get("body")
    if isinstance(body, dict):
        return body
    resources = response.get("resources")
    if isinstance(resources, dict):
        return resources
    return {}


def is_search_done(body: dict[str, Any]) -> bool:
    """Return True when a query job status body indicates completion."""
    if body.get("done") is True:
        return True
    status = str(body.get("status") or body.get("state") or "").lower()
    return status in {"done", "complete", "completed", "finished", "success"}


def extract_events(body: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract events from common NGSIEM query job response shapes."""
    events = body.get("events")
    if isinstance(events, list):
        return [event for event in events if isinstance(event, dict)]

    results = body.get("results")
    if isinstance(results, list):
        return [event for event in results if isinstance(event, dict)]
    if isinstance(results, dict) and isinstance(results.get("events"), list):
        return [event for event in results["events"] if isinstance(event, dict)]

    return []


def run_search(
    base_url: str,
    token: str,
    repository: str,
    query: str,
    start: str,
    end: str,
    page_size: int,
    max_results: int,
    poll_seconds: int,
    timeout_seconds: int,
) -> list[dict[str, Any]]:
    """Start an NGSIEM search, poll it, and retrieve result pages."""
    repository_path = url_quote(repository, safe="")
    start_response = ngsiem_request(
        "POST",
        base_url,
        token,
        f"/humio/api/v1/repositories/{repository_path}/queryjobs",
        "NGSIEM search start",
        body={
            "queryString": query,
            "start": start,
            "end": end,
            "isLive": False,
        },
    )
    search_id = nested_find_id(start_response)
    if not search_id:
        raise RuntimeError(f"NGSIEM search start did not return a search ID: {start_response}")

    deadline = time.monotonic() + timeout_seconds
    while True:
        body = ngsiem_request(
            "GET",
            base_url,
            token,
            f"/humio/api/v1/repositories/{repository_path}/queryjobs/{url_quote(search_id, safe='')}",
            "NGSIEM search status",
            params={"paginationLimit": 1, "paginationOffset": 0},
        )
        if is_search_done(body):
            break
        if body.get("cancelled") is True:
            raise RuntimeError(f"NGSIEM search was cancelled: {body}")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out waiting for NGSIEM search {search_id}")
        time.sleep(poll_seconds)

    events: list[dict[str, Any]] = []
    offset = 0
    while len(events) < max_results:
        remaining = max_results - len(events)
        limit = min(page_size, remaining)
        body = ngsiem_request(
            "GET",
            base_url,
            token,
            f"/humio/api/v1/repositories/{repository_path}/queryjobs/{url_quote(search_id, safe='')}",
            "NGSIEM search result page",
            params={"paginationLimit": limit, "paginationOffset": offset},
        )
        page_events = extract_events(body)
        if not page_events:
            break
        events.extend(page_events)
        if len(page_events) < limit:
            break
        offset += len(page_events)

    return events


def default_output_path(start: str, end: str) -> Path:
    """Build a timestamped output path for the current working directory."""
    safe_start = re.sub(r"[^0-9A-Za-z]+", "", start.replace("Z", "UTC"))
    safe_end = re.sub(r"[^0-9A-Za-z]+", "", end.replace("Z", "UTC"))
    return Path.cwd() / f"device_control_activity_{safe_start}_to_{safe_end}.json"


def main() -> int:
    """Collect inputs, run the search, and write event JSON output."""
    args = parse_args()

    try:
        client_id, client_secret, base_url = build_config(args)
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 2

    start_input = prompt_if_missing(args.start, "Start date/time")
    end_input = prompt_if_missing(args.end, 'End date/time, or "now"', "now")
    hostname = prompt_if_missing(args.hostname, "Hostname filter, blank for none")
    connection_type = prompt_if_missing(args.connection_type, "Connection type filter, blank for none")
    platform = prompt_if_missing(args.platform, "Platform filter, blank for none")
    permission = prompt_if_missing(args.permission, "Permission filter, blank for none")

    try:
        start = parse_time(start_input, end_of_day=False)
        end = parse_time(end_input, end_of_day=True)
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 2

    query = build_query(
        hostname=hostname,
        connection_types=split_csv(connection_type),
        platforms=split_csv(platform),
        permissions=split_csv(permission),
    )

    if args.print_query:
        print("\nGenerated NGSIEM query:\n")
        print(query)
        print()

    try:
        token = falcon_token(client_id, client_secret, base_url)
        events = run_search(
            base_url=base_url,
            token=token,
            repository=args.repository,
            query=query,
            start=start,
            end=end,
            page_size=args.page_size,
            max_results=args.max_results,
            poll_seconds=args.poll_seconds,
            timeout_seconds=args.timeout_seconds,
        )
    except (RuntimeError, TimeoutError) as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    output_path = args.output or default_output_path(start, end)
    output = {
        "query_metadata": {
            "repository": args.repository,
            "start": start,
            "end": end,
            "hostname": hostname,
            "connection_type": connection_type,
            "platform": platform,
            "permission": permission,
            "max_results": args.max_results,
            "query": query,
        },
        "event_count": len(events),
        "events": events,
    }
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {len(events)} event(s) to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
