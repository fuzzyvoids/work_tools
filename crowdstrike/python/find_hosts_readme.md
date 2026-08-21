# Host Lookup by Grouping Tag

`find_hosts.py` is a read-only CrowdStrike Falcon helper that lists hosts with one or more grouping tags. It supports both `FalconGroupingTags` and `SensorGroupingTags`.

The script writes compact host records to `hosts.json` by default. The JSON output remains compatible with `add_site.py`, which reads `hosts.json` and assigns matching ISci hosts to site host groups.

## Requirements

- Python 3
- `crowdstrike-falconpy`
- Falcon API client with Hosts read permissions

Install FalconPy if needed:

```bash
python3 -m pip install crowdstrike-falconpy
```

If using the local virtual environment in this directory:

```bash
bin/python -m pip install crowdstrike-falconpy
```

## Credentials

Credential lookup order is:

1. CLI arguments: `--client-id`, `--client-secret`, `--base-url`
2. CrowdStrike Gov environment variables: `CS_GOV_CLIENT_ID`, `CS_GOV_CLIENT_SECRET`, `CS_GOV_BASE_URL`
3. Generic Falcon environment variables: `FALCON_CLIENT_ID`, `FALCON_CLIENT_SECRET`, `FALCON_BASE_URL`
4. `~/devel/work_repo/crowdstrike/API.md`, section `RobF_Host_Management`

Use environment variables when possible:

```bash
export CS_GOV_CLIENT_ID="..."
export CS_GOV_CLIENT_SECRET="..."
export CS_GOV_BASE_URL="https://api.laggar.gcw.crowdstrike.com"
```

## Basic Use

Query a fully qualified Falcon grouping tag:

```bash
./find_hosts.py --tag FalconGroupingTags/Janteq
```

Query a bare Falcon grouping tag. Bare tags default to `FalconGroupingTags/`:

```bash
./find_hosts.py --tag Janteq
```

Query a sensor grouping tag:

```bash
./find_hosts.py --tag Enterprise-Workstations --tag-type sensor
```

Query multiple tags in one run:

```bash
./find_hosts.py --tag FalconGroupingTags/Janteq --tag SensorGroupingTags/Enterprise-Workstations
```

Write CSV instead of JSON:

```bash
./find_hosts.py --tag Janteq --format csv --output janteq-hosts.csv
```

Run diagnostics before the tag query:

```bash
./find_hosts.py --tag SensorGroupingTags/LAA-Isci-10293-BOI --diagnose
```

## Tag Files

Use a text file with one tag per line:

```bash
./find_hosts.py --tag-file tags.txt
```

Use a CSV file:

```bash
./find_hosts.py --tag-file tags.csv --csv-column tag
```

If a CSV column is not specified, the script looks for common column names such as `tag`, `tags`, `grouping_tag`, `sensor_tag`, or `falcon_tag`.

## Output Fields

Each output record includes:

- `device_id`
- `hostname`
- `platform_name`
- `status`
- `last_seen`
- `matched_tags`
- `tags`

`matched_tags` contains only the queried tags that matched the host. `tags` contains the full tag list returned by Falcon for the host.

## ISci Site Assignment Workflow

The old script was hardcoded for these ISci sensor tags:

- `SensorGroupingTags/LAA-Isci-10293-BOI`
- `SensorGroupingTags/LAA-Isci-10293-SLC`

The equivalent generic command is:

```bash
./find_hosts.py \
  --tag SensorGroupingTags/LAA-Isci-10293-BOI \
  --tag SensorGroupingTags/LAA-Isci-10293-SLC \
  --output hosts.json
```

After reviewing `hosts.json`, the existing site assignment script can still be run:

```bash
./add_site.py
```

## Notes

- The script is read-only. It does not add, remove, or modify grouping tags.
- Bare tags are treated as Falcon grouping tags unless `--tag-type sensor` is supplied.
- `--include-inactive` removes the default `status:'normal'` filter and includes inactive host records returned by Falcon.
