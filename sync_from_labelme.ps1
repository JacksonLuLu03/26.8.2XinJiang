param(
    [string]$Source,
    [string]$Project = $PSScriptRoot,
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"

if (-not $Source) {
    $Source = Join-Path 'E:\Labelme' ('3' + ([char]0x5362) + ([char]0x6770))
}

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

git -C $Project add -A

$pending = git -C $Project diff --cached --name-only
if (-not $pending) {
    Write-Host "No changes to commit. images=$($images.Count) annotations=$($jsons.Count)"
    exit 0
}

$message = "Sync Labelme annotations $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git -C $Project commit -m $message

if (-not $NoPush) {
    git -C $Project push
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "git push failed. Falling back to GitHub Contents API."
        powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Project "publish_to_github_api.ps1") -Project $Project
    }
}

Write-Host "Synced. images=$($images.Count) annotations=$($jsons.Count)"
