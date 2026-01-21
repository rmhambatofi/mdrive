# MDrive - Cloud Storage Application

A full-stack cloud storage application similar to Microsoft OneDrive, built with Flask (Python) backend and React frontend.

## Features

- **User Authentication**: Secure JWT-based authentication with bcrypt password hashing
- **File Management**: Upload, download, rename, and delete files
- **Folder Organization**: Create nested folders and navigate hierarchically
- **Storage Quota**: Per-user storage quotas with usage tracking
- **Drag & Drop**: Modern UI with drag-and-drop file upload
- **Responsive Design**: Mobile-friendly interface built with Tailwind CSS
- **Secure Storage**: Files stored in user-specific directories with UUID-based isolation

## Tech Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: Flask-JWT-Extended
- **Password Hashing**: bcrypt
- **Migrations**: Flask-Migrate

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Routing**: React Router v6

## Project Structure

```
mdrive/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── controllers/     # Request handlers
│   │   ├── services/        # Business logic
│   │   ├── middleware/      # Auth middleware
│   │   ├── routes/          # API routes
│   │   └── utils/           # Helper functions
│   ├── userdata/            # User file storage
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   ├── contexts/        # React contexts
│   │   └── pages/           # Page components
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file from the example:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

6. Configure the `.env` file with your settings:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mdrive
DB_USER=root
DB_PASSWORD=your_password

JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ACCESS_TOKEN_EXPIRES=86400

MAX_FILE_SIZE=104857600  # 100MB
DEFAULT_STORAGE_QUOTA=5368709120  # 5GB
```

7. Create the MySQL database:
```sql
CREATE DATABASE mdrive CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

8. Initialize the database:
```bash
python init_db.py
```

9. Run the Flask application:
```bash
python run.py
```

The backend API will be available at [http://localhost:5000](http://localhost:5000)

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

## API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### Get Profile
```http
GET /api/auth/profile
Authorization: Bearer <token>
```

### File Management Endpoints

#### Upload File
```http
POST /api/files/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary>
parent_folder_id: <optional>
```

#### Get Files
```http
GET /api/files?folder_id=<optional>&page=1&per_page=50
Authorization: Bearer <token>
```

#### Download File
```http
GET /api/files/download/<file_id>
Authorization: Bearer <token>
```

#### Delete File
```http
DELETE /api/files/<file_id>
Authorization: Bearer <token>
```

#### Create Folder
```http
POST /api/files/folder
Authorization: Bearer <token>
Content-Type: application/json

{
  "folder_name": "My Folder",
  "parent_folder_id": <optional>
}
```

#### Rename File/Folder
```http
PUT /api/files/<file_id>/rename
Authorization: Bearer <token>
Content-Type: application/json

{
  "new_name": "New Name.pdf"
}
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    storage_quota BIGINT DEFAULT 5368709120,
    storage_used BIGINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Files Table
```sql
CREATE TABLE files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    parent_folder_id INT,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT DEFAULT 0,
    mime_type VARCHAR(100),
    is_folder BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_folder_id) REFERENCES files(id) ON DELETE CASCADE,
    INDEX idx_user_parent (user_id, parent_folder_id),
    INDEX idx_user_folder (user_id, is_folder)
);
```

## Security Features

- **Password Security**: Passwords hashed with bcrypt
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Server-side validation of all inputs
- **File Validation**: Type and size restrictions
- **Path Traversal Protection**: Sanitized file paths
- **CORS Configuration**: Controlled cross-origin requests
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy

## Development

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production

#### Backend
```bash
cd backend
# Set environment to production
export FLASK_ENV=production  # Linux/Mac
set FLASK_ENV=production     # Windows

# Use a production WSGI server like Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

#### Frontend
```bash
cd frontend
npm run build
# Output will be in the dist/ directory
```

## Configuration

### Allowed File Extensions
Edit in [backend/.env](backend/.env):
```env
ALLOWED_EXTENSIONS=pdf,doc,docx,txt,png,jpg,jpeg,gif,zip,rar,mp4,mp3
```

### Storage Quotas
Default quota is 5GB per user. Change in [backend/.env](backend/.env):
```env
DEFAULT_STORAGE_QUOTA=5368709120  # 5GB in bytes
```

### Maximum File Size
Default is 100MB. Change in [backend/.env](backend/.env):
```env
MAX_FILE_SIZE=104857600  # 100MB in bytes
```

## Troubleshooting

### Database Connection Error
- Verify MySQL is running
- Check database credentials in `.env`
- Ensure database exists: `CREATE DATABASE mdrive;`

### File Upload Fails
- Check storage quota hasn't been exceeded
- Verify file type is allowed
- Check file size is under the maximum

### JWT Token Expired
- Tokens expire after 24 hours by default
- User needs to log in again
- Adjust `JWT_ACCESS_TOKEN_EXPIRES` in `.env`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Author

MDrive - Cloud Storage Application

## Support

For issues and questions, please open an issue on the GitHub repository.
