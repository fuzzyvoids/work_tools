#!/bin/bash

# Edited by Rob Fischer, EDR Security Engineer
# Last edit: 8/17/2
# Removed icons from status messages

echo "============================================"
echo " IPv6 Disable Script"
echo " $(date)"
echo "============================================"

# Check for administrator privileges
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (use sudo)."
    exit 1
fi

# Get all network services (skip the header line)
SERVICES=$(networksetup -listallnetworkservices | tail -n +2)

if [[ -z "$SERVICES" ]]; then
    echo "⚠️  No network services found."
    exit 1
fi

SUCCESS=0
FAILED=0
SKIPPED=0

while IFS= read -r service; do
    # Skip disabled services (prefixed with an asterisk *)
    if [[ "$service" == \** ]]; then
        echo "⏭️  Skipping disabled service: ${service}"
        ((SKIPPED++))
        continue
    fi

    # Get current IPv6 status
    IPV6_STATUS=$(networksetup -getinfo "$service" | grep "IPv6:" | awk '{print $2}')

    if [[ "$IPV6_STATUS" == "Off" ]]; then
        echo "Already disabled: $service"
        ((SKIPPED++))
    else
        # Attempt to disable IPv6
        if networksetup -setv6off "$service" 2>/dev/null; then
            echo "IPv6 disabled: $service"
            ((SUCCESS++))
        else
            echo "Failed to disable IPv6: $service"
            ((FAILED++))
        fi
    fi

done <<< "$SERVICES"

echo ""
echo "============================================"
echo " Summary"
echo "============================================"
echo " Disabled : $SUCCESS interface(s)"
echo " Skipped  : $SKIPPED interface(s)"
echo " Failed   : $FAILED interface(s)"
echo "============================================"

exit 0
