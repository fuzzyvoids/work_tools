#!/usr/bin/env python3
"""
Query CrowdStrike Falcon USB Device Control policies and print details
for the policy selected by the user.

The script prefers environment variables so credentials do not have to be stored
in the source file. If those variables are not set, it reads the local API.md
file and extracts the default profile section.

Environment variables:
    FALCON_CLIENT_ID       Falcon API client ID
    FALCON_CLIENT_SECRET   Falcon API client secret
    FALCON_BASE_URL        Falcon API base URL

Default API.md path:
    FALCON_API_MD or API.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_API_MD = Path(os.environ.get("FALCON_API_MD", "API.md"))
DEFAULT_GOV1_BASE_URL = os.environ.get("FALCON_DEFAULT_BASE_URL", "https://api.example.crowdstrike.com")
API_PROFILE_NAME = os.environ.get("FALCON_API_PROFILE", "default")
QUERY_LIMIT = 5000


def parse_args() -> argparse.Namespace:
    """Parse command-line options used to override default behavior."""
    parser = argparse.ArgumentParser(
        description="List Falcon USB Device Control policies and print one policy's details.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--api-md",
        type=Path,
        default=DEFAULT_API_MD,
        help="Path to the API.md file containing the default profile profile.",
    )
    parser.add_argument(
        "--client-id",
        default=os.environ.get("FALCON_CLIENT_ID"),
        help="Falcon API client ID. Overrides API.md when provided.",
    )
    parser.add_argument(
        "--client-secret",
        default=os.environ.get("FALCON_CLIENT_SECRET"),
        help="Falcon API client secret. Overrides API.md when provided.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("FALCON_BASE_URL"),
        help="Falcon API base URL. Defaults to when not found in API.md.",
    )
    parser.add_argument(
        "--filter",
        default=None,
        help="Optional Falcon Query Language filter for policy lookup.",
    )
    parser.add_argument(
        "--sort",
        default=None,
        help="Optional Falcon Query Language sort expression for policy lookup.",
    )
    parser.add_argument(
        "--cid",
        default=None,
        help="Find USB exceptions matching this Combined ID and optionally remove one after confirmation.",
    )
    return parser.parse_args()


def read_api_profile(api_md_path: Path, profile_name: str) -> dict[str, str]:
    """Return credential values from the named API.md profile section.

    API.md is Markdown rather than a structured config file, so this parser only
    extracts simple "key: value" lines inside the requested section. If the
    section omits Base URL, the first Base URL in the file is used as a fallback.
    """
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

    # The current default profile section does not list Base URL. is
    # documented elsewhere in the same file, so reuse that value if present.
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


def require_success(response: dict[str, Any], action: str) -> dict[str, Any]:
    """Raise a readable error when FalconPy returns a non-success response."""
    status_code = response.get("status_code")
    if isinstance(status_code, int) and 200 <= status_code < 300:
        return response

    body = response.get("body", {})
    errors = body.get("errors") if isinstance(body, dict) else None
    raise RuntimeError(f"{action} failed with status {status_code}: {errors or body}")


def response_resources(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the resources list from a FalconPy response body."""
    body = response.get("body", {})
    resources = body.get("resources", []) if isinstance(body, dict) else []
    return resources if isinstance(resources, list) else []


def pagination_total(response: dict[str, Any]) -> int | None:
    """Return Falcon API pagination total when the response includes it."""
    body = response.get("body", {})
    meta = body.get("meta", {}) if isinstance(body, dict) else {}
    pagination = meta.get("pagination", {}) if isinstance(meta, dict) else {}
    total = pagination.get("total")
    return total if isinstance(total, int) else None


def query_all_policies(
    falcon: Any,
    fql_filter: str | None,
    sort: str | None,
) -> list[dict[str, Any]]:
    """Query all matching USB Device Control policies with pagination."""
    policies: list[dict[str, Any]] = []
    offset = 0

    while True:
        kwargs: dict[str, Any] = {
            "limit": QUERY_LIMIT,
            "offset": offset,
        }
        if fql_filter:
            kwargs["filter"] = fql_filter
        if sort:
            kwargs["sort"] = sort

        response = require_success(
            falcon.query_combined_policies(**kwargs),
            "Device Control policy query",
        )
        resources = response_resources(response)
        policies.extend(resources)

        total = pagination_total(response)
        offset += len(resources)
        if not resources or total is None or offset >= total:
            break

    return policies


def policy_id(policy: dict[str, Any]) -> str:
    """Return the policy identifier field used by the API response."""
    for key in ("id", "policy_id"):
        value = policy.get(key)
        if value:
            return str(value)
    return ""


