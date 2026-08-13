[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Script:OutputBuffer = New-Object System.Collections.Generic.List[string]
$Script:ScriptVersion = '2026-07-21-host-bash-file-bounded-expanded-v3'
$Script:ChildTimeoutSeconds = 90
$Script:CurrentScriptPath = $PSCommandPath
$Script:CurrentScriptText = $null
if (-not [string]::IsNullOrWhiteSpace($Script:CurrentScriptPath) -and [IO.File]::Exists($Script:CurrentScriptPath)) {
    $Script:CurrentScriptText = [IO.File]::ReadAllText($Script:CurrentScriptPath)
}
else {
    $Script:CurrentScriptPath = $null
    $definition = $MyInvocation.MyCommand.Definition
    if (-not [string]::IsNullOrWhiteSpace($definition) -and [IO.File]::Exists($definition)) {
        $Script:CurrentScriptPath = $definition
        $Script:CurrentScriptText = [IO.File]::ReadAllText($definition)
    }
    else {
        $Script:CurrentScriptText = $definition
    }
}

$EmbeddedRemovalScriptLines = @(
    'set -euo pipefail',
    '',
    'SEARCH_BASE="/home"',
    'OUTPUT_FILE="/tmp/claude_removal_list_$(date +%Y%m%d_%H%M%S).txt"',
    '',
    'add_if_exists() {',
    '    local path="$1"',
    '    local out_file="$2"',
    '',
    '    if [[ -e "$path" || -L "$path" ]]; then',
    '        printf ''%s\n'' "$path" >> "$out_file"',
    '    fi',
    '}',
    '',
    'find_for_home() {',
    '    local user_home="$1"',
    '    local out_file="$2"',
    '',
    '    [[ -d "$user_home" ]] || return 0',
    '    echo "Scanning home: $user_home"',
    '',
    '    add_if_exists "$user_home/.local/bin/claude" "$out_file"',
    '    add_if_exists "$user_home/.npm-global/bin/claude" "$out_file"',
    '',
    '    if [[ -d "$user_home/.nvm" ]]; then',
    '        find "$user_home/.nvm" -maxdepth 8 -name "claude" \( -type f -o -type l \) 2>/dev/null >> "$out_file" || true',
    '    fi',
    '',
    '    if [[ -d "$user_home/.npm-global" ]]; then',
    '        find "$user_home/.npm-global" -maxdepth 8 -name "claude" \( -type f -o -type l \) 2>/dev/null >> "$out_file" || true',
    '    fi',
    '',
    '    if [[ -d "$user_home/.local" ]]; then',
    '        find "$user_home/.local" -maxdepth 8 -name "claude" \( -type f -o -type l \) 2>/dev/null >> "$out_file" || true',
    '    fi',
    '',
    '    add_if_exists "$user_home/.local/share/claude" "$out_file"',
    '',
    '    find "$user_home" -maxdepth 2 \( \',
    '        -name ".vscode" -o -name ".vscode-insiders" -o -name ".vscode-server" \',
    '        -o -name ".cursor" -o -name ".windsurf" \',
    '        \) -type d 2>/dev/null | while IFS= read -r ext_root; do',
    '        [[ -d "$ext_root/extensions" ]] || continue',
    '        find "$ext_root/extensions" -maxdepth 1 -name "anthropic.claude-code*" -type d 2>/dev/null >> "$out_file" || true',
    '    done',
    '}',
    '',
    'find_targets() {',
    '    local out_file="$1"',
    '    : > "$out_file"',
    '',
    '    if [[ ! -d "$SEARCH_BASE" ]]; then',
    '        echo "Search path does not exist or is not a directory: $SEARCH_BASE" >&2',
    '        return 2',
    '    fi',
    '',
    '    echo "Searching for Claude Code artifacts under: $SEARCH_BASE"',
    '    shopt -s nullglob',
    '    for user_home in "$SEARCH_BASE"/*/; do',
    '        find_for_home "${user_home%/}" "$out_file"',
    '    done',
    '    shopt -u nullglob',
    '',
    '    sort -u "$out_file" -o "$out_file"',
    '}',
    '',
    'print_list() {',
    '    local list_file="$1"',
    '    local count',
    '    count=$(wc -l < "$list_file" 2>/dev/null || echo 0)',
    '',
    '    if [[ "$count" -eq 0 ]]; then',
    '        echo "No Claude Code files or directories found."',
    '        return 0',
    '    fi',
    '',
    '    echo "Found $count item(s):"',
    '    while IFS= read -r item; do',
    '        if [[ -d "$item" && ! -L "$item" ]]; then',
    '            echo "  [dir]  $item"',
    '        elif [[ -L "$item" ]]; then',
    '            echo "  [link] $item -> $(readlink "$item" 2>/dev/null || true)"',
    '        elif [[ -f "$item" ]]; then',
    '            echo "  [file] $item"',
    '        else',
    '            echo "  [gone] $item"',
    '        fi',
    '    done < "$list_file"',
    '}',
    '',
    'perform_deletion() {',
    '    local list_file="$1"',
    '    local deleted=0',
    '    local failed=0',
    '    local skipped=0',
    '',
    '    while IFS= read -r item; do',
    '        [[ -n "$item" ]] || continue',
    '',
    '        if [[ -L "$item" ]]; then',
    '            target=$(readlink -f "$item" 2>/dev/null || true)',
    '            if rm -f "$item"; then',
    '                echo "  Deleted link: $item"',
    '                (( deleted++ )) || true',
    '            else',
    '                echo "  FAILED link:  $item"',
    '                (( failed++ )) || true',
    '            fi',
    '',
    '            if [[ -n "${target:-}" && -e "$target" ]]; then',
    '                if rm -rf "$target"; then',
    '                    echo "  Deleted target: $target"',
    '                    (( deleted++ )) || true',
    '                else',
    '                    echo "  FAILED target:  $target"',
    '                    (( failed++ )) || true',
    '                fi',
    '            fi',
    '        elif [[ -d "$item" ]]; then',
    '            if rm -rf "$item"; then',
    '                echo "  Deleted dir:  $item"',
    '                (( deleted++ )) || true',
    '            else',
    '                echo "  FAILED dir:   $item"',
    '                (( failed++ )) || true',
    '            fi',
    '        elif [[ -f "$item" ]]; then',
    '            if rm -f "$item"; then',
    '                echo "  Deleted file: $item"',
    '                (( deleted++ )) || true',
    '            else',
    '                echo "  FAILED file:  $item"',
    '                (( failed++ )) || true',
    '            fi',
    '        else',
    '            echo "  Skipped missing item: $item"',
    '            (( skipped++ )) || true',
    '        fi',
    '    done < "$list_file"',
    '',
    '    echo "Deletion complete. Deleted: $deleted  Failed: $failed  Skipped: $skipped"',
    '',
    '    if [[ "$failed" -gt 0 ]]; then',
    '        return 1',
    '    fi',
    '}',
    '',
    'find_targets "$OUTPUT_FILE"',
    'print_list "$OUTPUT_FILE"',
    'echo "List saved to: $OUTPUT_FILE"',
    'perform_deletion "$OUTPUT_FILE"'
)
$EmbeddedRemovalScript = $EmbeddedRemovalScriptLines -join [Environment]::NewLine

function Write-Status {
    param([string]$Message)
    $line = "[claude-removal-wsl-inline-delete-all] $Message"
    [void]$Script:OutputBuffer.Add($line)

    $logPath = [Environment]::GetEnvironmentVariable('CLAUDE_REMOVAL_WSL_LOG')
    if (-not [string]::IsNullOrWhiteSpace($logPath)) {
        try {
            [IO.File]::AppendAllText($logPath, $line + [Environment]::NewLine, [Text.Encoding]::UTF8)
        }
        catch {
            [Console]::Error.WriteLine("[claude-removal-wsl-inline-delete-all] Failed to write status log: $($_.Exception.Message)")
        }
    }
}

function Write-ChildOutput {
    param([string]$Message)

    [void]$Script:OutputBuffer.Add($Message)

    $logPath = [Environment]::GetEnvironmentVariable('CLAUDE_REMOVAL_WSL_LOG')
    if (-not [string]::IsNullOrWhiteSpace($logPath)) {
        try {
            [IO.File]::AppendAllText($logPath, $Message + [Environment]::NewLine, [Text.Encoding]::UTF8)
        }
        catch {
            [Console]::Error.WriteLine("[claude-removal-wsl-inline-delete-all] Failed to write child output log: $($_.Exception.Message)")
        }
    }
}

function Write-ParentStatus {
    param([string]$Message)
    [void]$Script:OutputBuffer.Add("[claude-removal-wsl-inline-delete-all] $Message")
}

function Write-ParentOutput {
    param([string]$Message)
    [void]$Script:OutputBuffer.Add($Message)
}

function Flush-OutputBuffer {
    foreach ($line in $Script:OutputBuffer) {
        Write-Output $line
    }
    $Script:OutputBuffer.Clear()
}

function Read-LogLinesShared {
    param([string]$LogPath)

    if (-not [IO.File]::Exists($LogPath)) { return @() }

    $stream = $null
    $reader = $null
    try {
        $stream = New-Object IO.FileStream($LogPath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
        $reader = New-Object IO.StreamReader($stream, [Text.Encoding]::UTF8, $true)
        $text = $reader.ReadToEnd()
        if ([string]::IsNullOrEmpty($text)) { return @() }
        return @($text -split "`r?`n" | Where-Object { $_ -ne '' })
    }
    catch {
        return @("[parent] Unable to read child log while it is open: $($_.Exception.Message)")
    }
    finally {
        if ($reader) { $reader.Close() }
        elseif ($stream) { $stream.Close() }
    }
}

function Normalize-WslOutputLine {
    param([string]$Line)
    return (($Line -replace "`0", '') -replace '^\s*\*\s*', '').Trim()
}

function Test-RunningAsSystem {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    return ($identity.User.Value -eq 'S-1-5-18')
}

function ConvertTo-PowerShellLiteral {
    param([string]$Value)
    return "'$($Value -replace "'", "''")'"
}

function Get-NativePowerShellPath {
    $sysnative = Join-Path -Path $env:WINDIR -ChildPath 'Sysnative\WindowsPowerShell\v1.0\powershell.exe'
    $system32 = Join-Path -Path $env:WINDIR -ChildPath 'System32\WindowsPowerShell\v1.0\powershell.exe'

    if ([IO.File]::Exists($sysnative)) { return $sysnative }
    if ([IO.File]::Exists($system32)) { return $system32 }

    return 'powershell.exe'
}

function Grant-UsersModifyAccess {
    param([string]$TargetPath)

    $icaclsPath = Join-Path -Path $env:WINDIR -ChildPath 'Sysnative\icacls.exe'
    if (-not [IO.File]::Exists($icaclsPath)) {
        $icaclsPath = Join-Path -Path $env:WINDIR -ChildPath 'System32\icacls.exe'
    }
    if (-not [IO.File]::Exists($icaclsPath)) {
        throw 'icacls.exe was not found on this host.'
    }

    $output = & $icaclsPath $TargetPath /grant '*S-1-5-32-545:(M)' /Q 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to grant Users modify access to '$TargetPath'. icacls.exe returned exit code $LASTEXITCODE. Output: $($output -join ' ')"
    }
}

function Add-UserSessionProcessApi {
    if ('UserSessionProcess.NativeMethods' -as [type]) { return }

    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

namespace UserSessionProcess
{
    public enum WTS_CONNECTSTATE_CLASS
    {
        WTSActive = 0,
        WTSConnected = 1,
        WTSConnectQuery = 2,
        WTSShadow = 3,
        WTSDisconnected = 4,
        WTSIdle = 5,
        WTSListen = 6,
        WTSReset = 7,
        WTSDown = 8,
        WTSInit = 9
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct WTS_SESSION_INFO
    {
        public Int32 SessionID;
        public IntPtr pWinStationName;
        public WTS_CONNECTSTATE_CLASS State;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct STARTUPINFO
    {
        public Int32 cb;
        public string lpReserved;
        public string lpDesktop;
        public string lpTitle;
        public Int32 dwX;
        public Int32 dwY;
        public Int32 dwXSize;
        public Int32 dwYSize;
        public Int32 dwXCountChars;
        public Int32 dwYCountChars;
        public Int32 dwFillAttribute;
        public Int32 dwFlags;
        public Int16 wShowWindow;
        public Int16 cbReserved2;
        public IntPtr lpReserved2;
        public IntPtr hStdInput;
        public IntPtr hStdOutput;
        public IntPtr hStdError;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct PROCESS_INFORMATION
    {
        public IntPtr hProcess;
        public IntPtr hThread;
        public Int32 dwProcessId;
        public Int32 dwThreadId;
    }

    public static class NativeMethods
    {
        public const UInt32 CREATE_NO_WINDOW = 0x08000000;
        public const UInt32 CREATE_UNICODE_ENVIRONMENT = 0x00000400;
        public const UInt32 WAIT_TIMEOUT = 0x00000102;

        [DllImport("wtsapi32.dll", SetLastError = true)]
        public static extern bool WTSEnumerateSessions(
            IntPtr hServer,
            Int32 Reserved,
            Int32 Version,
            out IntPtr ppSessionInfo,
            out Int32 pCount);

        [DllImport("wtsapi32.dll")]
        public static extern void WTSFreeMemory(IntPtr pMemory);

        [DllImport("wtsapi32.dll", SetLastError = true)]
        public static extern bool WTSQueryUserToken(UInt32 sessionId, out IntPtr Token);

        [DllImport("userenv.dll", SetLastError = true)]
        public static extern bool CreateEnvironmentBlock(out IntPtr lpEnvironment, IntPtr hToken, bool bInherit);

        [DllImport("userenv.dll", SetLastError = true)]
        public static extern bool DestroyEnvironmentBlock(IntPtr lpEnvironment);

        [DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
        public static extern bool CreateProcessAsUser(
            IntPtr hToken,
            string lpApplicationName,
            string lpCommandLine,
            IntPtr lpProcessAttributes,
            IntPtr lpThreadAttributes,
            bool bInheritHandles,
            UInt32 dwCreationFlags,
            IntPtr lpEnvironment,
            string lpCurrentDirectory,
            ref STARTUPINFO lpStartupInfo,
            out PROCESS_INFORMATION lpProcessInformation);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool GetExitCodeProcess(IntPtr hProcess, out UInt32 lpExitCode);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool TerminateProcess(IntPtr hProcess, UInt32 uExitCode);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool CloseHandle(IntPtr hObject);
    }
}
'@
}

function Get-InteractiveSessionIds {
    Add-UserSessionProcessApi

    $sessionInfoPtr = [IntPtr]::Zero
    $sessionCount = 0
    $sessions = @()

    $ok = [UserSessionProcess.NativeMethods]::WTSEnumerateSessions([IntPtr]::Zero, 0, 1, [ref]$sessionInfoPtr, [ref]$sessionCount)
    if (-not $ok) {
        $errorCode = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
        throw "Unable to enumerate Windows logon sessions. Win32 error: $errorCode"
    }

    try {
        $structSize = [Runtime.InteropServices.Marshal]::SizeOf([type][UserSessionProcess.WTS_SESSION_INFO])
        for ($i = 0; $i -lt $sessionCount; $i++) {
            $currentPtr = [IntPtr]::Add($sessionInfoPtr, $i * $structSize)
            $session = [Runtime.InteropServices.Marshal]::PtrToStructure($currentPtr, [type][UserSessionProcess.WTS_SESSION_INFO])
            if ($session.State -in @([UserSessionProcess.WTS_CONNECTSTATE_CLASS]::WTSActive, [UserSessionProcess.WTS_CONNECTSTATE_CLASS]::WTSConnected)) {
                $sessions += [int]$session.SessionID
            }
        }
    }
    finally {
        if ($sessionInfoPtr -ne [IntPtr]::Zero) {
            [UserSessionProcess.NativeMethods]::WTSFreeMemory($sessionInfoPtr)
        }
    }

    return $sessions | Sort-Object -Unique
}

function Get-RunningWslDistributions {
    Write-Status 'Listing running WSL distributions visible to this Windows user context.'
    Write-Status 'Running command: wsl.exe --list --running --quiet'
    $raw = & wsl.exe --list --running --quiet 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to list running WSL distributions. wsl.exe returned exit code $LASTEXITCODE. Output: $($raw -join ' ')"
    }

    $distros = @()
    foreach ($line in $raw) {
        $clean = Normalize-WslOutputLine -Line $line
        if ([string]::IsNullOrWhiteSpace($clean)) { continue }
        if ($clean -match '^Windows Subsystem for Linux') { continue }
        $distros += $clean
    }

    $uniqueDistros = @($distros | Sort-Object -Unique)
    Write-Status "Running WSL distro count visible to this context: $($uniqueDistros.Count)"
    return $uniqueDistros
}

function Invoke-WslInlineBashWithTimeout {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DistroName,

        [Parameter(Mandatory = $true)]
        [string]$BashCommand,

        [int]$TimeoutSeconds = 60
    )

    $safeDistroName = ($DistroName -replace '[^A-Za-z0-9_.-]', '_')
    $stdoutPath = Join-Path -Path $env:TEMP -ChildPath "claude_wsl_${safeDistroName}_stdout_$([Guid]::NewGuid().ToString('N')).log"
    $stderrPath = Join-Path -Path $env:TEMP -ChildPath "claude_wsl_${safeDistroName}_stderr_$([Guid]::NewGuid().ToString('N')).log"
    $bashPath = Join-Path -Path $env:ProgramData -ChildPath "claude_removal_wsl_inline_${safeDistroName}_$([Guid]::NewGuid().ToString('N')).sh"

    $bashText = ($BashCommand -replace "`r`n", "`n") -replace "`r", "`n"
    $utf8NoBom = New-Object Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($bashPath, $bashText, $utf8NoBom)

    $fullBashPath = [IO.Path]::GetFullPath($bashPath)
    $driveLetter = $fullBashPath.Substring(0, 1).ToLowerInvariant()
    $pathRemainder = $fullBashPath.Substring(2).Replace('\', '/')
    $wslBashPath = "/mnt/$driveLetter$pathRemainder"

    $argList = @('-d', $DistroName, '-u', 'root', '--', 'bash', $wslBashPath)
    Write-Status "Wrote temporary Windows-host Bash file: $bashPath"
    Write-Status "Starting wsl.exe process for distro '$DistroName' with timeout ${TimeoutSeconds}s."
    Write-Status "Running command: wsl.exe -d $DistroName -u root -- bash $wslBashPath"
    $process = Start-Process -FilePath 'wsl.exe' -ArgumentList $argList -NoNewWindow -PassThru -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath

    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        Start-Sleep -Seconds 2
    }

    if (-not $process.HasExited) {
        try { $process.Kill() } catch { }
        Write-ChildOutput "[$DistroName] Timed out after ${TimeoutSeconds}s while running inline Bash cleanup."
        if ([IO.File]::Exists($stdoutPath)) {
            Read-LogLinesShared -LogPath $stdoutPath | ForEach-Object { Write-ChildOutput "[$DistroName] $_" }
        }
        if ([IO.File]::Exists($stderrPath)) {
            Read-LogLinesShared -LogPath $stderrPath | ForEach-Object { Write-ChildOutput "[$DistroName] STDERR: $_" }
        }
        if ([IO.File]::Exists($bashPath)) {
            Remove-Item -Path $bashPath -Force -ErrorAction SilentlyContinue
        }
        return [PSCustomObject]@{ ExitCode = 124; TimedOut = $true }
    }

    if ([IO.File]::Exists($stdoutPath)) {
        Read-LogLinesShared -LogPath $stdoutPath | ForEach-Object { Write-ChildOutput "[$DistroName] $_" }
        Remove-Item -Path $stdoutPath -Force -ErrorAction SilentlyContinue
    }
    if ([IO.File]::Exists($stderrPath)) {
        Read-LogLinesShared -LogPath $stderrPath | ForEach-Object { Write-ChildOutput "[$DistroName] STDERR: $_" }
        Remove-Item -Path $stderrPath -Force -ErrorAction SilentlyContinue
    }
    if ([IO.File]::Exists($bashPath)) {
        Remove-Item -Path $bashPath -Force -ErrorAction SilentlyContinue
    }

    return [PSCustomObject]@{ ExitCode = [int]$process.ExitCode; TimedOut = $false }
}

function Invoke-InlineRemovalForVisibleWslDistros {
    Write-Status 'Starting inline WSL removal workflow in user context.'
    $runningDistros = @(Get-RunningWslDistributions)
    if ($runningDistros.Count -eq 0) {
        Write-Status 'No running WSL distributions found. No action taken.'
        return 0
    }

    $overallFailures = 0
    Write-Status 'Mode: Delete'
    Write-Status 'Search path inside WSL: /home'
    Write-Status "Target running distro(s): $($runningDistros -join ', ')"

    foreach ($target in $runningDistros) {
        Write-Status "Processing distro: $target"
        Write-Status "Executing inline Bash cleanup as root in WSL distro: $target"

        $runResult = Invoke-WslInlineBashWithTimeout -DistroName $target -BashCommand $EmbeddedRemovalScript -TimeoutSeconds 60
        if ($runResult.ExitCode -ne 0) {
            $overallFailures++
            Write-ChildOutput "[$target] Inline Bash cleanup failed with exit code $($runResult.ExitCode)."
        }
        else {
            Write-Status "Completed distro successfully: $target"
        }
    }

    if ($overallFailures -gt 0) { return 1 }
    return 0
}

function Invoke-SelfInUserSession {
    param(
        [Parameter(Mandatory = $true)]
        [int]$SessionId
    )

    Add-UserSessionProcessApi

    $token = [IntPtr]::Zero
    $environment = [IntPtr]::Zero
    $processInfo = New-Object UserSessionProcess.PROCESS_INFORMATION
    $scriptPath = $null
    $logPath = $null
    $launcherPath = $null
    $preserveDebugFiles = $false
    $logLineOffset = 0

    $tokenOk = [UserSessionProcess.NativeMethods]::WTSQueryUserToken([uint32]$SessionId, [ref]$token)
    if (-not $tokenOk) {
        $errorCode = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
        throw "Unable to query user token for session $SessionId. Win32 error: $errorCode"
    }

    try {
        [void][UserSessionProcess.NativeMethods]::CreateEnvironmentBlock([ref]$environment, $token, $false)

        $scriptPath = Join-Path -Path $env:ProgramData -ChildPath "claude_removal_wsl_inline_delete_all_child_session_${SessionId}.ps1"
        Write-ParentStatus "Preparing user-session child script for Windows session $SessionId at: $scriptPath"
        if (-not [string]::IsNullOrWhiteSpace($Script:CurrentScriptPath) -and [IO.File]::Exists($Script:CurrentScriptPath)) {
            Copy-Item -Path $Script:CurrentScriptPath -Destination $scriptPath -Force
        }
        elseif (-not [string]::IsNullOrWhiteSpace($Script:CurrentScriptText)) {
            [IO.File]::WriteAllText($scriptPath, $Script:CurrentScriptText, [Text.Encoding]::UTF8)
        }
        else {
            throw 'Unable to determine current script content for user-session launch.'
        }
        Grant-UsersModifyAccess -TargetPath $scriptPath

        $logPath = Join-Path -Path $env:ProgramData -ChildPath "claude_removal_wsl_inline_delete_all_session_${SessionId}.log"
        [IO.File]::WriteAllText($logPath, '', [Text.Encoding]::UTF8)
        Grant-UsersModifyAccess -TargetPath $logPath
        Write-ParentStatus "Child process log for Windows session ${SessionId}: $logPath"

        $launcherPath = Join-Path -Path $env:ProgramData -ChildPath "claude_removal_wsl_inline_delete_all_launcher_session_${SessionId}.ps1"
        $scriptLiteral = ConvertTo-PowerShellLiteral -Value $scriptPath
        $logLiteral = ConvertTo-PowerShellLiteral -Value $logPath
        $launcherLines = @(
            '$ErrorActionPreference = ''Stop''',
            '$ProgressPreference = ''SilentlyContinue''',
            "`$logPath = $logLiteral",
            "`$scriptPath = $scriptLiteral",
            'try {',
            '    "[child] Starting at $(Get-Date -Format o)" | Out-File -FilePath $logPath -Encoding UTF8 -Append',
            '    "[child] User: $([Security.Principal.WindowsIdentity]::GetCurrent().Name)" | Out-File -FilePath $logPath -Encoding UTF8 -Append',
            '    "[child] Script: $scriptPath" | Out-File -FilePath $logPath -Encoding UTF8 -Append',
            '    if (-not [IO.File]::Exists($scriptPath)) { throw "Child script not found: $scriptPath" }',
            '    [Environment]::SetEnvironmentVariable("CLAUDE_REMOVAL_WSL_LOG", $logPath, "Process")',
            '    & $scriptPath',
            '    $exitCode = $LASTEXITCODE',
            '    if ($null -eq $exitCode) { $exitCode = 0 }',
            '    "[child] Completed with exit code $exitCode at $(Get-Date -Format o)" | Out-File -FilePath $logPath -Encoding UTF8 -Append',
            '    exit $exitCode',
            '}',
            'catch {',
            '    "[child] ERROR: $($_.Exception.Message)" | Out-File -FilePath $logPath -Encoding UTF8 -Append',
            '    "[child] ERROR TYPE: $($_.Exception.GetType().FullName)" | Out-File -FilePath $logPath -Encoding UTF8 -Append',
            '    "[child] SCRIPT STACK: $($_.ScriptStackTrace)" | Out-File -FilePath $logPath -Encoding UTF8 -Append',
            '    exit 1',
            '}'
        )
        [IO.File]::WriteAllText($launcherPath, ($launcherLines -join [Environment]::NewLine), [Text.Encoding]::UTF8)
        Grant-UsersModifyAccess -TargetPath $launcherPath
        Write-ParentStatus "Child process launcher for Windows session ${SessionId}: $launcherPath"
        $powerShellPath = Get-NativePowerShellPath
        $commandLine = "`"$powerShellPath`" -NoProfile -ExecutionPolicy Bypass -File `"$launcherPath`""

        $startupInfo = New-Object UserSessionProcess.STARTUPINFO
        $startupInfo.cb = [Runtime.InteropServices.Marshal]::SizeOf([type][UserSessionProcess.STARTUPINFO])
        $startupInfo.lpDesktop = 'winsta0\default'

        $creationFlags = [UserSessionProcess.NativeMethods]::CREATE_NO_WINDOW -bor [UserSessionProcess.NativeMethods]::CREATE_UNICODE_ENVIRONMENT
        $created = [UserSessionProcess.NativeMethods]::CreateProcessAsUser(
            $token,
            $powerShellPath,
            $commandLine,
            [IntPtr]::Zero,
            [IntPtr]::Zero,
            $false,
            $creationFlags,
            $environment,
            (Split-Path -Parent $scriptPath),
            [ref]$startupInfo,
            [ref]$processInfo)

        if (-not $created) {
            $errorCode = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
            throw "Unable to launch script in session $SessionId. Win32 error: $errorCode"
        }
        Write-ParentStatus "Launched child process $($processInfo.dwProcessId) in Windows session $SessionId. Waiting up to $($Script:ChildTimeoutSeconds) seconds."

        $timeoutMilliseconds = [uint32]($Script:ChildTimeoutSeconds * 1000)
        $deadline = [DateTime]::UtcNow.AddSeconds($Script:ChildTimeoutSeconds)
        $waitResult = [uint32]0
        do {
            $waitResult = [UserSessionProcess.NativeMethods]::WaitForSingleObject($processInfo.hProcess, 2000)
            if ([IO.File]::Exists($logPath)) {
                $logLines = @(Read-LogLinesShared -LogPath $logPath)
                if ($logLines.Count -gt $logLineOffset) {
                    for ($i = $logLineOffset; $i -lt $logLines.Count; $i++) {
                        Write-ParentOutput "[session $SessionId] $($logLines[$i])"
                    }
                    $logLineOffset = $logLines.Count
                }
            }
        } while (($waitResult -eq [UserSessionProcess.NativeMethods]::WAIT_TIMEOUT) -and ([DateTime]::UtcNow -lt $deadline))

        if ($waitResult -eq [UserSessionProcess.NativeMethods]::WAIT_TIMEOUT) {
            [void][UserSessionProcess.NativeMethods]::TerminateProcess($processInfo.hProcess, 124)
            if ([IO.File]::Exists($logPath)) {
                $logLines = @(Read-LogLinesShared -LogPath $logPath)
                if ($logLines.Count -gt $logLineOffset) {
                    for ($i = $logLineOffset; $i -lt $logLines.Count; $i++) {
                        Write-ParentOutput "[session $SessionId] $($logLines[$i])"
                    }
                }
            }
            throw "User-context cleanup timed out after $($Script:ChildTimeoutSeconds) seconds in session $SessionId."
        }

        $exitCode = 0
        [void][UserSessionProcess.NativeMethods]::GetExitCodeProcess($processInfo.hProcess, [ref]$exitCode)
        if ([int]$exitCode -ne 0) {
            $preserveDebugFiles = $true
            Write-ParentStatus "Child process exited with code $exitCode. Preserving debug files: $launcherPath ; $scriptPath ; $logPath"
        }

        if ([IO.File]::Exists($logPath)) {
            $logLines = @(Read-LogLinesShared -LogPath $logPath)
            if ($logLines.Count -gt $logLineOffset) {
                for ($i = $logLineOffset; $i -lt $logLines.Count; $i++) {
                    Write-ParentOutput "[session $SessionId] $($logLines[$i])"
                }
            }
        }

        return [PSCustomObject]@{ ExitCode = [int]$exitCode }
    }
    finally {
        if ($logPath -and [IO.File]::Exists($logPath)) {
            if (-not $preserveDebugFiles) { Remove-Item -Path $logPath -Force -ErrorAction SilentlyContinue }
        }
        if ($scriptPath -and [IO.File]::Exists($scriptPath)) {
            if (-not $preserveDebugFiles) { Remove-Item -Path $scriptPath -Force -ErrorAction SilentlyContinue }
        }
        if ($launcherPath -and [IO.File]::Exists($launcherPath)) {
            if (-not $preserveDebugFiles) { Remove-Item -Path $launcherPath -Force -ErrorAction SilentlyContinue }
        }
        if ($processInfo.hThread -ne [IntPtr]::Zero) { [void][UserSessionProcess.NativeMethods]::CloseHandle($processInfo.hThread) }
        if ($processInfo.hProcess -ne [IntPtr]::Zero) { [void][UserSessionProcess.NativeMethods]::CloseHandle($processInfo.hProcess) }
        if ($environment -ne [IntPtr]::Zero) { [void][UserSessionProcess.NativeMethods]::DestroyEnvironmentBlock($environment) }
        if ($token -ne [IntPtr]::Zero) { [void][UserSessionProcess.NativeMethods]::CloseHandle($token) }
    }
}

function Invoke-SelfForLoggedOnUsersFromSystem {
    $sessionIds = @(Get-InteractiveSessionIds)
    if ($sessionIds.Count -eq 0) {
        Write-Status 'Running as SYSTEM, but no active logged-on user sessions were found. No action taken.'
        return 0
    }

    Write-Status "Running as SYSTEM. Launching user-context WSL cleanup in session(s): $($sessionIds -join ', ')"
    $failures = 0
    foreach ($sessionId in $sessionIds) {
        try {
            Write-Status "Launching user-context cleanup in Windows session $sessionId"
            $sessionResult = Invoke-SelfInUserSession -SessionId $sessionId
            if ($sessionResult.ExitCode -ne 0) {
                Write-Error "[session $sessionId] User-context cleanup exited with code $($sessionResult.ExitCode)."
                $failures++
            }
        }
        catch {
            Write-Error $_.Exception.Message
            $failures++
        }
    }

    if ($failures -gt 0) { return 1 }
    return 0
}

$startedAt = (Get-Date).ToUniversalTime().ToString('o')
$runningAsSystem = $null

try {
    $runningAsSystem = Test-RunningAsSystem

    Write-Status "Script version: $($Script:ScriptVersion)"
    if ($runningAsSystem) {
        $systemExitCode = Invoke-SelfForLoggedOnUsersFromSystem
        $result = if ($systemExitCode -eq 0) { 'success' } else { 'failure' }
        [PSCustomObject]@{
            result          = $result
            exitCode        = $systemExitCode
            hostname        = [System.Net.Dns]::GetHostName()
            computerName    = $env:COMPUTERNAME
            user            = [Security.Principal.WindowsIdentity]::GetCurrent().Name
            runningAsSystem = $runningAsSystem
            scriptVersion   = $Script:ScriptVersion
            startedAt       = $startedAt
            completedAt     = (Get-Date).ToUniversalTime().ToString('o')
            log             = @($Script:OutputBuffer)
            error           = $null
        } | ConvertTo-Json -Depth 8 -Compress
        $Script:OutputBuffer.Clear()
        exit $systemExitCode
    }

    if (-not (Get-Command -Name wsl.exe -ErrorAction SilentlyContinue)) {
        throw 'wsl.exe was not found on this host.'
    }

    $exitCode = Invoke-InlineRemovalForVisibleWslDistros
    if ($exitCode -ne 0) {
        Write-Status 'Completed with one or more failure(s).'
    }
    else {
        Write-Status 'Completed successfully.'
    }

    $result = if ($exitCode -eq 0) { 'success' } else { 'failure' }
    [PSCustomObject]@{
        result          = $result
        exitCode        = $exitCode
        hostname        = [System.Net.Dns]::GetHostName()
        computerName    = $env:COMPUTERNAME
        user            = [Security.Principal.WindowsIdentity]::GetCurrent().Name
        runningAsSystem = $runningAsSystem
        scriptVersion   = $Script:ScriptVersion
        startedAt       = $startedAt
        completedAt     = (Get-Date).ToUniversalTime().ToString('o')
        log             = @($Script:OutputBuffer)
        error           = $null
    } | ConvertTo-Json -Depth 8 -Compress
    $Script:OutputBuffer.Clear()
    exit $exitCode
}
catch {
    Write-Status "ERROR: $($_.Exception.Message)"
    [PSCustomObject]@{
        result          = 'error'
        exitCode        = 1
        hostname        = [System.Net.Dns]::GetHostName()
        computerName    = $env:COMPUTERNAME
        user            = [Security.Principal.WindowsIdentity]::GetCurrent().Name
        runningAsSystem = $runningAsSystem
        scriptVersion   = $Script:ScriptVersion
        startedAt       = $startedAt
        completedAt     = (Get-Date).ToUniversalTime().ToString('o')
        log             = @($Script:OutputBuffer)
        error           = $_.Exception.Message
    } | ConvertTo-Json -Depth 8 -Compress
    $Script:OutputBuffer.Clear()
    exit 1
}
