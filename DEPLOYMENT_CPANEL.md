# MDrive - Guide de Déploiement sur cPanel

Ce guide détaille le déploiement de l'application MDrive sur un hébergement cPanel avec Python et MySQL.

## Prérequis

- Hébergement cPanel avec :
  - Python Selector (Python 3.8+)
  - MySQL/MariaDB
  - Accès SSH (recommandé)
  - Node.js Selector (pour le build frontend)
- Domaine ou sous-domaine configuré
- Base de données MySQL créée

## Architecture de déploiement

```
public_html/
├── mdrive/                    # Application Flask (backend)
│   ├── app/
│   ├── userdata/
│   ├── passenger_wsgi.py      # Point d'entrée Passenger
│   ├── .htaccess
│   └── ...
└── mdrive-frontend/           # Frontend React (build statique)
    ├── index.html
    ├── assets/
    └── ...
```

---

## Étape 1 : Préparation de la base de données

### 1.1 Créer la base de données (si pas déjà fait)

1. Connectez-vous à cPanel
2. Allez dans **MySQL Databases**
3. Créez une nouvelle base de données : `votre_user_mdrive`
4. Créez un utilisateur MySQL : `votre_user_mdrive_user`
5. Associez l'utilisateur à la base avec **ALL PRIVILEGES**

### 1.2 Noter les informations de connexion

```
Hôte : localhost
Base : votre_cpanel_user_mdrive
Utilisateur : votre_cpanel_user_mdrive_user
Mot de passe : votre_mot_de_passe
```

---

## Étape 2 : Déploiement du Backend (Flask)

### 2.1 Créer l'application Python dans cPanel

1. Allez dans **Setup Python App** dans cPanel
2. Cliquez sur **Create Application**
3. Configurez :
   - **Python version** : 3.9 ou supérieur
   - **Application root** : `mdrive`
   - **Application URL** : `/api` (ou votre sous-domaine API)
   - **Application startup file** : `passenger_wsgi.py`
   - **Application Entry point** : `application`
4. Cliquez sur **Create**
5. Notez la commande pour activer l'environnement virtuel

### 2.2 Uploader les fichiers backend

Via **File Manager** ou **FTP**, uploadez le contenu du dossier `backend/` dans `~/mdrive/` :

```
mdrive/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   ├── controllers/
│   ├── services/
│   ├── middleware/
│   ├── routes/
│   └── utils/
├── userdata/           # Dossier pour les fichiers utilisateurs
├── requirements.txt
├── run.py
└── .env
```

### 2.3 Créer le fichier passenger_wsgi.py

Créez le fichier `~/mdrive/passenger_wsgi.py` :

```python
import sys
import os

# Chemin vers l'application
INTERP = os.path.expanduser("~/virtualenv/mdrive/3.9/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Ajouter le chemin de l'application
sys.path.insert(0, os.path.dirname(__file__))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Importer l'application Flask
from app import create_app

# Créer l'application
application = create_app('production')
```

> **Note** : Adaptez le chemin `~/virtualenv/mdrive/3.9/bin/python` selon votre configuration cPanel (visible dans Python App Setup).

### 2.4 Créer le fichier .htaccess

Créez le fichier `~/mdrive/.htaccess` :

```apache
# Activer le moteur de réécriture
RewriteEngine On

# Rediriger toutes les requêtes vers Passenger
PassengerEnabled On
PassengerAppRoot /home/votre_user/mdrive

# Headers de sécurité
Header set X-Content-Type-Options "nosniff"
Header set X-Frame-Options "SAMEORIGIN"
Header set X-XSS-Protection "1; mode=block"

# Autoriser les gros uploads (100MB)
LimitRequestBody 104857600
```

### 2.5 Configurer le fichier .env

Créez le fichier `~/mdrive/.env` :