def display_value(policy: dict[str, Any], key: str, default: str = "-") -> str:
    """Return a policy field as printable text."""
    value = policy.get(key, default)
    if value is None or value == "":
        return default
    return str(value)


def safe_filename(value: str, default: str = "usb_policy") -> str:
    """Return a filesystem-safe JSON filename based on a policy name."""
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "_", value).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip(" .")
    if not cleaned:
        cleaned = default
    if not cleaned.lower().endswith(".json"):
        cleaned += ".json"
    return cleaned


def prompt_for_output_path(default_path: Path) -> Path:
    """Return a non-existing output path, prompting if the default exists."""
    if not default_path.exists():
        return default_path

    print(f"\nOutput file already exists: {default_path.name}")
    while True:
        response = input("Enter a different output filename: ").strip()
        if not response:
            print("Filename cannot be blank.")
            continue

        candidate = Path(safe_filename(response))
        if candidate.exists():
            print(f"File already exists: {candidate.name}")
            continue

        return candidate


def print_policy_menu(policies: list[dict[str, Any]]) -> None:
    """Print a compact numbered menu for interactive selection."""
    print("\nUSB Device Control policies:\n")
    print(f"{'#':>3}  {'Name':<45}  {'Platform':<10}  {'Enabled':<7}  {'Precedence':<10}  ID")
    print("-" * 110)

    for index, policy in enumerate(policies, start=1):
        name = display_value(policy, "name")[:45]
        platform = display_value(policy, "platform_name")[:10]
        enabled = display_value(policy, "enabled")[:7]
        precedence = display_value(policy, "precedence")[:10]
        print(
            f"{index:>3}  {name:<45}  {platform:<10}  "
            f"{enabled:<7}  {precedence:<10}  {policy_id(policy)}"
        )


def prompt_for_policy(policies: list[dict[str, Any]]) -> dict[str, Any]:
    """Ask the user to select a policy by menu number."""
    while True:
        selection = input("\nSelect a policy number for details, or q to quit: ").strip()
        if selection.lower() in {"q", "quit", "exit"}:
            raise KeyboardInterrupt
        if not selection.isdigit():
            print("Enter a menu number or q.")
            continue

        index = int(selection)
        if 1 <= index <= len(policies):
            return policies[index - 1]
        print(f"Enter a number between 1 and {len(policies)}.")


def get_policy_details(falcon: Any, selected_policy: dict[str, Any]) -> dict[str, Any]:
    """Fetch full details for the selected policy.

    FalconPy 1.6.x provides get_policies_v2 for Device Control with Bluetooth,
    and get_policies for the original Device Control API. Try v2 first, then
    fall back to the original endpoint if the tenant/API version rejects it.
    """
    selected_id = policy_id(selected_policy)
    if not selected_id:
        return selected_policy

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
    return resources[0] if resources else selected_policy


def exception_combined_id(exception: dict[str, Any]) -> str:
    """Return the exception Combined ID, constructing it from parts if needed."""
    combined_id = exception.get("combined_id")
    if combined_id:
        return str(combined_id).strip()

    vendor_id = str(exception.get("vendor_id") or "").strip()
    product_id = str(exception.get("product_id") or "").strip()
    serial_number = str(exception.get("serial_number") or "").strip()
    if not vendor_id or not product_id:
        return ""
    return f"{vendor_id}_{product_id}_{serial_number}"


def matching_exceptions(policies: list[dict[str, Any]], cid: str) -> list[dict[str, Any]]:
    """Return policy exception records whose Combined ID matches cid."""
    normalized_cid = cid.strip()
    matches: list[dict[str, Any]] = []

    for policy in policies:
        usb_settings = policy.get("usb_settings", {})
        classes = usb_settings.get("classes", []) if isinstance(usb_settings, dict) else []
        if not isinstance(classes, list):
            continue

        for class_entry in classes:
            if not isinstance(class_entry, dict):
                continue
            usb_class = str(class_entry.get("class") or "")
            exceptions = class_entry.get("exceptions", [])
            if not isinstance(exceptions, list):
                continue

            for exception in exceptions:
                if not isinstance(exception, dict):
                    continue
                combined_id = exception_combined_id(exception)
                if combined_id == normalized_cid:
                    matches.append({
                        "policy": policy,
                        "usb_class": usb_class,
                        "combined_id": combined_id,
                        "exception": exception,
                    })

    return matches


