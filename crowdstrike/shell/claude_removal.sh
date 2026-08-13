#!/usr/bin/env sh

#!/usr/bin/env bash

set -euo pipefail

TEMP_FILE="/tmp/claude_removal_list_$(date +%Y%m%d_%H%M%S).txt"
MODE="list"
INPUT_FILE=""
SEARCH_BASE="$HOME"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Finds and optionally removes Claude Code executable files, libraries, and VS Code extensions.

Options:
  -l, --list            Generate list only, write to temp file (default)
  -d, --delete          Generate list and delete after confirmation
  -f, --file FILE       Use existing list file instead of running find (combine with --delete)
  -o, --output FILE     Write list to FILE instead of default temp file
  -p, --path PATH       Search PATH instead of \$HOME (e.g. /home to scan all users)
  -h, --help            Show this help message

Examples:
  $(basename "$0")                         # Generate list, search \$HOME (default)
  $(basename "$0") --list                  # Same as above
  $(basename "$0") --path /home            # Search all user home dirs under /home
  $(basename "$0") --delete                           # Find and delete with confirmation
  $(basename "$0") --delete --path /home              # Find across all users, delete with confirmation
  $(basename "$0") --delete --file /tmp/mylist.txt    # Delete from existing list file
  $(basename "$0") --list --output ~/my_claude_list.txt
EOF
}

find_targets() {
    local out_file="$1"
    : > "$out_file"

    if [[ "$SEARCH_BASE" == "$HOME" ]]; then
        # Single user: search directly in $HOME subdirs
        echo "Searching for Claude Code executables and libraries in: $SEARCH_BASE"
        find "$SEARCH_BASE/.nvm" "$SEARCH_BASE/.npm-global" "$SEARCH_BASE/.local" \
            -name "claude" \( -type f -o -type l \) 2>/dev/null >> "$out_file" || true
        # Catch the versioned install tree (e.g. ~/.local/share/claude/)
        [[ -d "$SEARCH_BASE/.local/share/claude" ]] && echo "$SEARCH_BASE/.local/share/claude" >> "$out_file" || true

        echo "Searching for Claude Code VS Code extensions in: $SEARCH_BASE"
        find "$SEARCH_BASE" -maxdepth 2 \( \
            -name ".vscode" -o -name ".vscode-insiders" -o -name ".vscode-server" \
            -o -name ".cursor" -o -name ".windsurf" \
            \) -type d 2>/dev/null | while IFS= read -r ext_root; do
            find "$ext_root/extensions" -maxdepth 1 -name "anthropic.claude-code*" -type d 2>/dev/null >> "$out_file" || true
        done
    else
        # Multi-user: iterate over immediate subdirectories of SEARCH_BASE
        echo "Searching for Claude Code executables and libraries under: $SEARCH_BASE"
        for user_home in "$SEARCH_BASE"/*/; do
            [[ -d "$user_home" ]] || continue
            find "${user_home}.nvm" "${user_home}.npm-global" "${user_home}.local" \
                -name "claude" \( -type f -o -type l \) 2>/dev/null >> "$out_file" || true
            [[ -d "${user_home}.local/share/claude" ]] && echo "${user_home}.local/share/claude" >> "$out_file" || true
        done

        echo "Searching for Claude Code VS Code extensions under: $SEARCH_BASE"
        for user_home in "$SEARCH_BASE"/*/; do
            [[ -d "$user_home" ]] || continue
            find "$user_home" -maxdepth 2 \( \
                -name ".vscode" -o -name ".vscode-insiders" -o -name ".vscode-server" \
                -o -name ".cursor" -o -name ".windsurf" \
                \) -type d 2>/dev/null | while IFS= read -r ext_root; do
                find "$ext_root/extensions" -maxdepth 1 -name "anthropic.claude-code*" -type d 2>/dev/null >> "$out_file" || true
            done
        done
    fi

    sort -u "$out_file" -o "$out_file"
}