```env
# Database Configuration (cPanel MySQL)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=votre_cpanel_user_mdrive
DB_USER=votre_cpanel_user_mdrive_user
DB_PASSWORD=votre_mot_de_passe_mysql

# JWT Configuration - CHANGEZ CES VALEURS !
JWT_SECRET_KEY=generez-une-cle-secrete-tres-longue-et-aleatoire-minimum-32-caracteres
JWT_ACCESS_TOKEN_EXPIRES=86400

# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=une-autre-cle-secrete-differente-de-jwt

# File Upload Configuration
MAX_FILE_SIZE=104857600
UPLOAD_FOLDER=/home/votre_user/mdrive/userdata
ALLOWED_EXTENSIONS=pdf,doc,docx,txt,png,jpg,jpeg,gif,zip,rar,mp4,mp3

# Storage Configuration
DEFAULT_STORAGE_QUOTA=5368709120

# CORS - Domaine du frontend
CORS_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com
```

> **Important** : Générez des clés secrètes uniques avec : `python -c "import secrets; print(secrets.token_hex(32))"`

### 2.6 Installer les dépendances

Via **Terminal SSH** ou **cPanel Terminal** :

```bash
# Activer l'environnement virtuel (commande fournie par cPanel)
source /home/votre_user/virtualenv/mdrive/3.9/bin/activate

# Aller dans le dossier de l'application
cd ~/mdrive

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.7 Créer le dossier userdata

```bash
mkdir -p ~/mdrive/userdata
chmod 755 ~/mdrive/userdata
```

### 2.8 Initialiser la base de données

```bash
cd ~/mdrive
source /home/votre_user/virtualenv/mdrive/3.9/bin/activate
python init_db.py
```

### 2.9 Redémarrer l'application

Dans cPanel > **Setup Python App** > Cliquez sur **Restart** pour votre application.

---

## Étape 3 : Déploiement du Frontend (React)

### 3.1 Build du frontend en local

Sur votre machine locale :

```bash
cd frontend

# Créer un fichier .env.production
echo "VITE_API_URL=https://votre-domaine.com/api" > .env.production

# Installer les dépendances
npm install

# Build pour la production
npm run build
```

### 3.2 Modifier la configuration API pour la production

Avant le build, modifiez `frontend/src/services/api.js` :

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ... reste du code
```

### 3.3 Uploader le build

Uploadez le contenu du dossier `frontend/dist/` vers `~/public_html/` (ou un sous-dossier) :

```
public_html/
├── index.html
├── assets/
│   ├── index-xxxxx.js
│   └── index-xxxxx.css
└── .htaccess
```

### 3.4 Créer le .htaccess pour le frontend

Créez `~/public_html/.htaccess` :

```apache
# Activer le moteur de réécriture
RewriteEngine On

# Rediriger les requêtes API vers le backend
RewriteRule ^api/(.*)$ /mdrive/$1 [P,L]

# Pour React Router - rediriger vers index.html
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]

# Compression Gzip
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/css application/json
    AddOutputFilterByType DEFLATE application/javascript text/javascript
</IfModule>

# Cache pour les assets statiques
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>

# Headers de sécurité
Header set X-Content-Type-Options "nosniff"
Header set X-Frame-Options "SAMEORIGIN"
Header set X-XSS-Protection "1; mode=block"
```

---

## Étape 4 : Configuration alternative avec sous-domaine API

Si vous préférez un sous-domaine pour l'API (ex: `api.votre-domaine.com`) :

### 4.1 Créer le sous-domaine

1. cPanel > **Subdomains**
2. Créez `api.votre-domaine.com` pointant vers `~/mdrive`

### 4.2 Modifier le .env backend

```env
CORS_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com
```

### 4.3 Modifier la config frontend

Dans `frontend/.env.production` :
```env
VITE_API_URL=https://api.votre-domaine.com
```

---

## Étape 5 : SSL/HTTPS

### 5.1 Activer SSL

