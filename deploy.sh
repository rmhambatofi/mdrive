#!/bin/bash
set -euo pipefail

# ============================================================
# MDrive — Script de déploiement cPanel
# Appelé par .cpanel.yml lors d'un git pull
# ============================================================

HOME_DIR="$HOME"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

PIP="$HOME_DIR/virtualenv/mdrive/3.11/bin/pip"
PYTHON="$HOME_DIR/virtualenv/mdrive/3.11/bin/python"

BACKEND_SRC="$REPO_DIR/backend"
BACKEND_DEST="$HOME_DIR/mdrive"

FRONTEND_SRC="$REPO_DIR/frontend"
FRONTEND_DEST="$HOME_DIR/drive.manitra.fr"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# ── BACKEND ──────────────────────────────────────────────────

log "==> [BACKEND] Installation des dépendances Python..."
"$PIP" install -r "$BACKEND_SRC/requirements.txt" --quiet

log "==> [BACKEND] Synchronisation des fichiers vers $BACKEND_DEST..."
rsync -a --delete \
  --exclude='.env' \
  --exclude='.htaccess' \
  --exclude='userdata/' \
  --exclude='venv/' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='logs/' \
  "$BACKEND_SRC/" "$BACKEND_DEST/"

#log "==> [BACKEND] Application des migrations..."
#FLASK_APP=run.py "$PYTHON" -m flask db upgrade --directory "$BACKEND_DEST/migrations"

log "==> [BACKEND] Redémarrage de l'application Passenger..."
mkdir -p "$BACKEND_DEST/tmp"
touch "$BACKEND_DEST/tmp/restart.txt"

# ── FRONTEND ─────────────────────────────────────────────────

log "==> [FRONTEND] Installation des dépendances Node.js..."
cd "$FRONTEND_SRC"
npm install

log "==> [FRONTEND] Build de l'application React..."
npm run build

log "==> [FRONTEND] Synchronisation du build vers $FRONTEND_DEST..."
rsync -a --delete "$FRONTEND_SRC/dist/" "$FRONTEND_DEST/"

log "==> [FRONTEND] Déploiement du .htaccess..."
cp "$FRONTEND_SRC/.htaccess.production" "$FRONTEND_DEST/.htaccess"

log "==> Déploiement terminé avec succès."
