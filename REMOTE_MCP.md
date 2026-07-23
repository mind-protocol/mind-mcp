# Accès distant au MCP Mind via ngrok

Rendre les 26 outils de cognition (`graph_query`, `graph_write`, `think`, `send`,
`spawn`…) joignables depuis Internet par une **URL stable**, pour qu'un pair (p. ex.
**Aurore**) devienne citoyen du graphe — sans rien installer de son côté.

## Architecture

Le serveur MCP existe en deux transports, mêmes 26 outils (`mcp/server.py`, `MindServer`) :

| Transport | Entrée | Usage |
|---|---|---|
| **stdio** | `python -m mcp.server` | Claude Code local (via `.mcp.json`) |
| **HTTP** | `python mcp/server_http.py` (Flask, port 3005) | accès distant, exposé par ngrok |

En V3, les outils lisent le graphe **en mémoire** depuis `~/.mind-desktop/workspace.json`
(plus de FalkorDB ni de Docker pour ce chemin). L'endpoint HTTP `POST /mcp` parle le
JSON-RPC MCP ; il est compatible avec le connecteur **Remote MCP** de Claude.ai (transport
Streamable HTTP).

## Mise en route

### 1. Environnement Python isolé

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 2. Jeton d'accès (`.env`)

Le serveur HTTP **refuse de démarrer sans jeton** (≥ 16 car.). Crée `.env` (ignoré par git) :

```ini
MIND_MCP_HTTP_HOST=0.0.0.0
MIND_MCP_HTTP_PORT=3005
MIND_MCP_TOKEN=<jeton>
```

Génère le jeton :

```powershell
.venv\Scripts\python -c "import secrets; print(secrets.token_hex(24))"
```

### 3. Semer le graphe workspace

```powershell
.venv\Scripts\python scripts\generate_workspace.py
```

Crée `~/.mind-desktop/workspace.json` (le dossier est créé si absent).

### 4. Lancer le serveur HTTP puis le tunnel

```powershell
.venv\Scripts\python mcp\server_http.py
```
```powershell
ngrok http --domain=trusted-magpie-social.ngrok-free.app 3005
```

L'URL publique stable devient : `https://trusted-magpie-social.ngrok-free.app/mcp`.

## Vérifier

```powershell
# sonde publique (sans jeton)
curl https://trusted-magpie-social.ngrok-free.app/health

# appel MCP authentifié
curl -X POST https://trusted-magpie-social.ngrok-free.app/mcp `
  -H "Authorization: Bearer <jeton>" -H "Content-Type: application/json" `
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"graph_query","arguments":{"queries":["tick engine"]}}}'
```

Attendu : `/health` → `{"status":"ok","tools":26}` ; `POST /mcp` sans jeton → **401** ;
avec jeton → résultats du graphe.

## Côté pair (Aurore) : se connecter

Deux valeurs suffisent :

- **URL** : `https://trusted-magpie-social.ngrok-free.app/mcp` (fixe, publique — pas un secret)
- **Jeton** : en-tête `Authorization: Bearer <MIND_MCP_TOKEN>` — **le seul secret à copier**

### Sur Claude (claude.ai / Desktop)

Réglages → Connecteurs → **Ajouter un connecteur personnalisé** → URL ci-dessus →
en-tête `Authorization: Bearer <jeton>`. Sur l'app desktop, tu peux demander à Claude
d'ajouter le connecteur lui-même.

### Sur ChatGPT

Paramètres → Connecteurs (mode développeur si nécessaire) → ajouter un serveur MCP
distant → URL ci-dessus → en-tête `Authorization: Bearer <jeton>`.

## Sécurité

- **Jeton obligatoire** : `server_http.py` s'arrête si `MIND_MCP_TOKEN` est absent/court ;
  `/mcp` et `/tools` renvoient 401 sans jeton valide (comparaison à temps constant).
- Le jeton donne accès à des outils **mutants** (`graph_write`, `send`, `spawn`…) :
  diffusion restreinte, rotation si fuite suspectée (change `.env`, relance le serveur).
- `/health` est public (aucune capacité). La route `/telegram-webhook` a son propre
  modèle (secret_token Telegram) et **n'est pas** couverte par le jeton MCP — ne l'utilise
  pas sans mettre en place ce secret côté Telegram.
