[CmdletBinding()]
param(
  [switch]$SkipBuild,
  [switch]$SkipTests,
  [int]$Port = 8000,
  [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

if (-not $SkipBuild) {
  & (Join-Path $PSScriptRoot "build.ps1") -SkipTests:$SkipTests
}

& (Join-Path $PSScriptRoot "start.ps1") -Port $Port -HostAddress $HostAddress
