## Written by Rob Fischer, Adv IT Security Spec 2 ##
## General Dynamics Mission Systems               ##
## Last edit: July 8 2026.                        ## 
## Change: added conditional logic to remap       ##
## printer if it already exists                   ##

#!/bin/bash

# Parameterization
# 4 = PRINTER - the "Friendly" name of the printer, for consistency set to the AD name
# 5 = URI - the URI of the printer, typically smb://printqueueserver/hostname e.g. cwapp053.gd-ms.us/idbo02-2ndfl
# 6 = DRIVER - the full path to the driver file. This MUST be installed PRIOR to running this script! e.g. /Library/Printers/PPDs/Contents/Resources/somefile.ppd.gz
# 7 = LOCATION - the "Friendly" location to display in the GUI e.g. "Boise, 2nd floor"
# 8 = DESTINATION - textual information of the destination; i.e. the DNS name of the printer. e.g. IDBO02-2ndFl


PRINTER="$4"
URI="$5"
DRIVER="$6"
LOCATION="$7"
DESTINATION="$8"

# Check if printer already exists & conditionally remove it if so
if /user/bin/lpstat -p "$PRINTER" &>/dev/null; then
  /usr/bin/sudo /usr/sbin/lpadmin -x "$PRINTER"
fi

# Add (Or re-add) printer
/usr/bin/sudo /usr/sbin/lpadmin -p $PRINTER -v $URI -m $DRIVER -L "$LOCATION" -D "$DESTINATION" -o printer-is-shared=false -o auth-info-required=negotiate -E

# Rationale
# -o printer-is-shared=false : tells MacOS not to (re)share the printer out, since it is alredy networked & not local
# -o auth-info-required=negotiate : this is REQUIRE
