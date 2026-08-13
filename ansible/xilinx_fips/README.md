# Xilinx FIPS

This role overrides the FIPS settings for the Xilinx Vitis application.
Vitis still relies on some non-FIPS cryptography which causes the application to fail when it calls on the libssl and libcrypto libraries.
This issue is also documented on Xilinx's forum here: https://adaptivesupport.amd.com/s/question/0D5KZ00000pDP2Z0AW/vitis-on-rhel-w-fips-mode-fails-during-create-platform-component

To address this issue, a shared library is pre-loaded using `LD_PRELOAD` that overrides the `libc` version of the `open` function.
The shared library checks to see if the file path name is `/proc/sys/crypto/fips_enabled` and overrides that path to point `/home/tools/Xilinx/fips_enabled`.
This file has the value `0` in it and "tricks" the libraries into thinking that FIPS is disabled on this system.

## Setup

The shared library must be compiled before running the playbook.
Enter into the `files` directory and run `make` to build the shared library.

## Configuration

This role sets the `xilinx_fips_versions` variable by default (`defaults/main.yml`) to a list of known Xilinx versions that have a FIPS issue.
You can override this variable if you want a targetted subset or a version that isn't yet added to the list.
