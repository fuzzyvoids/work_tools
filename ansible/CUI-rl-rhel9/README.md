DRAFT - Unclassified Information in Non-federal Information Systems and Organizations (NIST 800-171)
=========

Ansible Role for DRAFT - Unclassified Information in Non-federal Information Systems and Organizations (NIST 800-171)  
  
Profile Description:  
From NIST 800-171, Section 2.2:  
Security requirements for protecting the confidentiality of CUI in nonfederal  
information systems and organizations have a well-defined structure that  
consists of:  
(i) a basic security requirements section;  
(ii) a derived security requirements section.  
The basic security requirements are obtained from FIPS Publication 200, which  
provides the high-level and fundamental security requirements for federal  
information and information systems. The derived security requirements, which  
supplement the basic security requirements, are taken from the security controls  
in NIST Special Publication 800-53.  
This profile configures Red Hat Enterprise Linux 9 to the NIST Special  
Publication 800-53 controls identified for securing Controlled Unclassified  
Information (CUI)."

The tasks that are used in this role are generated using OpenSCAP.
See the OpenSCAP project for more details on Ansible playbook generation at [https://github.com/OpenSCAP/openscap](https://github.com/OpenSCAP/openscap)

To submit a fix or enhancement for an Ansible task that is failing or missing in this role,
see the ComplianceAsCode project at [https://github.com/ComplianceAsCode/content](https://github.com/ComplianceAsCode/content)

Requirements
------------

- Ansible version 2.9 or higher

Role Variables
--------------

To customize the role to your liking, check out the [list of variables](defaults/main.yml).

Dependencies
------------

N/A

Example Role Usage
----------------

Run `ansible-galaxy install RedHatOfficial.rhel9_cui` to
download and install the role. Then, you can use the following playbook snippet to run the Ansible role:

    - hosts: all
      roles:
         - { role: RedHatOfficial.rhel9_cui }

Next, check the playbook using (on the localhost) the following example:

    ansible-playbook -i "localhost," -c local --check playbook.yml

To deploy it, use (this may change configuration of your local machine!):

    ansible-playbook -i "localhost," -c local playbook.yml

## ISCI DN usage:
Use `cui-remediation.yml` with inventory.yml
```
- hosts: gem
  roles:
    - { role: CUI-rl-rhel9, when: ansible_distribution_major_version == '9' }
    - { role: CUI-rl-rhel8, when: ansible_distribution_major_version == '8' }
```
  `ansible-playbook -u $USER.admin -i cui-remediation.yml -i inventory.yml`
  
License
-------

BSD-3-Clause

Author Information
------------------

This Ansible remediation role has been generated from the body of security
policies developed by the ComplianceAsCode project. Please see
[https://github.com/complianceascode/content/blob/master/Contributors.md](https://github.com/complianceascode/content/blob/master/Contributors.md)
for an updated list of authors and contributors.

## Modifications for ISCI darknet
**Note there was no FIPS setup/remediation in this role**
1. Move all package installs to one task 
2. One Package facts task 
3. In the defaults/main.yml 
- Disabled across board:
- DISA_STIG_RHEL_09_212035: false  
  Virtual Syscalls provide an opportunity of attack for a user who has control of the return instruction pointer.  Some versions of Xilinx won't run correctly and will give wierd errors. 
- DISA_STIG_RHEL_09_213115: false, service_kdump_disabled: false 
  Kernel core dumps may contain the full contents of system memory at the time of the crash. Kernel core dumps consume a considerable amount of disk space and may result in denial of service by exhausting the available space on the target file system partition. Unless the system is used for kernel development or testing, there is little need to run the kdump  service.
- DISA_STIG_RHEL_09_255090: false  
  By decreasing the limit based on the amount of data and enabling time-based limit, effects of potential attacks against encryption keys are limited. Recommended setting is 1G 1H, which would have significant impact on transfers. 
- DISA_STIG_RHEL_09_411075: false
  Lock Accounts After Failed Password Attempts, screws with authselect. RHEL recommends not doing a custom profile when connecting to IDM or Windows domain. 
- DISA_STIG_RHEL_09_411085: false
  Set Interval For Counting Failed Password Attempts, screws with authselect. RHEL recommends not doing a custom profile when connecting to IDM or Windows domain.
- DISA_STIG_RHEL_09_411090: false
  Set Lockout Time for Failed Password Attempts, screws with authselect. RHEL recommends not doing a custom profile when connecting to IDM or Windows domain.
- DISA_STIG_RHEL_09_611025: false
  Prevent Login to Accounts With Empty Password, screws with authselect. RHEL recommends not doing a custom profile when connecting to IDM or Windows domain.
- DISA_STIG_needed_rules: false
  Enable authselect, and creation of custom profile, screws with authselect. RHEL recommends not doing a custom profile when connecting to IDM or Windows domain.
- sysctl_user_max_user_namespaces: false -  impact to containers if set to true
4. Items limited to physical_servers and virtual_hosts by adding `inventory_hostname in groups['physical_servers:virtual_hosts']` to related tasks below
- DISA-STIG-RHEL-09-433015 - Fapolicyd enabled 
- DISA-STIG-RHEL-09-291020 - USBGuard enable
- Configure OpenSSL to use FIPS
  - DISA-STIG-RHEL-09-215105
  - DISA-STIG-RHEL-09-672030
- DISA-STIG-RHEL-09-412080 - Set 'StopIdleSessionSec' to '1800' in the [Login] section of '/etc/systemd/logind.conf'
- DISA-STIG-RHEL-09-255135 - Disable GSSAPI Authentication
- DISA-STIG-RHEL-09-255140 - Disable Kerberos Authentication
5. add to var/main.yml and special task in tasks/main.yml to put gpgcheck=0 back for these two repos
```
fix_repos:
  - /etc/yum.repos.d/isci.repo
  - /etc/yum.repos.d/libre-office.repo
```
