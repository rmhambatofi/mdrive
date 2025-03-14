# MDrive - File Storage Service

MDrive is a secure file storage service built with Flask, offering user authentication and file management capabilities.

## Features

- User authentication with JWT tokens
- Secure file upload and storage
- File management operations (upload, download, delete)
- Docker support for easy deployment

## Tech Stack

- Python/Flask - Backend framework
- Flask-JWT-Extended - Authentication
- SQLAlchemy - Database ORM
- Docker - Containerization

## Getting Started

### Prerequisites

- Python 3.x
- Docker and Docker Compose (for containerized setup)
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mdrive
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a .env file in the project root with the following variables:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:password@localhost:5432/mdrive
   ```

### Running with Docker

1. Start the services using Docker Compose:
   ```bash
   docker-compose up -d
   ```

2. The application will be available at `http://localhost:5000`

## API Documentation

### Authentication

#### Register a new user
```
POST /api/auth/register
Content-Type: application/json

{
    "username": "user123",
    "email": "user@example.com",
    "password": "secure_password"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
    "username": "user123",
    "password": "secure_password"
}
```

### File Operations

#### Upload File
```
POST /api/files/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

form-data:
  file: <file>
```

#### Download File
```
GET /api/files/download/<file_id>
Authorization: Bearer <access_token>
```

#### List Files
```
GET /api/files/list
Authorization: Bearer <access_token>
```

## Development

### Project Structure
```
mdrive/
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   └── files.py
│   ├── models/
│   │   ├── file.py
│   │   └── user.py
│   └── services/
│       ├── auth_service.py
│       ├── file_service.py
│       └── storage_service.py
├── config.py
├── app.py
└── docker-compose.yml
```

### Running Tests
```bash
python -m pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.