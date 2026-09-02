[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$filePattern = 'claude_removal_list_*.txt'
$outputDirectory = 'C:\temp'
$outputPath = Join-Path -Path $outputDirectory -ChildPath "get_remediation_results_$([Guid]::NewGuid().ToString('N')).txt"
$scriptExitCode = 0

# Create the result file before doing WSL work so failures are captured in a
# predictable location for collection tooling.
New-Item -Path $outputDirectory -ItemType Directory -Force | Out-Null
New-Item -Path $outputPath -ItemType File -Force | Out-Null

function Write-ResultLine {
    param([string]$Message)

    Write-Output $Message
    Add-Content -Path $outputPath -Encoding UTF8 -Value $Message
}

try {
    Write-ResultLine "[get-remediation-results] Started: $(Get-Date -Format o)"
    Write-ResultLine "[get-remediation-results] Windows result file: $outputPath"
    Write-ResultLine "[get-remediation-results] Target WSL file pattern: /tmp/$filePattern"

    if (-not (Get-Command -Name wsl.exe -ErrorAction SilentlyContinue)) {
        throw 'wsl.exe was not found on this host.'
    }

    $rawDistros = & wsl.exe --list --running --quiet 2>&1
    $wslListExitCode = $LASTEXITCODE
    Write-ResultLine "[get-remediation-results] wsl.exe --list --running --quiet exit code: $wslListExitCode"

    if ($wslListExitCode -ne 0) {
        throw "Unable to list running WSL distributions. Output: $($rawDistros -join ' ')"
    }

    $runningDistros = @(
        $rawDistros |
            ForEach-Object { (($_ -replace "`0", '') -replace '^\s*\*\s*', '').Trim() } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
            Where-Object { $_ -notmatch '^Windows Subsystem for Linux' } |
            Sort-Object -Unique
    )

    Write-ResultLine "[get-remediation-results] Running WSL distro count: $($runningDistros.Count)"

    if ($runningDistros.Count -eq 0) {
        Write-ResultLine '[get-remediation-results] No running WSL distributions found. No action taken.'
    }

    foreach ($distro in $runningDistros) {
        $foundDistroRoot = $false
        $foundFiles = $false

        Write-ResultLine "[get-remediation-results] Processing WSL distro: $distro"

        foreach ($rootPrefix in @('\\wsl$', '\\wsl.localhost')) {
            $tmpPath = Join-Path -Path "$rootPrefix\$distro" -ChildPath 'tmp'
            Write-ResultLine "[get-remediation-results] Checking path: $tmpPath"

            try {
                if (-not (Test-Path -LiteralPath $tmpPath -PathType Container)) {
                    Write-ResultLine "[get-remediation-results] Path not accessible: $tmpPath"
                    continue
                }

                $foundDistroRoot = $true
                Write-ResultLine "[get-remediation-results] Reading $filePattern from: $tmpPath"

                $matchingFiles = @(
                    Get-ChildItem -LiteralPath $tmpPath -Filter $filePattern -File -ErrorAction Stop |
                        Sort-Object -Property FullName
                )

                Write-ResultLine "[get-remediation-results] Matching file count for ${distro}: $($matchingFiles.Count)"

                foreach ($file in $matchingFiles) {
                    $foundFiles = $true
                    Write-ResultLine "===== BEGIN $($file.FullName) ====="

                    try {
                        Get-Content -LiteralPath $file.FullName -ErrorAction Stop |
                            ForEach-Object { Write-ResultLine $_ }
                    }
                    catch {
                        $scriptExitCode = 1
                        Write-ResultLine "[get-remediation-results] ERROR: Failed to read '$($file.FullName)': $($_.Exception.Message)"
                    }

                    Write-ResultLine "===== END $($file.FullName) ====="
                }

                if (-not $foundFiles) {
                    Write-ResultLine "[get-remediation-results] No remediation result files found matching $filePattern in $tmpPath"
                }

                break
            }
            catch {
                Write-ResultLine "[get-remediation-results] ERROR: Failed while checking '$tmpPath': $($_.Exception.Message)"
            }
        }

        if (-not $foundDistroRoot) {
            $scriptExitCode = 1
            Write-ResultLine "[get-remediation-results] ERROR: Unable to access distro '$distro' through \\wsl$ or \\wsl.localhost."
        }
    }
}
catch {
    $scriptExitCode = 1
    Write-ResultLine "[get-remediation-results] ERROR: $($_.Exception.Message)"
}
finally {
    Write-ResultLine "[get-remediation-results] Finished: $(Get-Date -Format o)"
    Write-ResultLine "[get-remediation-results] Final exit code: $scriptExitCode"
    Write-ResultLine "[get-remediation-results] Windows result file: $outputPath"
}

exit $scriptExitCode
