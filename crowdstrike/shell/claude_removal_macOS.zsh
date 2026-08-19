#!/usr/bin/env zsh

# CrowdStrike RTR script for removing Claude Code binaries from macOS.
#
# Default behavior is intentionally non-interactive for RTR deployment:
#   - find known Claude Code CLI install artifacts
#   - delete only allowlisted binaries, symlinks, npm package directories, and
#     high-confidence cloned Claude/Anthropic repositories
#   - preserve user settings, caches, logs, shell profiles, editor settings, and
#     application support directories

emulate -R zsh
set -o errexit
set -o nounset
set -o pipefail

MODE="delete"
OUTPUT_FORMAT="json"
OUTPUT_FILE="$(mktemp -t claude_removal_macOS_list.XXXXXX)"
SEARCH_BASE="/Users"
SCRIPT_NAME="${0:t}"
SCRIPT_VERSION="1.1.1"
STARTED_AT="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
COMPLETED_AT=""
RESULT="unknown"
EXIT_CODE=0
ERROR_MESSAGE=""
TARGET_COUNT=0
DELETED_COUNT=0
FAILED_COUNT=0
SKIPPED_COUNT=0

typeset -ga LOG_LINES=()

SYSTEM_PATH_DIRS=(
    "/opt/homebrew/bin"
    "/opt/homebrew/sbin"
    "/usr/local/bin"
    "/usr/local/sbin"
    "/usr/bin"
    "/bin"
    "/usr/sbin"
    "/sbin"
    "/opt/local/bin"
    "/opt/local/sbin"
    "/usr/local/share/npm/bin"
)

USER_DOTFILES=(
    ".zshenv"
    ".zprofile"
    ".zshrc"
    ".zlogin"
    ".profile"
    ".bash_profile"
    ".bashrc"
    ".bash_login"
)

USER_REPO_ROOTS=(
    "devel"
    "dev"
    "src"
    "source"
    "sources"
    "code"
    "Code"
    "Projects"
    "repos"
    "Repositories"
    "workspace"
    "workspaces"
    "git"
    "Git"
    "Downloads"
)

SYSTEM_DOTFILES=(
    "/etc/zprofile"
    "/etc/zshrc"
    "/etc/profile"
    "/etc/bashrc"
)

HOMEBREW_BINARIES=(
    "/opt/homebrew/bin/brew"
    "/usr/local/bin/brew"
)

HOMEBREW_PACKAGE_NAMES=(
    "claude-code"
    "claude"
)

usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Finds and optionally removes Claude Code CLI binaries and package install directories on macOS.
The script preserves user configuration and settings by design.

Options:
  -d, --delete          Generate list and delete matches (default)
  -l, --list            Generate list only
      --json            Write a single JSON result object to stdout (default)
      --text            Write human-readable progress output to stdout
  -o, --output FILE     Write list to FILE
  -p, --path PATH       Search user homes under PATH instead of /Users
  -h, --help            Show this help message

Examples:
  $SCRIPT_NAME                     # RTR-friendly default: find and delete
  $SCRIPT_NAME --list              # Inventory only
  $SCRIPT_NAME --path /Users       # Search all normal macOS user homes
EOF
}

log_line() {
    local line="$1"
    LOG_LINES+=("$line")

    if [[ "$OUTPUT_FORMAT" == "text" ]]; then
        print -r -- "$line"
    fi
}

write_status() {
    log_line "[claude-removal-macos] $1"
}

write_error() {
    log_line "[claude-removal-macos] ERROR: $1"
}

append_command_output() {
    local output="$1"
    local line

    [[ -n "$output" ]] || return 0

    while IFS= read -r line || [[ -n "$line" ]]; do
        log_line "$line"
    done <<< "$output"
}

json_escape() {
    local value="$1"
    value="${value//\\/\\\\}"
    value="${value//\"/\\\"}"
    value="${value//$'\n'/\\n}"
    value="${value//$'\r'/\\r}"
    value="${value//$'\t'/\\t}"
    print -r -- "$value"
}

json_string() {
    local value="$1"
    printf '"%s"' "$(json_escape "$value")"
}

