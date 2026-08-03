param(
    [string]$Source,
    [string]$Project = $PSScriptRoot,
    [int]$IntervalSeconds = 20
)

$ErrorActionPreference = "Stop"

if (-not $Source) {
    $Source = Join-Path 'E:\Labelme' ('3' + ([char]0x5362) + ([char]0x6770))
}
$LogPath = Join-Path $Project "watch_labelme.log"
$SyncScript = Join-Path $Project "sync_from_labelme.ps1"

function Write-Log($Message) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
    Write-Host $line
}

function Get-State {
    $files = Get-ChildItem -LiteralPath $Source -File -Filter "*.json" | Sort-Object FullName
    if (-not $files) {
        return "empty"
    }

    return ($files | ForEach-Object {
        "$($_.Name)|$($_.Length)|$($_.LastWriteTimeUtc.Ticks)"
    }) -join "`n"
}

Write-Log "Watcher started. Source=$Source Project=$Project Interval=${IntervalSeconds}s"
$lastState = Get-State

while ($true) {
    Start-Sleep -Seconds $IntervalSeconds
    $currentState = Get-State

    if ($currentState -eq $lastState) {
        continue
    }

    Write-Log "JSON change detected. Syncing..."
    try {
        powershell -NoProfile -ExecutionPolicy Bypass -File $SyncScript -Source $Source -Project $Project *>> $LogPath
        $lastState = Get-State
        Write-Log "Sync finished."
    } catch {
        Write-Log "Sync failed: $($_.Exception.Message)"
    }
}
