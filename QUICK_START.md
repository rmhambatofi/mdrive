# MDrive - Quick Start Guide

Get MDrive up and running in minutes!

## Prerequisites

Choose one of these options:

### Option 1: Docker (Recommended)
- Docker Desktop installed
- Docker Compose installed

### Option 2: Manual Setup
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

---

## Option 1: Docker Setup (Easiest)

### 1. Clone or navigate to the project
```bash
cd mdrive
```

### 2. Start all services
```bash
docker-compose up -d
```

This will start:
- MySQL database on port 3306
- Flask backend on port 5000
- React frontend on port 3000

### 3. Initialize the database
```bash
docker exec -it mdrive-backend python init_db.py
```

### 4. Access the application
Open your browser and visit: [http://localhost:3000](http://localhost:3000)

### 5. Stop the services
```bash
docker-compose down
```

---

## Option 2: Manual Setup

### Step 1: Database Setup

1. **Start MySQL** and create the database:
```sql
CREATE DATABASE mdrive CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. **Create a MySQL user** (optional but recommended):
```sql
CREATE USER 'mdrive_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON mdrive.* TO 'mdrive_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 2: Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Configure environment:**
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and update these values:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mdrive
DB_USER=mdrive_user
DB_PASSWORD=your_password

JWT_SECRET_KEY=change-this-to-a-random-secret-key
SECRET_KEY=change-this-to-another-random-key
```

6. **Initialize database:**
```bash
python init_db.py
```

7. **Start the backend:**
```bash
python run.py
```

Backend will be running on [http://localhost:5000](http://localhost:5000)

### Step 3: Frontend Setup

1. **Open a new terminal** and navigate to frontend directory:
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

Frontend will be running on [http://localhost:3000](http://localhost:3000)

---

## First Time Usage

### 1. Create an Account

1. Visit [http://localhost:3000](http://localhost:3000)
2. Click "Sign up"
3. Enter your details:
   - Email address
   - Password (min. 8 chars, 1 uppercase, 1 lowercase, 1 number)
   - Full name (optional)
4. Click "Sign Up"

### 2. Upload Your First File

1. Click "Upload Files" button
2. Drag and drop files or click "Browse files"
3. Click "Upload"
4. Your files will appear in the main view

### 3. Create Folders

1. Click "New Folder" button
2. Enter folder name
3. Click "Create Folder"
4. Double-click folder to open it

### 4. Organize Files

- **Rename**: Right-click file → Rename
- **Download**: Right-click file → Download
- **Delete**: Right-click file → Delete
- **Navigate**: Use breadcrumb navigation at the top

---

## Troubleshooting

### Backend won't start

**Error: Can't connect to MySQL**
```bash
# Check if MySQL is running
# Windows: services.msc
# Linux: sudo systemctl status mysql
# Mac: brew services list

# Verify database exists
mysql -u root -p
> SHOW DATABASES;
```

**Error: Module not found**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start

**Error: Cannot find module**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json  # Linux/Mac
rmdir /s node_modules & del package-lock.json  # Windows
npm install
```

**Error: Port 3000 already in use**
```bash
# Change port in vite.config.js or stop other service
```

### File upload fails

**Storage quota exceeded**
- Default quota is 5GB per user
- Check your usage in the navbar
- Delete old files to free space

**File type not allowed**
- Check `ALLOWED_EXTENSIONS` in backend/.env
- Default: pdf, doc, docx, txt, png, jpg, jpeg, gif, zip, rar, mp4, mp3

**File too large**
- Default max size is 100MB
- Adjust `MAX_FILE_SIZE` in backend/.env

### Docker issues

**Services won't start**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

**Database connection failed**
```bash
# Wait for database to be ready (takes ~30 seconds on first start)
docker-compose logs db

# Restart backend after database is ready
docker-compose restart backend
```

---

## Default Configuration

| Setting | Default Value |
|---------|--------------|
| Backend Port | 5000 |
| Frontend Port | 3000 |
| Database Port | 3306 |
| JWT Token Expiry | 24 hours |
| Max File Size | 100 MB |
| Storage Quota | 5 GB per user |
| Allowed Extensions | pdf, doc, docx, txt, png, jpg, jpeg, gif, zip, rar, mp4, mp3 |

---

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
- Customize configuration in `.env` files
- Set up HTTPS for production deployment
- Configure backups for user data

---

## Quick Commands Reference

### Docker
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Rebuild and start
docker-compose up --build -d
```

### Backend
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Start server
python run.py

# Initialize database
python init_db.py

# Install new package
pip install package_name
pip freeze > requirements.txt
```

### Frontend
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Install new package
npm install package_name
```

---

## Support

If you encounter issues not covered here:

1. Check the [README.md](README.md) troubleshooting section
2. Review application logs
3. Verify all prerequisites are installed
4. Check environment variable configuration

Happy storing with MDrive!
