#!/usr/bin/env python3
"""
List recent blocked USB Device Control events and create selected exceptions.

The script uses two Falcon API areas:
    - NGSIEM searches for recent Device Control block events. Starting a
      search creates a query job, so the API client needs NGSIEM read and
      write access for the activity lookup.
    - FalconPy DeviceControlPolicies updates the selected policy's USB class exceptions.

Environment variables:
    FALCON_CLIENT_ID       Falcon API client ID
    FALCON_CLIENT_SECRET   Falcon API client secret
    FALCON_BASE_URL        Falcon API base URL
    FALCON_NGSIEM_REPO     NGSIEM repository or view name

Default API.md path:
    FALCON_API_MD or API.md

Typical workflow:
    1. Run the script to list the most recent blocked USB devices.
    2. Select one menu number to unblock, or 0 to exit without changes.
    3. Review the exception JSON and type yes to apply it.

Example:
    ./allow_recent_usb_blocks.py --hours 24 --policy-name "Example USB Policy"
    ./allow_recent_usb_blocks.py --hours 24 --limit 25 --policy-name "Example USB Policy"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote as url_quote, urlencode
from urllib.request import Request, urlopen


DEFAULT_API_MD = Path(os.environ.get("FALCON_API_MD", "API.md"))
DEFAULT_GOV1_BASE_URL = os.environ.get("FALCON_DEFAULT_BASE_URL", "https://api.example.crowdstrike.com")
DEFAULT_REPOSITORY = "search-all"
DEFAULT_USB_CLASS = "MASS_STORAGE"
API_PROFILE_NAME = os.environ.get("FALCON_API_PROFILE", "default")
QUERY_LIMIT = 5000


@dataclass(frozen=True)
class BlockedUsbDevice:
    """Normalized event data needed to show and allow a blocked USB device."""

    index: int
    timestamp: str
    hostname: str
    username: str
    policy: str
    usb_class: str
    vendor_id: str
    product_id: str
    serial_number: str
    combined_id: str
    vendor_name: str
    product_name: str
    raw_event: dict[str, Any]


def parse_args() -> argparse.Namespace:
    """Parse CLI options used to query blocks and update exceptions."""
    parser = argparse.ArgumentParser(
        description="List recent blocked USB Device Control events and allow selected devices.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--api-md", type=Path, default=DEFAULT_API_MD)
    parser.add_argument("--client-id", default=os.environ.get("FALCON_CLIENT_ID"))
    parser.add_argument("--client-secret", default=os.environ.get("FALCON_CLIENT_SECRET"))
    parser.add_argument("--base-url", default=os.environ.get("FALCON_BASE_URL"))
    parser.add_argument("--repository", default=os.environ.get("FALCON_NGSIEM_REPO", DEFAULT_REPOSITORY))
    parser.add_argument("--hours", type=int, default=24, help="How far back to search for blocked USB events.")
    parser.add_argument("--hostname", help="Optional exact hostname filter.")
    parser.add_argument("--policy-id", help="Device Control policy ID to update.")
    parser.add_argument("--policy-name", help="Device Control policy name to update.")
    parser.add_argument(
        "--usb-class",
        default=DEFAULT_USB_CLASS,
        help="USB class to query and use for new exceptions. Use ALL to skip the class filter.",
    )
    parser.add_argument("--description", help="Required description to place on the created exception. Prompts when omitted.")
    parser.add_argument("--expiration", help="Optional UTC expiration timestamp for created exceptions.")
    parser.add_argument("--limit", type=int, default=10, help="Number of recent blocked devices to list.")
    parser.add_argument("--selection", type=int, help="Single menu number to unblock. Use 0 for no change.")
    parser.add_argument("--list", action="store_true", help="List recent blocked devices and exit without updating a policy.")
    parser.add_argument("--output-payload", type=Path, help="Write the generated update payload to this JSON file.")
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--max-results", type=int, default=2000)
    parser.add_argument("--poll-seconds", type=int, default=3)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--print-query", action="store_true", help="Print the generated NGSIEM query.")
    return parser.parse_args()


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


def quote(value: str) -> str:
    """Return a safely quoted LogScale string literal."""
    return '"' + value.replace('"', '\\"') + '"'


def any_clause(clauses: list[str]) -> str:
    """Join query clauses with OR and wrap them."""
    return "(" + " OR ".join(clauses) + ")"


def usb_class_clause(usb_class: str) -> str:
    """Build a LogScale clause for the requested USB device class."""
    normalized = re.sub(r"\s+", "_", usb_class.strip().upper())
    if not normalized or normalized == "ALL":
        return ""

    if normalized == "MASS_STORAGE":
        return any_clause([
            "class=/MASS[_ ]?STORAGE/i",
            "Class=/MASS[_ ]?STORAGE/i",
            "DeviceClass=/MASS[_ ]?STORAGE/i",
            "DevicePolicyClass=/MASS[_ ]?STORAGE/i",
            "DevicePropertyClassName=/MASS[_ ]?STORAGE/i",
            "DevicePropertyDeviceDescription=/MASS[_ ]?STORAGE/i",
            "DevicePropertyManufacturer=/storage/i",
            "DcPolicyDeviceUsbClass=8",
            "DeviceUsbClass=8",
            "DeviceInstanceId=/USBSTOR/i",
        ])

    pattern = re.escape(normalized).replace("_", "[_ ]?")
    return any_clause([
        f"class=/{pattern}/i",
        f"Class=/{pattern}/i",
        f"DeviceClass=/{pattern}/i",
        f"DevicePolicyClass=/{pattern}/i",
        f"DevicePropertyClassName=/{pattern}/i",
    ])


def build_block_query(hostname: str | None, usb_class: str) -> str:
    """Build a broad LogScale query for blocked USB Device Control events."""
    clauses = [
        any_clause([
            "#event_simpleName=/^Dc.*Usb.*(Block|Deny|Prevent).*$/i",
            "event_simpleName=/^Dc.*Usb.*(Block|Deny|Prevent).*$/i",
            "DeviceInstanceId=/USB\\\\/i",
            "DeviceInstanceId=/USB/i",
            "ConnectionType=/USB/i",
            "DevicePropertyClassName=/USB/i",
        ]),
        any_clause([
            "AccessGranted=false",
            "action=/BLOCK/i",
            "Action=/Block/i",
            "PolicyType=/Block/i",
            "#event_simpleName=/Blocked/i",
            "event_simpleName=/Blocked/i",
        ]),
    ]

    class_clause = usb_class_clause(usb_class)
    if class_clause:
        clauses.append(class_clause)

    if hostname:
        clauses.append(any_clause([
            f"ComputerName={quote(hostname)}",
            f"HostName={quote(hostname)}",
            f"hostname={quote(hostname)}",
            f"aid_computer_name={quote(hostname)}",
        ]))

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


def response_body(response: dict[str, Any]) -> dict[str, Any]:
    """Return the most likely response payload dictionary."""
    body = response.get("body")
    if isinstance(body, dict):
        return body
    resources = response.get("resources")
    if isinstance(resources, dict):
        return resources
    return {}


def response_resources(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Return resources from a FalconPy response body."""
    body = response.get("body", {})
    resources = body.get("resources", []) if isinstance(body, dict) else []
    return resources if isinstance(resources, list) else []


