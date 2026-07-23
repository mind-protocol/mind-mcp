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
MIND_HTTP_CITIZEN=aurore
```

Génère le jeton :

```powershell
.venv\Scripts\python -c "import secrets; print(secrets.token_hex(24))"
```

### 2 bis. Identité du pair (`MIND_HTTP_CITIZEN`)

Les handlers résolvent le citoyen qui agit dans l'**environnement du processus**
(`runtime/identity.py`, `CITIZEN_HANDLE`), jamais par requête. Un processus HTTP porte
donc **une** identité, et le jeton est nominatif : **un jeton = un pair = un processus**.

Sans `MIND_HTTP_CITIZEN`, le pair est anonyme : `profile`, `bond`, `anamnesis`, `alarm`
répondent « Cannot determine citizen identity », les Moments créés par `send` n'ont pas
d'auteur, et le gate d'autonomie retombe sur `_unknown` (tier GUARDED, niveau 1).

Le handle doit avoir son profil, `citizens/<handle>/profile.json` — sinon le serveur
démarre quand même mais journalise un avertissement. Le bloc `capabilities` fixe les
droits, lus par `runtime/citizens/autonomy_gate.py` :

```json
"capabilities": { "autonomy_level": 5, "supervision_tier": 2 }
```

- `autonomy_level` (0-10, **un nombre**) : la table `AUTONOMY_PERMISSIONS`
  (`runtime/citizens/identity_loader.py`) donne les permissions. 1 = observateur (lecture
  + parole), 3 = écrit le graphe, 5 = + `task`, 6 = + `spawn`.
- `supervision_tier` (0-4) : 2 = GUARDED, tout passe sauf les actions irréversibles
  (`spawn`) qui sont mises en file d'attente humaine.

Chaque décision du gate est journalisée dans `shrine/state/autonomy_audit.jsonl` — c'est
là qu'on vérifie ce qu'un pair a le droit de faire, et ce qu'il a fait.

**Deux pairs = deux processus**, sur deux ports, avec chacun son jeton et son
`MIND_HTTP_CITIZEN`. Partager un jeton entre deux pairs les ferait écrire sous la même
identité — le graphe ne saurait plus qui a agi.

Le serveur stdio local (`mcp/server.py`) partage le même `.env` mais **ignore**
`MIND_HTTP_CITIZEN` : les sessions locales gardent leur propre identité.

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

L'identité se vérifie par un outil qui en dépend — `profile` doit renvoyer le bon pair,
pas « Cannot determine citizen identity » :

```powershell
curl -X POST https://trusted-magpie-social.ngrok-free.app/mcp `
  -H "Authorization: Bearer <jeton>" -H "Content-Type: application/json" `
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"profile","arguments":{"action":"get"}}}'
```

Attendu : `Profile for @aurore`. Au démarrage, le serveur journalise aussi
`Identité du transport HTTP : @aurore`.

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
