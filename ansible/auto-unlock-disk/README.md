# Auto Unlock Disk

NOTICE: This role should be considered deprecated.
The `nbde_client_for_rocky` role should be considered it's replacement.
If/when Red Hat adds built-in support for Rocky, then Red Hat's own `redhat.rhel_system_roles.nbde_client` role should be used.


This role utilizes Tang and Clevis to automatically unlock LUKS encrypted disks at boot time.
This is known as Network Bound Disk Encryption (NBDE).
At a high level, it installs Clevis, binds to the LUKS disk, and then regenerates the initramfs with the configuration required to unlock at boot.
If the Tang server is unavailable for automatic unlocking the disk password may be entered as usual at the keyboard.

This is a wrapper around the Red Hat System Role Network Bound Disk Encryption client (`nbde_client`).
A wrapper is necessary because the `nbde_client` does not yet support Rocky Linux and fails to execute on Rocky.
This wrapper essentially rewrites the ansible_facts to lie and say that we are a Red Hat machine so that the `nbde_client` role will operate correctly.
It also uses some legacy variables from when we tried to do nbde on our own before we knew the `nbde_client` role existed.

It is not as fully featured as the `nbde_client` role.
For example, this role only supports a single tang server.
Also, the `nbde_client` role supports and array of settings in case you had multiple encrypted disks to setup.
This role only supports a single encrypted disk.

This role contains the following variables that should be overridden to reflect the machine information:

* `luks_device` - The device name with the LUKS encryption.
  For example, `/dev/sda3`.
* `luks_password` - The current password for the LUKS encrypted disk.
* `tang_url` - The URL to connect to the tang server.

The `luks_device` variable may or may not need to be changed.
It depends on your hardware and disk configuration.

It is expected that the `luks_password` will need to be set for existing installs with encrypted disks.
If this is a new install and the disk is encrypted with the default `server` password, then the variable will not need to be set because `server` is the default password.

The `tang_url` will likely not need to be changed unless you are completing an advanced install.

This role is very basic and assumes that there is only one Tang server deployed and that this is the only Tang server the disk is every expected to connect to.

## References

* [RHEL 9 - Security Hardening](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/security_hardening/configuring-automated-unlocking-of-encrypted-volumes-using-policy-based-decryption_security-hardening)
