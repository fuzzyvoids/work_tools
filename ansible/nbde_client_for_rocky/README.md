# nbde_client_for_rocky

This is just a wrapper around the Red Hat system role nbde_client so that it
works on Rocky by overriding the "distribution" to RedHat.

## Dependencies

You must install the Red Hat ansible system roles package.
`sudo dnf install rhel-system-roles`

## Instructions

It assumes that you will pass in the `nbde_client_bindings` variable.
See `/usr/share/ansible/roles/rhel-system-roles.nbde_client/README.md`.

