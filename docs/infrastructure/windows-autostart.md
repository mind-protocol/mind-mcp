# Windows autostart (Scheduled Task)

Runbook pour exposer le serveur MCP publiquement depuis un hote Windows,
en gardant vivants le serveur HTTP (`mcp/server_http.py`) et le tunnel ngrok.
Equivalent Windows du guide WSL (`wsl-autostart.md`).

## Architecture

| Composant | Role | Adresse |
|---|---|---|
| `mcp/server_http.py` (Flask) | Transport HTTP MCP | `127.0.0.1:3005` |
| `ngrok` (MSIX) | Tunnel public | `https://trusted-magpie-social.ngrok-free.app` |
| `scripts/mcp_online.ps1` | Superviseur (relance si l'un tombe) | Scheduled Task |

Le serveur Flask expose `POST /mcp`, `GET /health`, `/sse`, `/tools` — **sans**
prefixe `/api/mcp`. L'endpoint a configurer cote client (ChatGPT, connecteur
Claude.ai, Citizen) est donc :

```
https://trusted-magpie-social.ngrok-free.app/mcp
```

## 1) Prerequis

- venv du projet installe : `.venv\Scripts\python.exe` a la racine du repo.
- ngrok installe et authentifie (`ngrok config check` doit etre valide).
  Le domaine reserve `trusted-magpie-social` doit appartenir au compte ngrok.

## 2) Installer la Scheduled Task

Le superviseur vit sous `%LOCALAPPDATA%\mind-mcp\` (hors OneDrive, pour ne pas
synchroniser les logs). Copiez `scripts/mcp_online.ps1` puis enregistrez la
tache, en une passe :

```powershell
$Dir = Join-Path $env:LOCALAPPDATA 'mind-mcp'
New-Item -ItemType Directory -Force -Path $Dir | Out-Null
Copy-Item "C:\Users\reyno\OneDrive\Documents\mind-mcp-v2\scripts\mcp_online.ps1" (Join-Path $Dir 'mcp_online.ps1') -Force
$Script = Join-Path $Dir 'mcp_online.ps1'

$Action    = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Script`""
$Trigger   = New-ScheduledTaskTrigger -AtLogOn
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$Settings  = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
             -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero)
Register-ScheduledTask -TaskName 'MindMCP-Online' -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force
```

Demarrer sans attendre le prochain logon (le superviseur detecte ce qui tourne
deja et ne double rien) :

```powershell
Start-ScheduledTask -TaskName 'MindMCP-Online'
```

## 3) Checks de sante

Local :

```powershell
curl.exe -s http://127.0.0.1:3005/health
```

Remote :

```powershell
curl.exe -s https://trusted-magpie-social.ngrok-free.app/health
```

Test JSON-RPC complet (doit lister les tools, pas un 404) :

```powershell
curl.exe -s -X POST https://trusted-magpie-social.ngrok-free.app/mcp -H "Content-Type: application/json" -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}'
```

## 4) Logs et status

```powershell
Get-ScheduledTaskInfo -TaskName 'MindMCP-Online' | Format-List TaskName,LastRunTime,LastTaskResult,NextRunTime
Get-Content "$env:LOCALAPPDATA\mind-mcp\logs\supervisor.log" -Tail 20 -Wait
```

Fichiers de logs (`%LOCALAPPDATA%\mind-mcp\logs\`) :

- `supervisor.log`  — decisions du superviseur (start/restart)
- `mcp-http.out.log` / `mcp-http.err.log` — serveur Flask
- `ngrok.out.log` / `ngrok.err.log` — tunnel

## 5) Arret / desinstallation

```powershell
Unregister-ScheduledTask -TaskName 'MindMCP-Online' -Confirm:$false
Get-Process ngrok,python -ErrorAction SilentlyContinue | Stop-Process -Force
```

## 6) Depannage

- **404 sur l'URL publique** : soit le serveur Flask est down (ngrok forwarde
  vers un autre process qui renvoie 404), soit le client tape le mauvais path.
  L'endpoint MCP est `/mcp`, pas `/api/mcp` ni la racine `/`. Verifiez d'abord
  `curl http://127.0.0.1:3005/health` en local.
- **Page HTML ngrok au lieu du JSON** : le tunnel n'a pas d'agent actif (ngrok
  sert sa page d'erreur). Verifiez `Get-Process ngrok` et `ngrok.out.log`.
- **`address already in use` sur :3005** : un ancien process traine.
  `Get-NetTCPConnection -LocalPort 3005 | Select OwningProcess` puis `Stop-Process`.
- **La tache ne demarre pas au boot** : le trigger est `AtLogOn` (session
  utilisateur), pas au boot pur — impose par ngrok en MSIX (l'alias ne se
  resout que dans la session de l'utilisateur). Pour un demarrage headless
  avant logon, remplacer le ngrok MSIX par le binaire standalone `.exe` et le
  lancer via un service Windows (NSSM).