emit_json() {
    COMPLETED_AT="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

    local hostname_value computer_name user_value running_as_system
    hostname_value="$(hostname 2>/dev/null || print -r -- "unknown")"
    computer_name="$(scutil --get ComputerName 2>/dev/null || hostname 2>/dev/null || print -r -- "unknown")"
    user_value="$(id -un 2>/dev/null || whoami 2>/dev/null || print -r -- "unknown")"

    if [[ "$(id -u 2>/dev/null || print -r -- 1)" -eq 0 ]]; then
        running_as_system="true"
    else
        running_as_system="false"
    fi

    printf '{\n'
    printf '  "result": '; json_string "$RESULT"; printf ',\n'
    printf '  "exitCode": %d,\n' "$EXIT_CODE"
    printf '  "hostname": '; json_string "$hostname_value"; printf ',\n'
    printf '  "computerName": '; json_string "$computer_name"; printf ',\n'
    printf '  "user": '; json_string "$user_value"; printf ',\n'
    printf '  "runningAsSystem": %s,\n' "$running_as_system"
    printf '  "scriptVersion": '; json_string "$SCRIPT_VERSION"; printf ',\n'
    printf '  "startedAt": '; json_string "$STARTED_AT"; printf ',\n'
    printf '  "completedAt": '; json_string "$COMPLETED_AT"; printf ',\n'

    if [[ -n "$ERROR_MESSAGE" ]]; then
        printf '  "error": '; json_string "$ERROR_MESSAGE"; printf ',\n'
    else
        printf '  "error": null,\n'
    fi

    printf '  "log": [\n'
    local i total
    total=${#LOG_LINES[@]}
    for (( i = 1; i <= total; i++ )); do
        printf '    '
        json_string "${LOG_LINES[$i]}"
        if [[ "$i" -lt "$total" ]]; then
            printf ','
        fi
        printf '\n'
    done
    printf '  ]\n'
    printf '}\n'
}

exit_with_option_error() {
    local message="$1"
    ERROR_MESSAGE="$message"
    RESULT="failed"
    EXIT_CODE=1
    write_error "$message"

    if [[ "$OUTPUT_FORMAT" == "text" ]]; then
        usage >&2
    else
        emit_json
    fi

    exit "$EXIT_CODE"
}

add_if_exists() {
    local candidate="$1"
    local out_file="$2"

    if [[ -e "$candidate" || -L "$candidate" ]]; then
        print -r -- "$candidate" >> "$out_file"
    fi
}

path_is_in_tree() {
    local path_to_check="$1"
    local tree_root="$2"
    local normalized_path="${path_to_check:A}"
    local normalized_root="${tree_root:A}"

    [[ "$normalized_path" == "$normalized_root" || "$normalized_path" == "$normalized_root"/* ]]
}

expand_path_dir() {
    local raw_dir="$1"
    local user_home="$2"
    local inherited_path="$3"

    # Strip common shell quoting and trailing export syntax fragments. This is
    # intentionally a parser for simple PATH assignments, not a shell evaluator.
    raw_dir="${raw_dir%%#*}"
    raw_dir="${raw_dir%%;*}"
    raw_dir="${raw_dir%\"}"
    raw_dir="${raw_dir#\"}"
    raw_dir="${raw_dir%\'}"
    raw_dir="${raw_dir#\'}"
    raw_dir="${raw_dir//\$HOME/$user_home}"
    raw_dir="${raw_dir//\$\{HOME\}/$user_home}"
    raw_dir="${raw_dir/#\~/$user_home}"

    if [[ "$raw_dir" == '$PATH' || "$raw_dir" == '${PATH}' ]]; then
        print -r -- "$inherited_path"
        return 0
    fi

    # Ignore unresolved shell substitutions or variables. Executing dotfiles as
    # root would be unsafe, so complex expressions are deliberately skipped.
    if [[ "$raw_dir" == *'$('* || "$raw_dir" == *'`'* || "$raw_dir" == *'$'* ]]; then
        return 0
    fi

    print -r -- "$raw_dir"
}

add_claude_binary_from_path_dir() {
    local path_dir="$1"
    local out_file="$2"
    local search_root="${3:-}"

    [[ -n "$path_dir" ]] || return 0
    [[ "$path_dir" = /* ]] || return 0
    [[ -d "$path_dir" ]] || return 0

    if [[ -n "$search_root" ]] && ! path_is_in_tree "$path_dir" "$search_root"; then
        return 0
    fi

    add_if_exists "$path_dir/claude" "$out_file"
}

add_system_path_targets() {
    local out_file="$1"
    local path_dir

    for path_dir in "${SYSTEM_PATH_DIRS[@]}"; do
        add_claude_binary_from_path_dir "$path_dir" "$out_file"
    done

    if [[ -f "/etc/paths" ]]; then
        while IFS= read -r path_dir || [[ -n "$path_dir" ]]; do
            path_dir="${path_dir%%#*}"
            add_claude_binary_from_path_dir "$path_dir" "$out_file"
        done < "/etc/paths"
    fi

    local path_file
    for path_file in /etc/paths.d/*(N); do
        [[ -f "$path_file" ]] || continue
        while IFS= read -r path_dir || [[ -n "$path_dir" ]]; do
            path_dir="${path_dir%%#*}"
            add_claude_binary_from_path_dir "$path_dir" "$out_file"
        done < "$path_file"
    done

    add_dotfile_path_targets "/var/root" "$out_file" "system"
}

add_dotfile_path_targets() {
    local user_home="$1"
    local out_file="$2"
    local scope="${3:-user}"
    local inherited_path="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    local dotfile line path_value path_part expanded_part expanded_dir

    local -a dotfiles_to_read=()
    if [[ "$scope" == "system" ]]; then
        dotfiles_to_read=("${SYSTEM_DOTFILES[@]}")
    else
        for dotfile in "${USER_DOTFILES[@]}"; do
            dotfiles_to_read+=("$user_home/$dotfile")
        done
    fi

    for dotfile in "${dotfiles_to_read[@]}"; do
        [[ -f "$dotfile" ]] || continue

        while IFS= read -r line || [[ -n "$line" ]]; do
            line="${line#export }"
            line="${line#typeset -x }"
            line="${line#PATH=PATH}" # no-op guard for malformed text

            case "$line" in
                PATH=*|path=*)
                    path_value="${line#*=}"
                    path_value="${path_value%%[[:space:]]*}"
                    path_value="${path_value%\"}"
                    path_value="${path_value#\"}"
                    path_value="${path_value%\'}"
                    path_value="${path_value#\'}"

                    for path_part in "${(@s/:/)path_value}"; do
                        expanded_part=$(expand_path_dir "$path_part" "$user_home" "$inherited_path")
                        for expanded_dir in "${(@s/:/)expanded_part}"; do
                            add_claude_binary_from_path_dir "$expanded_dir" "$out_file"
                        done
                    done

                    inherited_path="$path_value"
                    ;;
            esac
        done < "$dotfile"
    done
}

add_user_dotfile_path_targets() {
    local user_home="$1"
    local out_file="$2"

    add_dotfile_path_targets "$user_home" "$out_file" "user"
}

is_claude_repo_dir() {
    local repo_dir="$1"

    [[ -d "$repo_dir" ]] || return 1

    local base="${repo_dir:t:l}"
    case "$base" in
        *claude*|*anthropic*)
            ;;
        *)
            return 1
            ;;
    esac

    # Require strong project markers before treating a directory as removable.
    if [[ -d "$repo_dir/.git" ]]; then
        local origin
        origin=$(git -C "$repo_dir" config --get remote.origin.url 2>/dev/null || true)
        origin="${origin:l}"
        case "$origin" in
            *anthropic*/claude-code|*anthropic*/claude-code.git)
                return 0
                ;;
        esac
    fi

    if [[ -f "$repo_dir/package.json" ]]; then
        if grep -Eiq '"name"[[:space:]]*:[[:space:]]*"@anthropic-ai/claude-code"' "$repo_dir/package.json" 2>/dev/null; then
            return 0
        fi
    fi

    return 1
}

is_claude_executable() {
    local item="$1"

    [[ "${item:t}" == "claude" ]] || return 1
    [[ -f "$item" || -L "$item" ]] || return 1
    [[ -x "$item" || -L "$item" ]] || return 1

    return 0
}

is_claude_app_bundle() {
    local app_path="$1"
    local plist="$app_path/Contents/Info.plist"
    local bundle_id display_name bundle_name

    # Keep app deletion intentionally narrow: only the standard Claude.app
    # bundle path is considered, and symlinked bundles are not accepted.
    [[ "$app_path" == "/Applications/Claude.app" ]] || return 1
    [[ -d "$app_path" && ! -L "$app_path" ]] || return 1
    [[ -f "$plist" ]] || return 1

    bundle_id="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$plist" 2>/dev/null || true)"
    display_name="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleDisplayName' "$plist" 2>/dev/null || true)"
    bundle_name="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleName' "$plist" 2>/dev/null || true)"

    [[ "$bundle_id" == com.anthropic* ]] || return 1
    [[ "$display_name" == "Claude" || "$bundle_name" == "Claude" ]] || return 1

    return 0
}

add_homebrew_targets() {
    local out_file="$1"
    local brew_bin package_name

    for brew_bin in "${HOMEBREW_BINARIES[@]}"; do
        [[ -x "$brew_bin" ]] || continue

        for package_name in "${HOMEBREW_PACKAGE_NAMES[@]}"; do
            if "$brew_bin" list --formula --versions "$package_name" >/dev/null 2>&1; then
                print -r -- "homebrew:formula:$brew_bin:$package_name" >> "$out_file"
            fi

            if "$brew_bin" list --cask --versions "$package_name" >/dev/null 2>&1; then
                print -r -- "homebrew:cask:$brew_bin:$package_name" >> "$out_file"
            fi
        done
    done
}

add_user_repo_targets() {
    local user_home="$1"
    local out_file="$2"
    local repo_root repo_dir

    for repo_root in "${USER_REPO_ROOTS[@]}"; do
        repo_root="$user_home/$repo_root"
        [[ -d "$repo_root" ]] || continue

        find "$repo_root" -maxdepth 4 -type d \
            \( -iname '*claude*' -o -iname '*anthropic*' \) \
            -print 2>/dev/null | while IFS= read -r repo_dir; do
            if is_claude_repo_dir "$repo_dir"; then
                print -r -- "$repo_dir" >> "$out_file"
            fi
        done
    done
}

add_global_targets() {
    local out_file="$1"

    # Homebrew and common global npm install locations. These entries are
    # limited to the Claude executable and the Claude Code package directory.
    local -a global_candidates=(
        "/Applications/Claude.app"
        "/opt/homebrew/bin/claude"
        "/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code"
        "/usr/local/bin/claude"
        "/usr/local/lib/node_modules/@anthropic-ai/claude-code"
    )

    local candidate
    for candidate in "${global_candidates[@]}"; do
        add_if_exists "$candidate" "$out_file"
    done

    add_homebrew_targets "$out_file"
    add_system_path_targets "$out_file"
}

add_user_targets() {
    local user_home="$1"
    local out_file="$2"

    [[ -d "$user_home" ]] || return 0

    # npm prefix installs under the user's home directory.
    add_if_exists "$user_home/.npm-global/bin/claude" "$out_file"
    add_if_exists "$user_home/.npm-global/lib/node_modules/@anthropic-ai/claude-code" "$out_file"
    add_if_exists "$user_home/.local/bin/claude" "$out_file"
    add_if_exists "$user_home/.local/lib/node_modules/@anthropic-ai/claude-code" "$out_file"

    # nvm installs one global package tree per Node version.
    if [[ -d "$user_home/.nvm/versions/node" ]]; then
        find "$user_home/.nvm/versions/node" \
            \( -path '*/bin/claude' -o -path '*/lib/node_modules/@anthropic-ai/claude-code' \) \
            \( -type f -o -type l -o -type d \) \
            -print 2>/dev/null >> "$out_file" || true
    fi

    # asdf shims and per-version npm package trees. Only the Claude shim and
    # Claude Code package directories are targeted.
    add_if_exists "$user_home/.asdf/shims/claude" "$out_file"
    if [[ -d "$user_home/.asdf/installs/nodejs" ]]; then
        find "$user_home/.asdf/installs/nodejs" \
            \( -path '*/bin/claude' -o -path '*/lib/node_modules/@anthropic-ai/claude-code' \) \
            \( -type f -o -type l -o -type d \) \
            -print 2>/dev/null >> "$out_file" || true
    fi

    # Volta exposes command shims in ~/.volta/bin and stores global package
    # images separately. Remove only the Claude shim and package image.
    add_if_exists "$user_home/.volta/bin/claude" "$out_file"
    add_if_exists "$user_home/.volta/tools/image/packages/@anthropic-ai/claude-code" "$out_file"

    # Bun can expose npm package binaries here. Remove only the Claude binary.
    add_if_exists "$user_home/.bun/bin/claude" "$out_file"

    # Read dotfiles for additional PATH entries without executing user code.
    add_user_dotfile_path_targets "$user_home" "$out_file"

    # Look for manually cloned Claude/Anthropic repositories in common source
    # directories. These require name and content/git markers before deletion.
    add_user_repo_targets "$user_home" "$out_file"
}

find_targets() {
    local out_file="$1"
    : > "$out_file"

    write_status "Searching global macOS locations."
    add_global_targets "$out_file"

    if [[ ! -d "$SEARCH_BASE" ]]; then
        write_error "Search path does not exist or is not a directory: $SEARCH_BASE"
        return 2
    fi

    if [[ "$SEARCH_BASE" == "/Users" ]]; then
        write_status "Searching user homes under: $SEARCH_BASE"
        local user_home
        for user_home in "$SEARCH_BASE"/*(/N); do
            case "$(basename "$user_home")" in
                Shared)
                    continue
                    ;;
            esac
            add_user_targets "$user_home" "$out_file"
        done
    else
        write_status "Searching user home or home root: $SEARCH_BASE"
        add_user_targets "$SEARCH_BASE" "$out_file"

        local user_home
        for user_home in "$SEARCH_BASE"/*(/N); do
            add_user_targets "$user_home" "$out_file"
        done
    fi

    sort -u "$out_file" -o "$out_file"
}

is_allowed_target() {
    local item="$1"

    case "$item" in
        homebrew:formula:*:claude-code|\
        homebrew:formula:*:claude|\
        homebrew:cask:*:claude-code|\
        homebrew:cask:*:claude|\
        /opt/homebrew/bin/claude|\
        /usr/local/bin/claude|\
        /opt/homebrew/lib/node_modules/@anthropic-ai/claude-code|\
        /usr/local/lib/node_modules/@anthropic-ai/claude-code|\
        */.npm-global/bin/claude|\
        */.npm-global/lib/node_modules/@anthropic-ai/claude-code|\
        */.local/bin/claude|\
        */.local/lib/node_modules/@anthropic-ai/claude-code|\
        */.nvm/versions/node/*/bin/claude|\
        */.nvm/versions/node/*/lib/node_modules/@anthropic-ai/claude-code|\
        */.asdf/shims/claude|\
        */.asdf/installs/nodejs/*/bin/claude|\
        */.asdf/installs/nodejs/*/lib/node_modules/@anthropic-ai/claude-code|\
        */.volta/bin/claude|\
        */.volta/tools/image/packages/@anthropic-ai/claude-code|\
        */.bun/bin/claude)
            return 0
            ;;
        /Applications/Claude.app)
            is_claude_app_bundle "$item"
            return $?
            ;;
        *)
            if is_claude_executable "$item"; then
                return 0
            fi
            if is_claude_repo_dir "$item"; then
                return 0
            fi
            return 1
            ;;
    esac
}

