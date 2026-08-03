param(
    [string]$Project = $PSScriptRoot
)

$ErrorActionPreference = "Stop"

function Encode-Path([string]$Path) {
    return (($Path -split "/") | ForEach-Object { [System.Uri]::EscapeDataString($_) }) -join "/"
}

function Get-GitHubCredentialToken {
    $credentialInput = "protocol=https`nhost=github.com`n`n"
    $credentialOutput = $credentialInput | git credential fill
    $credentialMap = @{}

    $credentialOutput -split "`n" | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            $credentialMap[$matches[1]] = $matches[2].TrimEnd("`r")
        }
    }

    if ([string]::IsNullOrWhiteSpace($credentialMap["password"])) {
        throw "GitHub credential token was not available. Run: git credential-manager github login"
    }

    return $credentialMap["password"]
}

function Get-RemoteBlobMap($Owner, $Repo, $Headers) {
    $ref = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo/git/ref/heads/main" -Headers $Headers -Method Get
    $commit = Invoke-RestMethod -Uri $ref.object.url -Headers $Headers -Method Get
    $tree = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo/git/trees/$($commit.tree.sha)?recursive=1" -Headers $Headers -Method Get
    $map = @{}

    foreach ($item in $tree.tree) {
        if ($item.type -eq "blob") {
            $map[$item.path] = $item.sha
        }
    }

    return $map
}

$config = Get-Content -LiteralPath (Join-Path $Project "config.json") -Encoding UTF8 -Raw | ConvertFrom-Json
$owner = $config.github_owner
$repo = $config.github_repo
$token = Get-GitHubCredentialToken
$headers = @{
    Authorization = "Bearer $token"
    Accept = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

$targetFiles = @(git -C $Project -c core.quotePath=false ls-files | Where-Object { $_.Trim() -ne "" })
$targetSet = @{}
foreach ($path in $targetFiles) {
    $targetSet[$path.Replace("\", "/")] = $true
}

$remoteMap = Get-RemoteBlobMap $owner $repo $headers

foreach ($path in $targetFiles) {
    $path = $path.Replace("\", "/")
    $local = Join-Path $Project ($path -replace "/", "\")
    $encodedPath = Encode-Path $path
    $uri = "https://api.github.com/repos/$owner/$repo/contents/$encodedPath"
    $sha = $null
    $localSha = (git -C $Project hash-object -- $local).Trim()

    if ($remoteMap.ContainsKey($path)) {
        $sha = $remoteMap[$path]
    }

    if ($sha -and $sha -eq $localSha) {
        Write-Host "SKIP $path"
        continue
    }

    $bodyHash = @{
        message = "Sync project layout"
        content = [Convert]::ToBase64String([System.IO.File]::ReadAllBytes($local))
        branch = "main"
    }
    if ($sha) {
        $bodyHash.sha = $sha
    }

    Invoke-RestMethod -Uri $uri -Headers $headers -Method Put -Body ($bodyHash | ConvertTo-Json -Compress) -ContentType "application/json" | Out-Null
    Write-Host "PUT $path"
}

$remoteMap = Get-RemoteBlobMap $owner $repo $headers

foreach ($path in @($remoteMap.Keys | Sort-Object)) {
    if (-not $targetSet.ContainsKey($path)) {
        $encodedPath = Encode-Path $path
        $uri = "https://api.github.com/repos/$owner/$repo/contents/$encodedPath"
        $body = @{
            message = "Remove old project layout file"
            sha = $remoteMap[$path]
            branch = "main"
        } | ConvertTo-Json -Compress

        Invoke-RestMethod -Uri $uri -Headers $headers -Method Delete -Body $body -ContentType "application/json" | Out-Null
        Write-Host "DELETE $path"
    }
}

Write-Host "GitHub API sync complete. files=$($targetFiles.Count)"
