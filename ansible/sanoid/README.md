# Sanoid

This role sets up and installs sanoid for automatically taking snapshots on a zfs enabled system.

## Configuration

Refer to the [github project online](https://github.com/jimsalterjrs/sanoid) for documentation on how to configure sanoid.

This role requires a sanoid configuration block to configure the host.
The configuration should be specified as a variable called `sanoid_conf`.

## Sanoid Version

A default version of sanoid is hard coded in the playbook.
See the `Clone sanoid repo` task and the `version` variable of that task.
When upgrading to a newer version, be sure to check the tasks against the new version of sanoid and update the tasks as needed.

Here is an example playbook to apply to the role to ds0101.

```
---
- hosts:
    - ds0101

  tasks:
    - name: sanoid
      include_role:
        name: sanoid
        vars:
          sanoid_conf: |
            [tank/projects]
            frequently = 48
            monthly = 12
            recursive = yes
```

