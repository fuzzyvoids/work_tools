#!/usr/bin/env python3
"""
Read hosts.json (output of find_hosts.py) and add each host to the
appropriate CrowdStrike site host group based on its sensor grouping tag:

Configurable variables:
  FALCON_CLIENT_ID      CrowdStrike Falcon API client ID. Required.
  FALCON_CLIENT_SECRET  CrowdStrike Falcon API client secret. Required.
  FALCON_BASE_URL       Falcon API base URL, for example https://api.example.crowdstrike.com.
  FALCON_INPUT_FILE     JSON file produced by find_hosts.py. Defaults to hosts.json.
  FALCON_SITE_MAP_JSON  JSON object mapping tag suffixes to site group names, for example
                        {"SITE1":"example-site-1","SITE2":"example-site-2"}.
"""

import json
import os
import sys
from falconpy import HostGroup

CLIENT_ID = os.environ.get("FALCON_CLIENT_ID")
CLIENT_SECRET = os.environ.get("FALCON_CLIENT_SECRET")
BASE_URL = os.environ.get("FALCON_BASE_URL", "https://api.example.crowdstrike.com")
INPUT_FILE = os.environ.get("FALCON_INPUT_FILE", "hosts.json")
BATCH_SIZE = 100

# Maps the suffix of the SensorGroupingTag to the target site name
TAG_SUFFIX_TO_SITE = json.loads(
    os.environ.get(
        "FALCON_SITE_MAP_JSON",
        '{"SITE1":"example-site-1","SITE2":"example-site-2"}',
    )
)


def find_site_group_id(hg_api: HostGroup, site_name: str) -> str:
    """Return the host group ID for the site with the given name."""
    response = hg_api.query_host_groups(
        filter=f"name:'{site_name}'+group_type:'site'",
        limit=5,
    )
    if response["status_code"] != 200:
        raise RuntimeError(
            f"query_host_groups failed: {response['body']}"
        )

    resources = response["body"].get("resources", [])
    if not resources:
        raise ValueError(
            f"No site host group named '{site_name}' found. "
            "Verify the site exists in the Falcon console."
        )
    if len(resources) > 1:
        raise ValueError(
            f"Multiple site host groups matched '{site_name}': {resources}. "
            "Refine the search."
        )

    group_id = resources[0]
    print(f"Found site host group ID: {group_id}")
    return group_id


def add_hosts_to_group(
    hg_api: HostGroup, group_id: str, device_ids: list[str]
) -> None:
    """Add device IDs to the host group in batches."""
    for i in range(0, len(device_ids), BATCH_SIZE):
        batch = device_ids[i : i + BATCH_SIZE]
        filter_expr = "device_id:['" + "','".join(batch) + "']"
        response = hg_api.perform_group_action(
            action_name="add-hosts",
            ids=[group_id],
            filter=filter_expr,
        )
        if response["status_code"] not in (200, 201):
            raise RuntimeError(
                f"perform_group_action failed for batch {i // BATCH_SIZE + 1}: "
                f"{response['body']}"
            )
        added = len(response["body"].get("resources", []))
        print(
            f"  Batch {i // BATCH_SIZE + 1}: submitted {len(batch)} host(s), "
            f"API returned {added} resource(s)"
        )


def site_for_host(host: dict) -> str | None:
    """Return the target site name for a host based on its sensor grouping tags."""
    for tag in host.get("tags", []):
        for suffix, site_name in TAG_SUFFIX_TO_SITE.items():
            if tag.endswith(suffix):
                return site_name
    return None


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print(
            "Error: set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET before running.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        with open(INPUT_FILE) as f:
            hosts = json.load(f)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found. Run find_hosts.py first.", file=sys.stderr)
        sys.exit(1)

    if not hosts:
        print("No hosts in input file. Nothing to do.")
        return

    print(f"Loaded {len(hosts)} host(s) from {INPUT_FILE}")

    # Partition hosts by target site
    site_to_ids: dict[str, list[str]] = {}
    skipped = 0
    for host in hosts:
        site = site_for_host(host)
        if site is None:
            print(
                f"  Warning: no matching tag found for {host['device_id']} "
                f"({host.get('hostname', '')}), skipping."
            )
            skipped += 1
            continue
        site_to_ids.setdefault(site, []).append(host["device_id"])

    if skipped:
        print(f"Skipped {skipped} host(s) with no recognized tag suffix.")

    hg_api = HostGroup(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        base_url=BASE_URL,
    )

    for site_name, device_ids in site_to_ids.items():
        print(f"\nLooking up site '{site_name}'...")
        group_id = find_site_group_id(hg_api, site_name)
        print(f"Adding {len(device_ids)} host(s) to site '{site_name}'...")
        add_hosts_to_group(hg_api, group_id, device_ids)

    print("\nDone.")


if __name__ == "__main__":
    main()
