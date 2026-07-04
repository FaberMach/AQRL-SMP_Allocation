param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8765,
    [switch]$Open
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

$Arguments = @("-m", "aqrl.dashboards.client_view", "--host", $HostName, "--port", "$Port")
if ($Open) {
    $Arguments += "--open"
}

poetry run python $Arguments
