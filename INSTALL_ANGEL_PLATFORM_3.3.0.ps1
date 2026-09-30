param([string]$Target = "D:\Angel_AI")
$ErrorActionPreference = "Stop"
$PackageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if (!(Test-Path $Target)) { throw "Target does not exist: $Target" }
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$files = @(
  "angel_platform\webui\app.js",
  "angel_platform\webui\index.html",
  "ANGEL_PLATFORM_3.3.0_RELEASE_NOTES.md"
)
foreach ($relative in $files) {
  $source = Join-Path $PackageRoot $relative
  $destination = Join-Path $Target $relative
  if (!(Test-Path $source)) { throw "Package file missing: $source" }
  $parent = Split-Path $destination -Parent
  New-Item -ItemType Directory -Force -Path $parent | Out-Null
  if (Test-Path $destination) {
    Copy-Item $destination "$destination.backup-$stamp" -Force
  }
  Copy-Item $source $destination -Force
  Write-Host "Updated $relative"
}
Write-Host "Angel Platform 3.3.0 full foundation upgrade installed."