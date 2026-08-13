#!/usr/bin/env python3
"""
Find all hosts tagged with one or more CrowdStrike sensor grouping tags and
write them to hosts.json.

Configurable variables:
  FALCON_CLIENT_ID      CrowdStrike Falcon API client ID. Required.
  FALCON_CLIENT_SECRET  CrowdStrike Falcon API client secret. Required.
  FALCON_BASE_URL       Falcon API base URL, for example https://api.example.crowdstrike.com.
  FALCON_OUTPUT_FILE    Output JSON path. Defaults to hosts.json.
  FALCON_TAGS           Comma-separated SensorGroupingTags values to query.

Pass --diagnose to run diagnostic checks before the main query.
"""

import json
import os
import sys
from falconpy import Hosts

CLIENT_ID = os.environ.get("FALCON_CLIENT_ID")
CLIENT_SECRET = os.environ.get("FALCON_CLIENT_SECRET")
BASE_URL = os.environ.get("FALCON_BASE_URL", "https://api.example.crowdstrike.com")
OUTPUT_FILE = os.environ.get("FALCON_OUTPUT_FILE", "hosts.json")

TAGS = [
    tag.strip()
    for tag in os.environ.get(
        "FALCON_TAGS",
        "SensorGroupingTags/example-site-1,SensorGroupingTags/example-site-2",
    ).split(",")
    if tag.strip()
]


def get_hosts_for_tag(hosts_api: Hosts, tag: str) -> list[str]:
    """Return all device IDs matching the given sensor grouping tag."""
    device_ids = []
    offset = 0
    limit = 500

    while True:
        response = hosts_api.query_devices_by_filter(
            filter=f"tags:'{tag}'",
            limit=limit,
            offset=offset,
        )
        if response["status_code"] != 200:
            raise RuntimeError(
                f"query_devices_by_filter failed for tag '{tag}': "
                f"{response['body']}"
            )

        resources = response["body"].get("resources", [])
        device_ids.extend(resources)

        total = response["body"]["meta"]["pagination"]["total"]
        offset += len(resources)
        if offset >= total or not resources:
            break

    return device_ids


def get_host_details(hosts_api: Hosts, device_ids: list[str]) -> list[dict]:
    """Fetch full device details for a list of device IDs (in batches of 100)."""
    details = []
    batch_size = 100

    for i in range(0, len(device_ids), batch_size):
        batch = device_ids[i : i + batch_size]
        response = hosts_api.get_device_details(ids=batch)
        if response["status_code"] != 200:
            raise RuntimeError(
                f"get_device_details failed: {response['body']}"
            )
        details.extend(response["body"].get("resources", []))

    return details


