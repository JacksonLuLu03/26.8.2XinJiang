param(
    [string]$Source,
    [string]$Project = $PSScriptRoot,
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"

function Resolve-Git {
    $command = Get-Command git -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidates = @(
        "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe",
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files\Git\bin\git.exe",
        "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    throw "Cannot find git.exe. Install Git for Windows or add git to PATH."
}

if (-not $Source) {
    $Source = Join-Path 'E:\Labelme' ('3' + ([char]0x5362) + ([char]0x6770))
}

$Git = Resolve-Git
$ImagesDir = Join-Path $Project "images"
$AnnotationsDir = Join-Path $Project "annotations"
$ImageExts = @(".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")

New-Item -ItemType Directory -Path $ImagesDir -Force | Out-Null
New-Item -ItemType Directory -Path $AnnotationsDir -Force | Out-Null

$images = Get-ChildItem -LiteralPath $Source -File | Where-Object { $ImageExts -contains $_.Extension.ToLowerInvariant() }
foreach ($image in $images) {
    Copy-Item -LiteralPath $image.FullName -Destination (Join-Path $ImagesDir $image.Name) -Force
}

$jsons = Get-ChildItem -LiteralPath $Source -File -Filter "*.json"
foreach ($json in $jsons) {
    $dest = Join-Path $AnnotationsDir $json.Name
    Copy-Item -LiteralPath $json.FullName -Destination $dest -Force

    $data = Get-Content -LiteralPath $dest -Encoding UTF8 -Raw | ConvertFrom-Json
    if ($data.PSObject.Properties.Name -contains "imagePath" -and $data.imagePath) {
        $imageName = Split-Path -Leaf ([string]$data.imagePath)
        $data.imagePath = "../images/$imageName"
        $data | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $dest -Encoding UTF8
    }
}

python (Join-Path $Project "update_readme.py")

& $Git -C $Project add -A

$pending = & $Git -C $Project diff --cached --name-only
if (-not $pending) {
    Write-Host "No changes to commit. images=$($images.Count) annotations=$($jsons.Count)"
    exit 0
}

$message = "Sync Labelme annotations $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
& $Git -C $Project commit -m $message

if (-not $NoPush) {
    powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Project "publish_to_github_api.ps1") -Project $Project
}

Write-Host "Synced. images=$($images.Count) annotations=$($jsons.Count)"
