[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$embeddedBash = @'
set -euo pipefail

output_file="$1"
distro_name="$2"
found=0

{
    echo "[cat-wsl-remediation-results] WSL distro: $distro_name"

    # Match the result-list files written by the Claude WSL remediation scripts.
    # If the glob does not match, Bash leaves the literal pattern in place, so
    # each candidate is tested before it is read.
    for result_file in /tmp/claude_removal_list_*.txt; do
        if [[ -e "$result_file" && -f "$result_file" ]]; then
            found=1
            echo "===== BEGIN $result_file ====="
            cat "$result_file"
            echo
            echo "===== END $result_file ====="
        fi
    done

    if [[ "$found" -eq 0 ]]; then
        echo "No remediation result files found matching /tmp/claude_removal_list_*.txt"
    fi

    echo
} >> "$output_file"
'@

if (-not (Get-Command -Name wsl.exe -ErrorAction SilentlyContinue)) {
    throw 'wsl.exe was not found on this host.'
}

$rawDistros = & wsl.exe --list --running --quiet 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Unable to list running WSL distributions. wsl.exe returned exit code $LASTEXITCODE. Output: $($rawDistros -join ' ')"
}

$runningDistros = @(
    $rawDistros |
        ForEach-Object { (($_ -replace "`0", '') -replace '^\s*\*\s*', '').Trim() } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Where-Object { $_ -notmatch '^Windows Subsystem for Linux' } |
        Sort-Object -Unique
)

if ($runningDistros.Count -eq 0) {
    Write-Output '[cat-wsl-remediation-results] No running WSL distributions found. No action taken.'
    exit 0
}

$tempBashPath = Join-Path -Path $env:TEMP -ChildPath "cat_wsl_remediation_results_$([Guid]::NewGuid().ToString('N')).sh"
$windowsOutputPath = Join-Path -Path $env:TEMP -ChildPath "cat_wsl_remediation_results_$([Guid]::NewGuid().ToString('N')).txt"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$bashText = ($embeddedBash -replace "`r`n", "`n") -replace "`r", "`n"
[IO.File]::WriteAllText($tempBashPath, $bashText, $utf8NoBom)
[IO.File]::WriteAllText($windowsOutputPath, '', $utf8NoBom)

$fullTempBashPath = [IO.Path]::GetFullPath($tempBashPath)
$driveLetter = $fullTempBashPath.Substring(0, 1).ToLowerInvariant()
$pathRemainder = $fullTempBashPath.Substring(2).Replace('\', '/')
$wslBashPath = "/mnt/$driveLetter$pathRemainder"

$fullWindowsOutputPath = [IO.Path]::GetFullPath($windowsOutputPath)
$outputDriveLetter = $fullWindowsOutputPath.Substring(0, 1).ToLowerInvariant()
$outputPathRemainder = $fullWindowsOutputPath.Substring(2).Replace('\', '/')
$wslOutputPath = "/mnt/$outputDriveLetter$outputPathRemainder"

$overallFailures = 0

try {
    foreach ($distro in $runningDistros) {
        Write-Output "[cat-wsl-remediation-results] Copying /tmp/claude_removal_list_*.txt from WSL distro '$distro' into: $windowsOutputPath"

        $output = & wsl.exe -d $distro -u root -- bash $wslBashPath $wslOutputPath $distro 2>&1
        $exitCode = $LASTEXITCODE

        foreach ($line in $output) {
            Write-Output "[$distro] $line"
        }

        if ($exitCode -ne 0) {
            $overallFailures++
            Write-Output "[$distro] ERROR: Failed to read remediation result files. Exit code: $exitCode"
        }
    }
}
finally {
    Remove-Item -Path $tempBashPath -Force -ErrorAction SilentlyContinue
}

Write-Output "[cat-wsl-remediation-results] Windows result file: $windowsOutputPath"

try {
    if ([IO.File]::Exists($windowsOutputPath)) {
        Write-Output '[cat-wsl-remediation-results] Result file contents:'
        Get-Content -Path $windowsOutputPath -ErrorAction Stop | ForEach-Object { Write-Output $_ }
    }
    else {
        Write-Output '[cat-wsl-remediation-results] Result file was not created.'
    }
}
catch {
    Write-Output "[cat-wsl-remediation-results] Unable to print result file contents: $($_.Exception.Message)"
}

if ($overallFailures -gt 0) {
    exit 1
}

exit 0