def pagination_total(response: dict[str, Any]) -> int | None:
    """Return Falcon pagination total when present."""
    body = response.get("body", {})
    meta = body.get("meta", {}) if isinstance(body, dict) else {}
    pagination = meta.get("pagination", {}) if isinstance(meta, dict) else {}
    total = pagination.get("total")
    return total if isinstance(total, int) else None


def nested_find_id(value: Any) -> str | None:
    """Find an NGSIEM search job ID in several possible response shapes."""
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


def is_search_done(body: dict[str, Any]) -> bool:
    """Return True when a query job status body indicates completion."""
    if body.get("done") is True:
        return True
    status = str(body.get("status") or body.get("state") or "").lower()
    return status in {"done", "complete", "completed", "finished", "success"}


def extract_events(body: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract event dictionaries from common NGSIEM result shapes."""
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
    """Start an NGSIEM search, poll it, and retrieve event pages."""
    repository_path = url_quote(repository, safe="")
    search_body = {
        "queryString": query,
        "start": start,
        "isLive": False,
    }
    if end:
        search_body["end"] = end
    start_response = ngsiem_request(
        "POST",
        base_url,
        token,
        f"/humio/api/v1/repositories/{repository_path}/queryjobs",
        "NGSIEM search start",
        body=search_body,
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


def value_from(event: dict[str, Any], candidates: tuple[str, ...]) -> str:
    """Return the first non-empty event field from a list of candidate names."""
    for key in candidates:
        value = event.get(key)
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return ""


def normalize_usb_id(value: str) -> str:
    """Normalize a USB vendor/product ID to CrowdStrike's decimal string form.

    Falcon policy exports in this repository store USB vendor and product IDs as
    decimal strings. Event data may contain decimal values, hexadecimal values,
    or strings like VID_0781 / PID_5567. This helper preserves decimal values and
    converts clear hexadecimal values to decimal.
    """
    cleaned = value.strip()
    if not cleaned:
        return ""

    vid_pid_match = re.search(r"(?:VID|PID)[_:-]?([0-9A-Fa-f]{4})", cleaned, flags=re.IGNORECASE)
    if vid_pid_match:
        return str(int(vid_pid_match.group(1), 16))

    hex_match = re.fullmatch(r"0x([0-9A-Fa-f]+)", cleaned)
    if hex_match:
        return str(int(hex_match.group(1), 16))

    if re.fullmatch(r"[0-9]+", cleaned):
        return cleaned

    if re.fullmatch(r"[0-9A-Fa-f]{4}", cleaned) and re.search(r"[A-Fa-f]", cleaned):
        return str(int(cleaned, 16))

    return cleaned


def parse_usb_ids_from_text(text: str) -> tuple[str, str, str]:
    """Extract vendor ID, product ID, and serial from USB-ish text fields."""
    vendor_id = ""
    product_id = ""
    serial_number = ""

    vid_match = re.search(r"VID[_:-]?([0-9A-Fa-f]{4})", text, flags=re.IGNORECASE)
    pid_match = re.search(r"PID[_:-]?([0-9A-Fa-f]{4})", text, flags=re.IGNORECASE)
    if vid_match:
        # VID/PID values embedded in USB instance paths are hexadecimal, even
        # when the four characters happen to be all digits, such as VID_0781.
        vendor_id = str(int(vid_match.group(1), 16))
    if pid_match:
        product_id = str(int(pid_match.group(1), 16))

    # Windows device instance paths often end with the serial after the final backslash.
    if "\\" in text:
        serial_number = text.rsplit("\\", 1)[-1].strip()

    return vendor_id, product_id, serial_number


def normalize_combined_id(value: str) -> str:
    """Normalize a combined_id when it appears to contain hex VID/PID values."""
    cleaned = value.strip()
    match = re.fullmatch(r"([0-9A-Fa-f]{4})_([0-9A-Fa-f]{4})_(.*)", cleaned)
    if not match:
        return cleaned

    vendor_text, product_text, serial_number = match.groups()
    if re.search(r"[A-Fa-f]", vendor_text + product_text) or vendor_text.startswith("0"):
        return f"{int(vendor_text, 16)}_{int(product_text, 16)}_{serial_number}"
    return cleaned


def parse_combined_id_from_text(text: str) -> str:
    """Extract a CrowdStrike Combined ID / CID value from descriptive text."""
    match = re.search(
        r"\b(?:Combined\s+ID|CID)\s*:\s*([^\)\]\}\r\n]+)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return ""
    return normalize_combined_id(match.group(1).strip())


def split_combined_id(combined_id: str) -> tuple[str, str, str]:
    """Split a combined_id into vendor ID, product ID, and serial components."""
    parts = combined_id.split("_", 2)
    if len(parts) != 3:
        return "", "", ""
    return parts[0].strip(), parts[1].strip(), parts[2].strip()


def combined_id_from_parts(vendor_id: str, product_id: str, serial_number: str) -> str:
    """Build CrowdStrike's combined_id string from exception components."""
    if not vendor_id or not product_id:
        return ""
    return f"{vendor_id}_{product_id}_{serial_number}"


def normalize_event(event: dict[str, Any], index: int, fallback_class: str) -> BlockedUsbDevice | None:
    """Convert one raw event into a candidate USB exception record."""
    device_text = value_from(event, ("DeviceInstanceId", "device_instance_id", "DeviceId", "device_id"))
    parsed_vendor, parsed_product, parsed_serial = parse_usb_ids_from_text(device_text)
    device_details = value_from(event, ("DeviceDetails", "device_details", "DeviceDetail", "device_detail"))

    vendor_id = normalize_usb_id(value_from(event, (
        "VendorId",
        "vendor_id",
        "DeviceVendorId",
        "USBVendorId",
        "VendorID",
    ))) or parsed_vendor
    product_id = normalize_usb_id(value_from(event, (
        "ProductId",
        "product_id",
        "DeviceProductId",
        "USBProductId",
        "ProductID",
    ))) or parsed_product
    serial_number = value_from(event, (
        "SerialNumber",
        "serial_number",
        "DeviceSerialNumber",
        "USBSerialNumber",
    )) or parsed_serial
    combined_id = value_from(event, ("combined_id", "CombinedId", "CombinedID")) or parse_combined_id_from_text(device_details)
    if combined_id:
        combined_id = normalize_combined_id(combined_id)
        combined_vendor, combined_product, combined_serial = split_combined_id(combined_id)
        vendor_id = vendor_id or combined_vendor
        product_id = product_id or combined_product
        serial_number = serial_number or combined_serial
    else:
        combined_id = combined_id_from_parts(vendor_id, product_id, serial_number)

    # Do not offer a menu item if it cannot produce a precise exception.
    if not combined_id or not vendor_id or not product_id:
        return None

    usb_class = value_from(event, ("class", "Class", "DeviceClass", "DevicePolicyClass", "DevicePropertyClassName"))
    if not usb_class or usb_class.upper() == "USB":
        usb_class = fallback_class

    return BlockedUsbDevice(
        index=index,
        timestamp=value_from(event, ("@timestamp", "timestamp", "Time", "event_time", "EventTime")),
        hostname=value_from(event, ("ComputerName", "HostName", "hostname", "aid_computer_name", "ComputerName.raw")),
        username=value_from(event, ("UserName", "username", "UserPrincipal", "UserSid", "UID")),
        policy=value_from(event, (
            "DcPolicyName",
            "DevicePolicyName",
            "PolicyName",
            "policy_name",
            "DcPolicyGroupId",
            "DevicePolicyGroupId",
            "PolicyGroupId",
            "policy_group_id",
            "DcPolicyId",
            "DevicePolicyId",
            "PolicyId",
            "policy_id",
        )),
        usb_class=usb_class.upper(),
        vendor_id=vendor_id,
        product_id=product_id,
        serial_number=serial_number,
        combined_id=combined_id,
        vendor_name=value_from(event, ("VendorName", "vendor_name", "DeviceVendor", "DeviceVendorName")),
        product_name=value_from(event, ("ProductName", "product_name", "DeviceProduct", "DeviceProductName")),
        raw_event=event,
    )


def event_timestamp(event: dict[str, Any]) -> datetime:
    """Return an event timestamp for sorting, or datetime.min when absent."""
    timestamp = value_from(event, ("@timestamp", "timestamp", "Time", "event_time", "EventTime"))
    if not timestamp:
        return datetime.min.replace(tzinfo=timezone.utc)

    normalized = timestamp.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def unique_devices(events: list[dict[str, Any]], fallback_class: str) -> list[BlockedUsbDevice]:
    """Return de-duplicated, normalized USB devices newest event first."""
    devices: list[BlockedUsbDevice] = []
    seen: set[tuple[str, str]] = set()
    for event in sorted(events, key=event_timestamp, reverse=True):
        candidate = normalize_event(event, len(devices) + 1, fallback_class)
        if not candidate:
            continue
        key = (candidate.usb_class, candidate.combined_id)
        if key in seen:
            continue
        seen.add(key)
        devices.append(candidate)
    return devices


def print_device_menu(devices: list[BlockedUsbDevice]) -> None:
    """Print a compact numbered menu of blocked USB devices."""
    print("\nRecent blocked USB devices:\n")
    print("  0  No change")
    print()
    print(f"{'#':>3}  {'Time':<24}  {'Host':<24}  {'Policy':<36}  {'Class':<24}  {'Combined ID':<34}  Product")
    print("-" * 166)
    for device in devices:
        product = device.product_name or "-"
        policy = device.policy or "-"
        print(
            f"{device.index:>3}  "
            f"{device.timestamp[:24]:<24}  "
            f"{device.hostname[:24]:<24}  "
            f"{policy[:36]:<36}  "
            f"{device.usb_class[:24]:<24}  "
            f"{device.combined_id[:34]:<34}  "
            f"{product[:28]}"
        )


def parse_selection(selection: int, maximum: int) -> int | None:
    """Validate one menu selection. Return None when 0 means no change."""
    if selection == 0:
        return None
    if 1 <= selection <= maximum:
        return selection
    raise ValueError(f"Selection must be 0 or a number between 1 and {maximum}")


def prompt_for_selection(maximum: int) -> int | None:
    """Prompt until the user selects one menu item or exits with 0."""
    while True:
        response = input("\nSelect one device to unblock, or 0 for no change: ").strip()
        if not response.isdigit():
            print("ERROR: Enter 0 or one menu number.")
            continue
        try:
            return parse_selection(int(response), maximum)
        except ValueError as err:
            print(f"ERROR: {err}")


def prompt_for_description(description: str | None) -> str:
    """Return a non-empty exception description, prompting when needed."""
    if description and description.strip():
        return description.strip()

    while True:
        response = input("\nEnter the exception description: ").strip()
        if response:
            return response
        print("ERROR: Description is required.")


def query_all_policies(falcon: Any, fql_filter: str | None = None) -> list[dict[str, Any]]:
    """Query all matching USB Device Control policies with pagination."""
    policies: list[dict[str, Any]] = []
    offset = 0
    while True:
        kwargs: dict[str, Any] = {"limit": QUERY_LIMIT, "offset": offset}
        if fql_filter:
            kwargs["filter"] = fql_filter
        response = require_success(falcon.query_combined_policies(**kwargs), "Device Control policy query")
        resources = response_resources(response)
        policies.extend(resources)

        total = pagination_total(response)
        offset += len(resources)
        if not resources or total is None or offset >= total:
            break
    return policies


def query_all_policies_direct(base_url: str, token: str) -> list[dict[str, Any]]:
    """Query all Device Control policies directly for read-only lookups."""
    policies: list[dict[str, Any]] = []
    offset = 0
    while True:
        body = ngsiem_request(
            "GET",
            base_url,
            token,
            "/policy/combined/device-control/v1",
            "Device Control policy query",
            params={"limit": QUERY_LIMIT, "offset": offset},
        )
        resources = body.get("resources", [])
        if not isinstance(resources, list):
            break
        policies.extend([policy for policy in resources if isinstance(policy, dict)])

        meta = body.get("meta", {}) if isinstance(body, dict) else {}
        pagination = meta.get("pagination", {}) if isinstance(meta, dict) else {}
        total = pagination.get("total")
        offset += len(resources)
        if not resources or not isinstance(total, int) or offset >= total:
            break

    return policies


def build_policy_name_map(base_url: str, token: str) -> dict[str, str]:
    """Return a map of policy IDs to policy names, or an empty map on failure."""
    try:
        policies = query_all_policies_direct(base_url, token)
    except RuntimeError:
        return {}

    names: dict[str, str] = {}
    for policy in policies:
        current_id = policy_id(policy)
        current_name = str(policy.get("name") or "").strip()
        if current_id and current_name:
            names[current_id] = current_name
            names[normalize_policy_lookup_id(current_id)] = current_name
    return names


def normalize_policy_lookup_id(value: str) -> str:
    """Normalize policy IDs so dashed event UUIDs match Falcon API IDs."""
    return value.replace("-", "").lower()


def apply_policy_names(devices: list[BlockedUsbDevice], policy_names: dict[str, str]) -> list[BlockedUsbDevice]:
    """Replace policy IDs with policy names where a mapping is available."""
    if not policy_names:
        return devices
    return [
        replace(device, policy=policy_names.get(device.policy, policy_names.get(normalize_policy_lookup_id(device.policy), device.policy)))
        for device in devices
    ]


def policy_id(policy: dict[str, Any]) -> str:
    """Return the policy identifier field used by the API response."""
    for key in ("id", "policy_id"):
        value = policy.get(key)
        if value:
            return str(value)
    return ""


def get_policy_details(falcon: Any, selected_id: str) -> dict[str, Any]:
    """Fetch full details for one policy, preferring the v2 endpoint."""
    try:
        response = require_success(
            falcon.get_policies_v2(ids=[selected_id]),
            "Device Control policy detail lookup via get_policies_v2",
        )
    except RuntimeError:
        response = require_success(
            falcon.get_policies(ids=[selected_id]),
            "Device Control policy detail lookup via get_policies",
        )
    resources = response_resources(response)
    if not resources:
        raise RuntimeError(f"No policy details returned for policy ID {selected_id}")
    return resources[0]


def resolve_policy(falcon: Any, policy_id_value: str | None, policy_name: str | None) -> dict[str, Any]:
    """Resolve the policy to update by ID, name, or interactive menu."""
    if policy_id_value:
        return get_policy_details(falcon, policy_id_value)

    policies = query_all_policies(falcon)
    if policy_name:
        matches = [policy for policy in policies if str(policy.get("name", "")).lower() == policy_name.lower()]
        if len(matches) == 1:
            return get_policy_details(falcon, policy_id(matches[0]))
        if not matches:
            raise RuntimeError(f"No Device Control policy found named {policy_name!r}")
        raise RuntimeError(f"Multiple Device Control policies found named {policy_name!r}; use --policy-id")

    if not policies:
        raise RuntimeError("No Device Control policies were returned by the API")

    print("\nDevice Control policies:\n")
    print(f"{'#':>3}  {'Name':<48}  {'Platform':<10}  {'Enabled':<7}  ID")
    print("-" * 100)
    for index, policy in enumerate(policies, start=1):
        print(
            f"{index:>3}  "
            f"{str(policy.get('name', '-'))[:48]:<48}  "
            f"{str(policy.get('platform_name', '-'))[:10]:<10}  "
            f"{str(policy.get('enabled', '-'))[:7]:<7}  "
            f"{policy_id(policy)}"
        )

    while True:
        response = input("\nSelect the policy to update, or q to quit: ").strip()
        if response.lower() in {"q", "quit", "exit"}:
            raise KeyboardInterrupt
        if response.isdigit() and 1 <= int(response) <= len(policies):
            return get_policy_details(falcon, policy_id(policies[int(response) - 1]))
        print(f"Enter a number between 1 and {len(policies)}.")


def existing_exception_ids(policy: dict[str, Any]) -> set[tuple[str, str]]:
    """Return existing (class, combined_id) pairs from a policy."""
    existing: set[tuple[str, str]] = set()
    classes = policy.get("usb_settings", {}).get("classes", [])
    if not isinstance(classes, list):
        return existing
    for class_entry in classes:
        if not isinstance(class_entry, dict):
            continue
        usb_class = str(class_entry.get("class") or "").upper()
        exceptions = class_entry.get("exceptions", [])
        if not isinstance(exceptions, list):
            continue
        for exception in exceptions:
            if not isinstance(exception, dict):
                continue
            combined_id = str(exception.get("combined_id") or "")
            if usb_class and combined_id:
                existing.add((usb_class, combined_id))
    return existing


def exception_from_device(device: BlockedUsbDevice, description: str, expiration: str | None) -> dict[str, Any]:
    """Build one CrowdStrike USB exception record from a normalized event."""
    exception: dict[str, Any] = {
        "action": "FULL_ACCESS",
        "class": device.usb_class,
        "combined_id": device.combined_id,
        "vendor_id": device.vendor_id,
        "product_id": device.product_id,
    }
    if device.serial_number:
        exception["serial_number"] = device.serial_number
    if device.vendor_name:
        exception["vendor_name"] = device.vendor_name
    if device.product_name:
        exception["product_name"] = device.product_name
    if description:
        exception["description"] = description
    if expiration:
        exception["expiration_time"] = expiration
    return exception


def build_update_payload(policy: dict[str, Any], exceptions: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the Device Control class update payload."""
    return {
        "policies": [
            {
                "id": policy_id(policy),
                "usb_classes": {
                    "upsert_exceptions": exceptions,
                },
            }
        ]
    }


def print_exception_preview(exceptions: list[dict[str, Any]]) -> None:
    """Print the exception JSON that will be sent to CrowdStrike."""
    print("\nException to create:\n")
    print(json.dumps(exceptions[0], indent=2, sort_keys=True))


def confirm_apply(policy: dict[str, Any]) -> bool:
    """Require an explicit final yes before applying the exception."""
    policy_name = str(policy.get("name") or policy_id(policy))
    response = input(f"\nCreate this exception in policy {policy_name!r}? Type yes to continue: ").strip()
    return response.lower() == "yes"


def main() -> int:
    """Run the recent-block lookup and optional exception update."""
    args = parse_args()

    if args.limit < 1:
        print("ERROR: --limit must be 1 or greater.", file=sys.stderr)
        return 2

    try:
        client_id, client_secret, base_url = build_config(args)
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 2

    start_text = f"{args.hours}h"
    end_text = ""
    query = build_block_query(args.hostname, args.usb_class)

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
            start=start_text,
            end=end_text,
            page_size=args.page_size,
            max_results=args.max_results,
            poll_seconds=args.poll_seconds,
            timeout_seconds=args.timeout_seconds,
        )
        devices = unique_devices(events, args.usb_class)[: args.limit]
        policy_names = build_policy_name_map(base_url, token)
        devices = apply_policy_names(devices, policy_names)
    except (RuntimeError, TimeoutError) as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    if not devices:
        print("No recent blocked USB devices with enough identifier data were found.")
        return 0

    print_device_menu(devices)

    if args.list:
        class_text = re.sub(r"\s+", "_", args.usb_class.strip().upper()) or DEFAULT_USB_CLASS
        print(f"\nListed recent blocked USB devices for class {class_text}. No policy update requested.")
        return 0

    try:
        selected_index = parse_selection(args.selection, len(devices)) if args.selection is not None else prompt_for_selection(len(devices))
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 2

    if selected_index is None:
        print("No device selected. Exiting.")
        return 0

    try:
        from falconpy import DeviceControlPolicies
    except ImportError:
        print(
            "ERROR: falconpy is required for policy updates. Run: python3 -m pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    policies = DeviceControlPolicies(client_id=client_id, client_secret=client_secret, base_url=base_url)

    try:
        policy = resolve_policy(policies, args.policy_id, args.policy_name)
    except KeyboardInterrupt:
        print("\nNo policy selected. Exiting.")
        return 130
    except RuntimeError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    selected_device = devices[selected_index - 1]
    already_present = existing_exception_ids(policy)

    if (selected_device.usb_class, selected_device.combined_id) in already_present:
        print("\nNo new exception needed. This device is already present in the selected policy.")
        return 0

    description = prompt_for_description(args.description)
    exceptions = [exception_from_device(selected_device, description, args.expiration)]

    payload = build_update_payload(policy, exceptions)
    print_exception_preview(exceptions)

    if args.output_payload:
        args.output_payload.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"\nWrote update payload to: {args.output_payload}")

    if not confirm_apply(policy):
        print("No changes made.")
        return 0

    try:
        response = require_success(
            policies.update_policy_classes(body=payload),
            "Device Control USB exception update",
        )
    except RuntimeError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(f"\nCreated 1 exception in policy {policy.get('name') or policy_id(policy)}.")
    if args.output_payload:
        print(f"Update response status: {response.get('status_code')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
