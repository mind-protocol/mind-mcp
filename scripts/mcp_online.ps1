# mcp_online.ps1 — Windows supervisor for the remote MCP surface.
#
# Keeps two processes alive so the Mind MCP is reachable publicly:
#   1. the Flask HTTP MCP server (mcp/server_http.py) on $Port
#   2. the ngrok tunnel exposing it on the reserved domain
#
# Restarts either one if it dies. Meant to be launched by a per-user
# Scheduled Task at logon (see docs/infrastructure/windows-autostart.md).
#
# Paths default to this host but can be overridden via environment variables:
#   MIND_REPO_DIR, MIND_MCP_PORT, MIND_NGROK_DOMAIN, MIND_NGROK_EXE

$ErrorActionPreference = 'SilentlyContinue'

$RepoDir = if ($env:MIND_REPO_DIR)     { $env:MIND_REPO_DIR }     else { 'C:\Users\reyno\OneDrive\Documents\mind-mcp-v2' }
$Port    = if ($env:MIND_MCP_PORT)     { [int]$env:MIND_MCP_PORT } else { 3005 }
$Domain  = if ($env:MIND_NGROK_DOMAIN) { $env:MIND_NGROK_DOMAIN } else { 'trusted-magpie-social.ngrok-free.app' }
$Ngrok   = if ($env:MIND_NGROK_EXE)    { $env:MIND_NGROK_EXE }    else { 'C:\Users\reyno\AppData\Local\Microsoft\WindowsApps\ngrok.exe' }
$Python  = Join-Path $RepoDir '.venv\Scripts\python.exe'
$LogDir  = Join-Path $env:LOCALAPPDATA 'mind-mcp\logs'

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Beat($m) {
    "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $m" |
        Out-File -Append -Encoding utf8 (Join-Path $LogDir 'supervisor.log')
}
function PortUp($p) {
    Test-NetConnection 127.0.0.1 -Port $p -WarningAction SilentlyContinue -InformationLevel Quiet
}
function NgrokUp {
    [bool](Get-Process ngrok -ErrorAction SilentlyContinue)
}

Beat "supervisor started (repo=$RepoDir port=$Port domain=$Domain)"

while ($true) {
    # 1. Flask HTTP MCP server
    if (-not (PortUp $Port)) {
        Beat "MCP HTTP down -> starting server_http.py"
        Start-Process -FilePath $Python -ArgumentList 'mcp/server_http.py' `
            -WorkingDirectory $RepoDir -WindowStyle Hidden `
            -RedirectStandardOutput (Join-Path $LogDir 'mcp-http.out.log') `
            -RedirectStandardError  (Join-Path $LogDir 'mcp-http.err.log')
        Start-Sleep 5
    }

    # 2. ngrok tunnel on the reserved domain
    if (-not (NgrokUp)) {
        Beat "ngrok down -> starting tunnel"
        Start-Process -FilePath $Ngrok `
            -ArgumentList @('http', "--url=https://$Domain", "$Port", '--log=stdout') `
            -WindowStyle Hidden `
            -RedirectStandardOutput (Join-Path $LogDir 'ngrok.out.log') `
            -RedirectStandardError  (Join-Path $LogDir 'ngrok.err.log')
        Start-Sleep 3
    }

    Start-Sleep 30
}
