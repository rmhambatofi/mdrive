# Dépannage Dashboard MDrive

## Problème : Le dashboard ne s'affiche pas après le login

### Causes possibles et solutions

#### 1. Backend non démarré ou erreur

**Vérifier que le backend fonctionne :**
```bash
# Dans un terminal
cd c:\Projects\manitra\mdrive\backend
python run.py
```

Vous devriez voir :
```
* Running on http://127.0.0.1:5000
* Running on http://172.21.0.1:5000
```

**Si erreur de base de données :**
- Vérifiez que MySQL est démarré
- Vérifiez le fichier [.env](c:\Projects\manitra\mdrive\backend\.env)
- Exécutez : `python init_db.py`

#### 2. Frontend non démarré

**Vérifier que le frontend fonctionne :**
```bash
# Dans un autre terminal
cd c:\Projects\manitra\mdrive\frontend
npm run dev
```

Vous devriez voir :
```
VITE v5.0.7  ready in 1234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

#### 3. Erreur CORS

**Symptômes :**
- Le login semble réussir mais rien ne se passe
- Erreurs CORS dans la console du navigateur

**Solution :**
Vérifiez dans [backend/.env](c:\Projects\manitra\mdrive\backend\.env) :
```env
CORS_ORIGINS=http://localhost:3000
```

#### 4. Token JWT invalide ou expiré

**Symptômes :**
- Redirection immédiate vers `/login` après connexion
- Erreur 401 dans la console

**Solution :**
Videz le localStorage :
```javascript
// Dans la console du navigateur (F12)
localStorage.clear()
```

Puis reconnectez-vous.

#### 5. Dépendances manquantes

**Frontend :**
```bash
cd frontend
npm install
```

**Backend :**
```bash
cd backend
pip install -r requirements.txt
```

### Étapes de débogage complètes

#### Étape 1 : Vérifier la console du navigateur

1. Ouvrez les DevTools (F12)
2. Allez dans l'onglet "Console"
3. Rechargez la page après le login
4. Cherchez les erreurs

**Erreurs courantes :**

```
Failed to fetch
```
→ Le backend n'est pas démarré ou le proxy ne fonctionne pas

```
401 Unauthorized
```
→ Token invalide, videz le localStorage

```
Network Error
```
→ Vérifiez que le backend tourne sur le port 5000

#### Étape 2 : Vérifier la console backend

Dans le terminal où tourne le backend, vérifiez :
```
127.0.0.1 - - [date] "POST /api/auth/login HTTP/1.1" 200
127.0.0.1 - - [date] "GET /api/files HTTP/1.1" 200
```

Si vous voyez des erreurs 500 ou 401, il y a un problème côté serveur.

#### Étape 3 : Test manuel de l'API

Utilisez curl ou Postman pour tester :

```bash
# Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'
```

Vous devriez recevoir un token.

```bash
# Test get files (remplacez <TOKEN> par le token reçu)
curl -X GET http://localhost:5000/api/files \
  -H "Authorization: Bearer <TOKEN>"
```

#### Étape 4 : Vérifier la base de données

```bash
mysql -u root -p mdrive
```

```sql
-- Vérifier les utilisateurs
SELECT id, email, full_name FROM users;

-- Vérifier les fichiers
SELECT id, file_name, is_folder FROM files;
```

### Solutions spécifiques par erreur

#### Erreur : "Cannot GET /dashboard"

**Cause :** React Router ne fonctionne pas correctement

**Solution :**
Vérifiez que [frontend/src/App.jsx](c:\Projects\manitra\mdrive\frontend\src\App.jsx) contient :
```jsx
<Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
```

#### Erreur : "Module not found" dans le frontend

**Solution :**
```bash
cd frontend
rm -rf node_modules package-lock.json  # Linux/Mac
# ou
rmdir /s node_modules & del package-lock.json  # Windows
npm install
```

#### Page blanche après login

**Causes possibles :**
1. Erreur JavaScript - Vérifiez la console
2. Composant Dashboard n'existe pas
3. CSS Tailwind non chargé

**Solution :**
```bash
# Vérifier que tous les fichiers existent
ls frontend/src/pages/Dashboard.jsx
ls frontend/src/components/Layout/Navbar.jsx
ls frontend/src/components/Layout/Sidebar.jsx
```

#### Login réussit mais redirige immédiatement vers /login

**Cause :** PrivateRoute détecte que l'utilisateur n'est pas authentifié

**Solution :**
Vérifiez [AuthContext.jsx](c:\Projects\manitra\mdrive\frontend\src\contexts\AuthContext.jsx) :
```jsx
// Dans la fonction login
if (result.success) {
  setUser(data.user);  // Important !
  return { success: true, data };
}
```

### Checklist complète de vérification

- [ ] MySQL est démarré
- [ ] Base de données `mdrive` existe
- [ ] Fichier [backend/.env](c:\Projects\manitra\mdrive\backend\.env) est configuré
- [ ] Backend démarre sans erreur sur le port 5000
- [ ] Frontend démarre sans erreur sur le port 3000
- [ ] Aucune erreur dans la console du navigateur
- [ ] Aucune erreur dans la console du backend
- [ ] Token JWT est généré et stocké après le login
- [ ] API `/api/files` répond correctement

### Commande rapide pour tout tester

```bash
# Terminal 1 : Backend
cd c:\Projects\manitra\mdrive\backend
python run.py

# Terminal 2 : Frontend
cd c:\Projects\manitra\mdrive\frontend
npm run dev

# Terminal 3 : Test
curl http://localhost:5000/api/auth/login
curl http://localhost:3000
```

### Si rien ne fonctionne : Réinitialisation complète

```bash
# 1. Arrêter tous les serveurs (Ctrl+C)

# 2. Nettoyer le frontend
cd frontend
rm -rf node_modules package-lock.json
npm install

# 3. Réinitialiser la base de données
cd ../backend
python init_db.py

# 4. Redémarrer backend
python run.py

# 5. Redémarrer frontend (nouveau terminal)
cd ../frontend
npm run dev

# 6. Vider le cache du navigateur
# F12 > Application > Clear Storage > Clear site data
```

### Contact et Support

Si le problème persiste :
1. Vérifiez les logs dans les deux terminaux
2. Partagez les messages d'erreur complets
3. Vérifiez la version de Python, Node.js, MySQL