def print_exception_matches(matches: list[dict[str, Any]]) -> None:
    """Print matching exceptions in a compact table."""
    print("\nMatching USB exceptions:\n")
    print(
        f"{'#':>3}  {'Policy':<45}  {'Class':<18}  {'Exception ID':<34}  "
        f"{'Combined ID':<34}  Description"
    )
    print("-" * 160)
    for index, match in enumerate(matches, start=1):
        policy = match["policy"]
        exception = match["exception"]
        print(
            f"{index:>3}  "
            f"{display_value(policy, 'name', policy_id(policy))[:45]:<45}  "
            f"{str(match['usb_class'])[:18]:<18}  "
            f"{str(exception.get('id') or '-')[:34]:<34}  "
            f"{str(match['combined_id'])[:34]:<34}  "
            f"{str(exception.get('description') or '-')[:40]}"
        )


def prompt_for_exception_removal(matches: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Ask which matching exception should be removed, returning None for no change."""
    while True:
        response = input("\nSelect an exception to remove, or 0 for no change: ").strip()
        if response == "0":
            return None
        if not response.isdigit():
            print("Enter 0 or a menu number.")
            continue

        index = int(response)
        if 1 <= index <= len(matches):
            match = matches[index - 1]
            exception_id = str(match["exception"].get("id") or "").strip()
            if not exception_id:
                print("Selected exception does not include an exception ID and cannot be removed safely.")
                continue
            return match
        print(f"Enter a number between 0 and {len(matches)}.")


def build_delete_exception_payload(policy: dict[str, Any], exception_id: str) -> dict[str, Any]:
    """Build the Device Control payload for deleting one USB exception."""
    return {
        "policies": [
            {
                "id": policy_id(policy),
                "usb_classes": {
                    "delete_exceptions": [exception_id],
                },
            }
        ]
    }


def confirm_exception_removal(match: dict[str, Any]) -> bool:
    """Require explicit confirmation before deleting a policy exception."""
    policy = match["policy"]
    exception = match["exception"]
    print("\nException selected for removal:\n")
    print(json.dumps(exception, indent=2, sort_keys=True))
    response = input(
        f"\nRemove this exception from policy {display_value(policy, 'name', policy_id(policy))!r}? "
        "Type yes or y to continue: "
    ).strip()
    return response.lower() in {"yes", "y"}


def handle_cid_lookup(falcon: Any, policies: list[dict[str, Any]], cid: str) -> int:
    """Find exceptions by Combined ID and optionally remove a selected match."""
    detailed_policies = [get_policy_details(falcon, policy) for policy in policies]
    matches = matching_exceptions(detailed_policies, cid)
    if not matches:
        print(f"No USB exceptions matched Combined ID {cid!r}.")
        return 0

    print_exception_matches(matches)
    selected_match = prompt_for_exception_removal(matches)
    if selected_match is None:
        print("No changes made.")
        return 0

    if not confirm_exception_removal(selected_match):
        print("No changes made.")
        return 0

    exception_id = str(selected_match["exception"].get("id") or "").strip()
    payload = build_delete_exception_payload(selected_match["policy"], exception_id)
    response = require_success(
        falcon.update_policy_classes(body=payload),
        "Device Control USB exception removal",
    )
    print(f"\nRemoved exception {exception_id}.")
    print(f"Update response status: {response.get('status_code')}")
    return 0


def main() -> int:
    """Run the policy query, prompt for a selection, and print details."""
    args = parse_args()

    try:
        from falconpy import DeviceControlPolicies
    except ImportError:
        print(
            "ERROR: falconpy is not installed. Run: "
            "python3 -m pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    try:
        client_id, client_secret, base_url = build_config(args)
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 2

    falcon = DeviceControlPolicies(
        client_id=client_id,
        client_secret=client_secret,
        base_url=base_url,
    )

    try:
        policies = query_all_policies(falcon, args.filter, args.sort)
        if not policies:
            print("No USB Device Control policies were returned by the API.")
            return 0

        if args.cid:
            return handle_cid_lookup(falcon, policies, args.cid)

        print_policy_menu(policies)
        selected_policy = prompt_for_policy(policies)
        details = get_policy_details(falcon, selected_policy)
    except KeyboardInterrupt:
        print("\nNo policy selected. Exiting.")
        return 130
    except RuntimeError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    policy_name = display_value(details, "name", default=policy_id(details) or "usb_policy")
    output_path = prompt_for_output_path(Path.cwd() / safe_filename(policy_name))
    output_path.write_text(json.dumps(details, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\nWrote selected policy details to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