print_list() {
    local list_file="$1"
    local count
    count=$(wc -l < "$list_file" 2>/dev/null | tr -d '[:space:]' || print 0)
    TARGET_COUNT="$count"

    if [[ "$count" -eq 0 ]]; then
        write_status "No Claude Code CLI binaries or package directories found."
        return 0
    fi

    write_status "Found $count item(s):"
    local item
    while IFS= read -r item; do
        [[ -n "$item" ]] || continue

        if [[ -d "$item" && ! -L "$item" ]]; then
            log_line "  [dir]  $item"
        elif [[ "$item" == homebrew:* ]]; then
            local brew_type="${${item#homebrew:}%%:*}"
            local brew_rest="${item#homebrew:$brew_type:}"
            local brew_package="${brew_rest##*:}"
            local brew_bin="${brew_rest%:$brew_package}"
            log_line "  [brew-$brew_type] $brew_package via $brew_bin"
        elif [[ -L "$item" ]]; then
            log_line "  [link] $item -> $(readlink "$item" 2>/dev/null || true)"
        elif [[ -f "$item" ]]; then
            log_line "  [file] $item"
        else
            log_line "  [gone] $item"
        fi
    done < "$list_file"
}

uninstall_homebrew_target() {
    local item="$1"
    local brew_type="${${item#homebrew:}%%:*}"
    local brew_rest="${item#homebrew:$brew_type:}"
    local package_name="${brew_rest##*:}"
    local brew_bin="${brew_rest%:$package_name}"

    [[ "$brew_type" == "formula" || "$brew_type" == "cask" ]] || return 1
    [[ -x "$brew_bin" ]] || return 1

    if [[ "$brew_type" == "formula" ]]; then
        "$brew_bin" uninstall --formula "$package_name"
    else
        "$brew_bin" uninstall --cask "$package_name"
    fi
}

