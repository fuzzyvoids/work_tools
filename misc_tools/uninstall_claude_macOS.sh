#!/bin/bash
# Uninstall Homebrew Claude Code for all users on macOS
# Jamf Pro compatible - runs as root
# Note: ~/.claude config directory is intentionally preserved

# --- Detect Homebrew prefix (Intel vs Apple Silicon) ---
if [[ -x /opt/homebrew/bin/brew ]]; then
    BREW=/opt/homebrew/bin/brew
elif [[ -x /usr/local/bin/brew ]]; then
    BREW=/usr/local/bin/brew
else
    echo "Homebrew not found. Skipping Homebrew uninstall steps."
fi

# --- Uninstall claude-code formula if installed ---
if [[ -n "$BREW" ]]; then
    if "$BREW" list --formula 2>/dev/null | grep -q "^claude-code$"; then
        echo "Uninstalling claude-code via Homebrew..."
        sudo -u "$SUDO_USER" "$BREW" uninstall claude-code
    else
        echo "claude-code formula not found via Homebrew."
    fi

    # --- Remove tap if present ---
    if "$BREW" tap 2>/dev/null | grep -qi "claude"; then
        TAP=$("$BREW" tap | grep -i claude)
        echo "Removing tap: $TAP"
        sudo -u "$SUDO_USER" "$BREW" untap "$TAP"
    fi
fi

# --- Remove the binary directly if it still exists (Homebrew paths) ---
for BIN in /opt/homebrew/bin/claude /usr/local/bin/claude; do
    if [[ -f "$BIN" ]]; then
        echo "Removing leftover binary: $BIN"
        rm -f "$BIN"
    fi
done

# --- Remove Claude Code installed via system-level npm (non-nvm) ---
echo "Checking for Claude Code installed via system npm..."

SYSTEM_NPM_PATHS=(
    /usr/local/bin/npm
    /opt/homebrew/bin/npm
    /usr/bin/npm
)

for NPM_BIN in "${SYSTEM_NPM_PATHS[@]}"; do
    if [[ ! -x "$NPM_BIN" ]]; then
        continue
    fi

    GLOBAL_PREFIX=$("$NPM_BIN" config get prefix 2>/dev/null)
    CLAUDE_PKG="$GLOBAL_PREFIX/lib/node_modules/@anthropic-ai/claude-code"

    if [[ -d "$CLAUDE_PKG" ]]; then
        echo "Found claude-code at: $CLAUDE_PKG -- uninstalling via $NPM_BIN..."
        "$NPM_BIN" uninstall -g @anthropic-ai/claude-code
    else
        echo "claude-code not found under $NPM_BIN global prefix ($GLOBAL_PREFIX)."
    fi
done

# --- Remove Claude Code installed via local-bin / user-level npm for all local users ---
echo "Checking for Claude Code installed via user-local npm prefix..."

while IFS= read -r USER_HOME; do
    USER_NPM_PREFIXES=(
        "$USER_HOME/.local"
        "$USER_HOME/.npm-global"
        "$USER_HOME/.npm"
    )

    for PREFIX in "${USER_NPM_PREFIXES[@]}"; do
        CLAUDE_PKG="$PREFIX/lib/node_modules/@anthropic-ai/claude-code"
        if [[ -d "$CLAUDE_PKG" ]]; then
            echo "Found claude-code at: $CLAUDE_PKG -- removing..."
            rm -rf "$CLAUDE_PKG"
            rm -f "$PREFIX/bin/claude"
        fi
    done

    USER_NPM_CONFIG="$USER_HOME/.npmrc"
    if [[ -f "$USER_NPM_CONFIG" ]]; then
        CUSTOM_PREFIX=$(grep "^prefix=" "$USER_NPM_CONFIG" | cut -d'=' -f2 | tr -d ' ')
        if [[ -n "$CUSTOM_PREFIX" ]]; then
            CLAUDE_PKG="$CUSTOM_PREFIX/lib/node_modules/@anthropic-ai/claude-code"
            if [[ -d "$CLAUDE_PKG" ]]; then
                echo "Found claude-code at custom npm prefix: $CLAUDE_PKG -- removing..."
                rm -rf "$CLAUDE_PKG"
                rm -f "$CUSTOM_PREFIX/bin/claude"
            fi
        fi
    fi

done < <(dscl . -list /Users NFSHomeDirectory | awk '$2 ~ /^\/Users\// {print $2}')

# --- Remove Claude Code installed via nvm/npm for all local users ---
echo "Checking for Claude Code installed via nvm/npm..."

while IFS= read -r USER_HOME; do
    NVM_DIR="$USER_HOME/.nvm"

    if [[ ! -d "$NVM_DIR" ]]; then
        continue
    fi

    echo "Found nvm at: $NVM_DIR"

    while IFS= read -r NPM_BIN; do
        CLAUDE_PKG=$(dirname "$NPM_BIN")/../lib/node_modules/@anthropic-ai/claude-code

        if [[ -d "$CLAUDE_PKG" ]]; then
            echo "Found claude-code at: $CLAUDE_PKG -- uninstalling..."
            sudo -u "$SUDO_USER" "$NPM_BIN" uninstall -g @anthropic-ai/claude-code
        fi
    done < <(find "$NVM_DIR/versions" -name "npm" -type f 2>/dev/null)

done < <(dscl . -list /Users NFSHomeDirectory | awk '$2 ~ /^\/Users\// {print $2}')

# --- Remove any leftover claude binary dropped into nvm shims ---
while IFS= read -r USER_HOME; do
    SHIM="$USER_HOME/.nvm/shims/claude"
    if [[ -f "$SHIM" ]]; then
        echo "Removing nvm shim: $SHIM"
        rm -f "$SHIM"
    fi
done < <(dscl . -list /Users NFSHomeDirectory | awk '$2 ~ /^\/Users\// {print $2}')

# --- Remove Claude Code installed via native installer ---
while IFS= read -r USER_HOME; do
    CLAUDE_SHARE="$USER_HOME/.local/share/claude"
    if [[ -d "$CLAUDE_SHARE" ]]; then
        echo "Found native Claude install at: $CLAUDE_SHARE -- removing..."
        rm -rf "$CLAUDE_SHARE"
        rm -f "$USER_HOME/.local/bin/claude"
    fi
done < <(dscl . -list /Users NFSHomeDirectory | awk '$2 ~ /^\/Users\// {print $2}')

echo "Claude Code uninstall complete. User config directories (~/.claude) have been preserved."
exit 0