1. cPanel > **SSL/TLS Status**
2. Activez **AutoSSL** ou installez un certificat Let's Encrypt
3. Forcez HTTPS dans cPanel > **Domains** > **Force HTTPS Redirect**

### 5.2 Mettre à jour les URLs

Assurez-vous que toutes les URLs dans `.env` utilisent `https://`.

---

## Étape 6 : Vérification du déploiement

### 6.1 Tester le backend

```bash
# Depuis SSH
curl https://votre-domaine.com/api/auth/login

# Ou depuis votre navigateur
https://votre-domaine.com/api/auth/login
```

Réponse attendue :
```json
{"error": "Email and password are required"}
```

### 6.2 Tester le frontend

Ouvrez `https://votre-domaine.com` dans votre navigateur.

### 6.3 Tester l'inscription

1. Allez sur la page d'inscription
2. Créez un compte
3. Vérifiez que vous pouvez vous connecter

---

## Dépannage

### Erreur 500 Internal Server Error

1. Vérifiez les logs d'erreur :
   ```bash
   cat ~/mdrive/stderr.log
   ```

2. Vérifiez les permissions :
   ```bash
   chmod 755 ~/mdrive
   chmod 644 ~/mdrive/*.py
   chmod 755 ~/mdrive/userdata
   ```

3. Vérifiez le fichier `passenger_wsgi.py`

### Erreur de connexion à la base de données

1. Vérifiez les identifiants dans `.env`
2. Vérifiez que l'utilisateur MySQL a les droits sur la base
3. Testez la connexion :
   ```bash
   mysql -u votre_user_mdrive_user -p votre_user_mdrive
   ```

### CORS Error

1. Vérifiez que `CORS_ORIGINS` dans `.env` contient votre domaine frontend
2. Incluez les variantes avec et sans `www`

### Fichiers non uploadés

1. Vérifiez les permissions du dossier `userdata` :
   ```bash
   chmod 755 ~/mdrive/userdata
   ```

2. Vérifiez la limite de taille dans `.htaccess`

### Application ne redémarre pas

1. Allez dans cPanel > **Setup Python App**
2. Cliquez sur **Restart**
3. Vérifiez les logs d'erreur

---

## Maintenance

### Mise à jour de l'application

1. Uploadez les nouveaux fichiers
2. Via SSH :
   ```bash
   cd ~/mdrive
   source /home/votre_user/virtualenv/mdrive/3.9/bin/activate
   pip install -r requirements.txt
   ```
3. Redémarrez l'application dans cPanel

### Sauvegarde

Éléments à sauvegarder régulièrement :
- Base de données MySQL (via cPanel > **Backup**)
- Dossier `~/mdrive/userdata/` (fichiers utilisateurs)
- Fichier `.env` (configuration)

### Logs

```bash
# Logs d'erreur Python
cat ~/mdrive/stderr.log

# Logs d'accès Apache
cat ~/logs/votre-domaine.com-ssl_log
```

---

## Checklist de déploiement

- [ ] Base de données MySQL créée et configurée
- [ ] Application Python créée dans cPanel
- [ ] Fichiers backend uploadés
- [ ] `passenger_wsgi.py` créé et configuré
- [ ] `.env` configuré avec les bonnes valeurs
- [ ] Dépendances Python installées
- [ ] Dossier `userdata` créé avec les bonnes permissions
- [ ] Base de données initialisée (`init_db.py`)
- [ ] Frontend buildé en production
- [ ] Frontend uploadé dans `public_html`
- [ ] `.htaccess` configurés (backend et frontend)
- [ ] SSL/HTTPS activé
- [ ] Tests de fonctionnement effectués
- [ ] Sauvegarde configurée

---

## Support

En cas de problème :
1. Consultez les logs d'erreur
2. Vérifiez la configuration `.env`
3. Testez les endpoints API manuellement
4. Contactez le support de votre hébergeur pour les problèmes liés à cPanel