perform_deletion() {
    local list_file="$1"
    local deleted=0
    local failed=0
    local skipped=0
    local command_output

    local item
    while IFS= read -r item; do
        [[ -n "$item" ]] || continue
        [[ "$item" == homebrew:* ]] || continue

        if ! is_allowed_target "$item"; then
            log_line "  Skipped non-allowlisted path: $item"
            (( skipped++ )) || true
            continue
        fi

        if command_output="$(uninstall_homebrew_target "$item" 2>&1)"; then
            append_command_output "$command_output"
            log_line "  Uninstalled Homebrew package: $item"
            (( deleted++ )) || true
        else
            append_command_output "$command_output"
            log_line "  FAILED Homebrew package:      $item"
            (( failed++ )) || true
        fi
    done < "$list_file"

    while IFS= read -r item; do
        [[ -n "$item" ]] || continue
        [[ "$item" != homebrew:* ]] || continue

        if ! is_allowed_target "$item"; then
            log_line "  Skipped non-allowlisted path: $item"
            (( skipped++ )) || true
            continue
        fi

        if [[ -L "$item" ]]; then
            if rm -f "$item"; then
                log_line "  Deleted link: $item"
                (( deleted++ )) || true
            else
                log_line "  FAILED link:  $item"
                (( failed++ )) || true
            fi
        elif [[ -d "$item" ]]; then
            if rm -rf "$item"; then
                log_line "  Deleted dir:  $item"
                (( deleted++ )) || true
            else
                log_line "  FAILED dir:   $item"
                (( failed++ )) || true
            fi
        elif [[ -f "$item" ]]; then
            if rm -f "$item"; then
                log_line "  Deleted file: $item"
                (( deleted++ )) || true
            else
                log_line "  FAILED file:  $item"
                (( failed++ )) || true
            fi
        else
            log_line "  Skipped missing item: $item"
            (( skipped++ )) || true
        fi
    done < "$list_file"

    DELETED_COUNT="$deleted"
    FAILED_COUNT="$failed"
    SKIPPED_COUNT="$skipped"

    write_status "Deletion complete. Deleted: $deleted  Failed: $failed  Skipped: $skipped"

    if [[ "$failed" -gt 0 ]]; then
        return 1
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--delete)
            MODE="delete"
            shift
            ;;
        -l|--list)
            MODE="list"
            shift
            ;;
        --json)
            OUTPUT_FORMAT="json"
            shift
            ;;
        --text)
            OUTPUT_FORMAT="text"
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="${2:-}"
            [[ -n "$OUTPUT_FILE" ]] || exit_with_option_error "--output requires a file."
            shift 2
            ;;
        -p|--path)
            SEARCH_BASE="${2:-}"
            [[ -n "$SEARCH_BASE" ]] || exit_with_option_error "--path requires a directory."
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            exit_with_option_error "Unknown option: $1"
            ;;
    esac
done

if find_targets "$OUTPUT_FILE"; then
    print_list "$OUTPUT_FILE"
    write_status "List saved to: $OUTPUT_FILE"

    if [[ "$MODE" == "delete" ]]; then
        if perform_deletion "$OUTPUT_FILE"; then
            :
        else
            EXIT_CODE=$?
            RESULT="failed"
            ERROR_MESSAGE="Deletion completed with one or more failures."
        fi
    fi
else
    EXIT_CODE=$?
    RESULT="failed"
    ERROR_MESSAGE="Discovery failed."
fi

if [[ "$EXIT_CODE" -eq 0 ]]; then
    if [[ "$MODE" == "list" ]]; then
        if [[ "$TARGET_COUNT" -gt 0 ]]; then
            RESULT="found"
        else
            RESULT="not_found"
        fi
    else
        if [[ "$TARGET_COUNT" -eq 0 ]]; then
            RESULT="not_found"
        elif [[ "$DELETED_COUNT" -gt 0 ]]; then
            RESULT="deleted"
        elif [[ "$SKIPPED_COUNT" -gt 0 ]]; then
            RESULT="skipped"
        else
            RESULT="completed"
        fi
    fi
fi

if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    emit_json
fi

exit "$EXIT_CODE"