def diagnose(hosts_api: Hosts) -> None:
    """Run diagnostic checks to identify why tag queries return 0 results."""
    print("=" * 60)
    print("DIAGNOSTIC MODE")
    print("=" * 60)

    # 1. Unfiltered query — confirms connectivity and that hosts exist
    print("\n[1] Unfiltered query (limit=2) — confirm API connectivity:")
    resp = hosts_api.query_devices_by_filter(limit=2)
    print(f"    status_code: {resp['status_code']}")
    ids = resp["body"].get("resources", [])
    total = resp["body"].get("meta", {}).get("pagination", {}).get("total", "?")
    print(f"    total hosts visible: {total}")
    print(f"    sample ids: {ids}")

    if not ids:
        print("    ERROR: No hosts returned at all — check credentials/base_url.")
        return

    # 2. Inspect tags on one sample host
    print(f"\n[2] Tags on sample host {ids[0]}:")
    det = hosts_api.get_device_details(ids=[ids[0]])
    if det["status_code"] == 200:
        host = det["body"]["resources"][0]
        tags = host.get("tags", [])
        print(f"    tags field: {json.dumps(tags, indent=6)}")
    else:
        print(f"    ERROR fetching details: {det['body']}")

    # 3. Try each filter variant for the first target tag
    tag = TAGS[0]
    variants = [
        f"tags:'{tag}'",
        f'tags:"{tag}"',
        f"tags:['{tag}']",
        f'tags:["{tag}"]',
        f"tags:*'{tag}'*",
    ]
    print(f"\n[3] Filter variants for: {tag}")
    for fql in variants:
        r = hosts_api.query_devices_by_filter(filter=fql, limit=5)
        count = len(r["body"].get("resources", []))
        total = r["body"].get("meta", {}).get("pagination", {}).get("total", "?")
        errors = r["body"].get("errors", [])
        print(f"    filter={fql!r}")
        print(f"      status={r['status_code']}  total={total}  returned={count}  errors={errors}")

    # 4. Try the same tags with FalconGroupingTags prefix
    falcon_tag = tag.replace("SensorGroupingTags/", "FalconGroupingTags/")
    print(f"\n[4] Retry with FalconGroupingTags prefix: {falcon_tag}")
    for fql in [f"tags:'{falcon_tag}'", f'tags:"{falcon_tag}"']:
        r = hosts_api.query_devices_by_filter(filter=fql, limit=5)
        count = len(r["body"].get("resources", []))
        total = r["body"].get("meta", {}).get("pagination", {}).get("total", "?")
        errors = r["body"].get("errors", [])
        print(f"    filter={fql!r}")
        print(f"      status={r['status_code']}  total={total}  returned={count}  errors={errors}")

    # 5. Find any host tagged with the configured sample prefix to see real tag format.
    sample_tag_fragment = os.environ.get("FALCON_TAG_DIAGNOSTIC_FRAGMENT", "example")
    print(f"\n[5] Hunting for any host with a {sample_tag_fragment!r} tag (sampling 200 hosts):")
    sample_ids = []
    r = hosts_api.query_devices_by_filter(limit=200)
    sample_ids = r["body"].get("resources", [])
    matching_tags_found = {}
    for i in range(0, len(sample_ids), 100):
        batch = sample_ids[i:i+100]
        det = hosts_api.get_device_details(ids=batch)
        if det["status_code"] != 200:
            continue
        for host in det["body"].get("resources", []):
            for t in host.get("tags", []):
                if sample_tag_fragment.lower() in t.lower():
                    matching_tags_found[t] = host["device_id"]
    if matching_tags_found:
        print(f"    Found {len(matching_tags_found)} unique matching tag(s):")
        for t, hid in list(matching_tags_found.items())[:10]:
            print(f"      {t!r}  (host: {hid})")
    else:
        print("    No matching tags found in 200-host sample — tags may not exist in this tenant/scope.")

    print("\n" + "=" * 60)
    print("END DIAGNOSTICS — review output above before re-running normally.")
    print("=" * 60 + "\n")


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print(
            "Error: set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET before running.",
            file=sys.stderr,
        )
        sys.exit(1)

    diagnose_mode = "--diagnose" in sys.argv

    hosts_api = Hosts(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        base_url=BASE_URL,
    )

    if diagnose_mode:
        diagnose(hosts_api)
        return

    all_device_ids: set[str] = set()
    for tag in TAGS:
        print(f"Querying hosts with tag: {tag}")
        ids = get_hosts_for_tag(hosts_api, tag)
        print(f"  Found {len(ids)} host(s)")
        all_device_ids.update(ids)

    print(f"\nTotal unique hosts: {len(all_device_ids)}")

    if not all_device_ids:
        print("No hosts found. Writing empty output.")
        with open(OUTPUT_FILE, "w") as f:
            json.dump([], f, indent=2)
        return

    print("Fetching host details...")
    host_details = get_host_details(hosts_api, list(all_device_ids))

    # Retain the fields most useful for the site-assignment step
    output = [
        {
            "device_id": h["device_id"],
            "hostname": h.get("hostname", ""),
            "platform_name": h.get("platform_name", ""),
            "tags": h.get("tags", []),
        }
        for h in host_details
    ]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(output)} host(s) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
