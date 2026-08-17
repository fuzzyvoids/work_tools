#!/bin/bash

# Written by Rob Fischer, System Administrator
# Last Edit 5/11/26
#

# Parameterization: 
# Paramter 4 = Username to un-associate from Network Account, e.g. john.smith

username=$4

sudo /usr/bin/dscl . delete /Users/$username RecordName $username
sudo /usr/bin/dscl . delete /Users/$username dsAttrTypeStandard:NetworkUser
sudo /usr/bin/dscl . delete /Users/$username dsAttrTypeStandard:OIDCProvider
sudo /usr/bin/dscl . delete /Users/$username dsAttrTypeStandard:AzureUser
sudo /usr/bin/dscl . delete /Users/$username dsAttrTypeStandard:OktaUser

# Retained for reference: the below is how you can do it for the currently logged in user:
# Get current user
# user=$(dscl . read $HOME RecordName | awk '{print substr($0, index($0,$2)) }')

# Removing JamfConnect attributes from current user

# From Jamf docs:
# learn.jamf.com/r/en-US/jamf-connect-documentation-current/Unmigrating_a_Local_Account

# dscl . delete $HOME RecordName $user
# This one didn't return an alias in our environment
# dscl . delete $HOME dsAttrTypeStandard:NetworkUser
# dscl . delete $HOME dsAttrTypeStandard:OIDCProvider
# dscl . delete $HOME dsAttrTypeStandard:AzureUser
# dscl . delete $HOME dsAttrTypeStandard:OktaUser
