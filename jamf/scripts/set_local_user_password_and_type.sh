#!/bin/bash

##############################################################################
# Set Local User Password and Account Type
# Written By: Rob Fischer, EDR Security Engineer
# Last Edit: 8/26/26
##############################################################################

# Parameterization
# Parameter 4: username for the local account to change.
# Parameter 5: password to set for the local account.
# Parameter 6: requested account type.
#              User or user = standard user
#              Admin, admin, Administrator, or administrator = administrator
# IMPORTANT NOTES:
# Changing the password this way MAY OR MAY NOT also change the filevault and/or keychain
# passwords. If you use it to change a user account, assist the user in verifying that they
# can still access their keychain and unlock the disk; help them change those passwords as 
# well if not. ALSO, this does not change the Okta/AD password, so it will now be out of sync
# (if applicable), so that will need to be corrected as well.

targetUsername="$4"
targetPassword="$5"
requestedType="$6"

# Creation of functions to perform the work

# Explain why the script stops instead of failing silently in Jamf policy logs.
function fail {
  echo "ERROR: $1"
  exit "$2"
}

# Jamf normally runs scripts as root. Password and group changes require root.
function check_root {
  if [[ "$EUID" -ne 0 ]]; then
    fail "This script must run as root. Jamf policies normally meet this requirement." 77
  fi
}

# Required parameters are validated before making changes so a partial update is avoided.
function check_jamf_parameters {
  if [[ -z "$targetUsername" ]]; then
    fail "Parameter 4 is required and must contain the target username." 74
  fi

  if [[ -z "$targetPassword" ]]; then
    fail "Parameter 5 is required and must contain the new password." 74
  fi

  if [[ -z "$requestedType" ]]; then
    fail "Parameter 6 is required and must contain User, user, Admin, admin, Administrator, or administrator." 74
  fi
}

# The script changes existing local users only. It does not create accounts.
function check_local_user_exists {
  if ! /usr/bin/dscl . -read "/Users/$targetUsername" UniqueID >/dev/null 2>&1; then
    fail "Local user '$targetUsername' was not found. No changes were made." 67
  fi
}

# Normalize the human-friendly Jamf parameter into one internal value.
function normalize_account_type {
  case "$requestedType" in
    User|user)
      normalizedType="standard"
      ;;
    Admin|admin|Administrator|administrator)
      normalizedType="admin"
      ;;
    *)
      fail "Invalid account type '$requestedType'. Use User, user, Admin, admin, Administrator, or administrator." 65
      ;;
  esac
}

# Check current admin membership using an exact username match.
function user_is_admin {
  /usr/bin/dscl . -read "/Groups/admin" GroupMembership 2>/dev/null | \
    /usr/bin/tr ' ' '\n' | \
    /usr/bin/grep -Fxq "$targetUsername"
}

# Change the password first because that is the primary credential operation.
# The password value is never echoed to keep it out of Jamf policy logs.
function change_password {
  echo "Changing password for local user '$targetUsername'."
  if /usr/bin/dscl . -passwd "/Users/$targetUsername" "$targetPassword"; then
    echo "Password changed for local user '$targetUsername'."
  else
    fail "Unable to change password for local user '$targetUsername'." 1
  fi
}

# Apply the requested account type after the password change succeeds.
function set_account_type {
  if [[ "$normalizedType" == "admin" ]]; then
    if user_is_admin; then
      echo "'$targetUsername' already has administrator privileges. No group change required."
    elif /usr/sbin/dseditgroup -o edit -a "$targetUsername" -t user admin; then
      echo "Granted administrator privileges to '$targetUsername'."
    else
      fail "Unable to grant administrator privileges to '$targetUsername'." 1
    fi
  else
    if user_is_admin; then
      if /usr/sbin/dseditgroup -o edit -d "$targetUsername" -t user admin; then
        echo "Removed administrator privileges from '$targetUsername'."
      else
        fail "Unable to remove administrator privileges from '$targetUsername'." 1
      fi
    else
      echo "'$targetUsername' is already a standard user. No group change required."
    fi
  fi
}

# Running the functions to perform the work:

echo "============================================"
echo " Local User Password and Account Type Update"
echo " $(/bin/date)"
echo "============================================"

# Step 1: verify the script has the privileges needed to modify local users.
check_root

# Step 2: verify Jamf supplied all required inputs before changing anything.
check_jamf_parameters

# Step 3: translate the requested account type into predictable internal logic.
normalize_account_type

# Step 4: confirm the target account exists so typos do not create confusing failures.
check_local_user_exists

# Step 5: update the password, then set the requested admin or standard status.
change_password
set_account_type

echo "============================================"
echo " Completed account update for '$targetUsername'."
echo " Requested account type: $normalizedType"
echo "============================================"

exit 0
