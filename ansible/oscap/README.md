## About
- This role is used collect the scap scores of hosts based off the inventory.yml file
  - my_servers - use the standard CUI from the SSG 
  - my_workstations - use a customized CUI based on the original SSG
- This role should be run with your `$USER.admin` account
- This role should be run with above account from DS0101
- When completed a file in theScores.txt is /tank/projects/IT/SCAP/Latest and should be copied to into 
  it/Configuration_Management/Collect_data 
- When the text is copied then the spreadsheet should be opened and data updated. 

### Future customizations
Any future customization should be updated here with short excerpt of why it was done

### Customizations:
Rocky9/RHEL9 CUI workstatin customized scap profile that were unchecked from the original SSG:
- configure dnf-automatic to install avaialable updates automatically
- enable dnf-automatic-timer - disabled so we don't have systems running with updated packages and not rebooted. 
- enable authselect , authselect automatic for IDM
- lock accounts after failed password attempts ...covered by IDM
- set interval for counting failed password attempts ...covered by IDM
- set lockout time for failed password attempts ...covered by IDM
- prevent login to accouts with empty passwords ...covered by IDM
- disable vsyscalls  --- older xilinx tools will not work correctly
- disable the use of user namespaces ... user containers will be affected
- enable File Access Policy service, --user issues with developing in /home
- disable GSSAPI Authentication - users used to this being available
- force frequent session key renegotiation  - will affect transfer rates across network
- enable the USBGuard Service - affects users plugging items into workstations - some work could be done so it is enabled on workstations, but not lab workstations or items that where usb tatical devices are being plugged in
- Enforce usage of pam_wheel for su authentication - workstations, runners, lab machines, etc. where users may need to su  to another account 

Rocky 8 CUI workstatin customized scap profile that were unchecked from the original SSG:
- configure dnf-automatic to install avaialable updates automatically
- Configure dnf-automatic to install only security updates
- enable dnf-automatic-timer
- enable authselect , authselect automatic for IDM
- lock accounts after failed password attempts ...covered by IDM
- set interval for counting failed password attempts 
- set lockout time for failed password attempts
- prevent login to accouts with empty passwords
- disable vsyscalls  --- older xilinx tools will not work correctly
- disable the use of user namespaces ... user containers will be affected
- enable File Access Policy service, --user issues with developing in /home
- disable kerberos by removing host keytab, connected to IDM
- uninstall nfs-utils ...then nfs won't work
- disable GSSAPI Authentication - users used to this being available
- force frequent session key renegotiation  - will affect transfer rates across network
- enable the USBGuard Service - affects users plugging items into workstations - some work could be done so it is enabled on workstations, but not lab workstations or items that where usb tatical devices are being plugged in