print_list() {
    local list_file="$1"
    local count
    count=$(wc -l < "$list_file" 2>/dev/null || echo 0)

    if [[ "$count" -eq 0 ]]; then
        echo "No Claude Code files or directories found."
    else
        echo ""
        echo "Found $count item(s):"
        while IFS= read -r item; do
            if [[ -d "$item" ]]; then
                echo "  [dir]  $item"
            elif [[ -f "$item" ]]; then
                echo "  [file] $item"
            else
                echo "  [gone] $item"
            fi
        done < "$list_file"
        echo ""
    fi
}

confirm_deletion() {
    local list_file="$1"
    local count
    count=$(wc -l < "$list_file" 2>/dev/null || echo 0)

    if [[ "$count" -eq 0 ]]; then
        echo "Nothing to delete."
        return 1
    fi

    read -r -p "Delete these $count item(s)? [y/N] " response
    [[ "${response,,}" == "y" ]]
}

perform_deletion() {
    local list_file="$1"
    local deleted=0
    local failed=0

    while IFS= read -r item; do
        if [[ -d "$item" && ! -L "$item" ]]; then
            if rm -rf "$item"; then
                echo "  Deleted dir:  $item"
                (( deleted++ )) || true
            else
                echo "  FAILED:       $item"
                (( failed++ )) || true
            fi
        elif [[ -L "$item" ]]; then
            local target
            target=$(readlink -f "$item")
            if rm -f "$item"; then
                echo "  Deleted link: $item"
                (( deleted++ )) || true
            else
                echo "  FAILED:       $item"
                (( failed++ )) || true
            fi
            # Remove the symlink target if it still exists and wasn't already listed
            if [[ -n "$target" && -e "$target" ]]; then
                if rm -rf "$target"; then
                    echo "  Deleted target: $target"
                    (( deleted++ )) || true
                else
                    echo "  FAILED target:  $target"
                    (( failed++ )) || true
                fi
            fi
        elif [[ -f "$item" ]]; then
            if rm -f "$item"; then
                echo "  Deleted file: $item"
                (( deleted++ )) || true
            else
                echo "  FAILED:       $item"
                (( failed++ )) || true
            fi
        else
            echo "  Skipped (not found): $item"
        fi
    done < "$list_file"

    echo ""
    echo "Done. Deleted: $deleted  Failed: $failed"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -l|--list)
            MODE="list"
            shift
            ;;
        -d|--delete)
            MODE="delete"
            shift
            ;;
        -f|--file)
            INPUT_FILE="${2:-}"
            if [[ -z "$INPUT_FILE" ]]; then
                echo "Error: --file requires a filename argument." >&2
                exit 1
            fi
            shift 2
            ;;
        -o|--output)
            TEMP_FILE="${2:-}"
            if [[ -z "$TEMP_FILE" ]]; then
                echo "Error: --output requires a filename argument." >&2
                exit 1
            fi
            shift 2
            ;;
        -p|--path)
            SEARCH_BASE="${2:-}"
            if [[ -z "$SEARCH_BASE" ]]; then
                echo "Error: --path requires a directory argument." >&2
                exit 1
            fi
            if [[ ! -d "$SEARCH_BASE" ]]; then
                echo "Error: Path does not exist or is not a directory: $SEARCH_BASE" >&2
                exit 1
            fi
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

case "$MODE" in
    list)
        find_targets "$TEMP_FILE"
        print_list "$TEMP_FILE"
        echo "List saved to: $TEMP_FILE"
        ;;
    delete)
        if [[ -n "$INPUT_FILE" ]]; then
            # --delete --file: skip find, use the provided list
            if [[ ! -f "$INPUT_FILE" ]]; then
                echo "Error: File not found: $INPUT_FILE" >&2
                exit 1
            fi
            echo "Reading list from: $INPUT_FILE"
            print_list "$INPUT_FILE"
            if confirm_deletion "$INPUT_FILE"; then
                echo ""
                perform_deletion "$INPUT_FILE"
            else
                echo "Deletion cancelled."
            fi
        else
            # --delete only: find then delete
            find_targets "$TEMP_FILE"
            print_list "$TEMP_FILE"
            echo "List saved to: $TEMP_FILE"
            if confirm_deletion "$TEMP_FILE"; then
                echo ""
                perform_deletion "$TEMP_FILE"
            else
                echo "Deletion cancelled."
            fi
        fi
        ;;
esac
