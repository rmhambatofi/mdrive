# MDrive API Documentation

Complete API documentation for the MDrive cloud storage application.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Response Format

All API responses follow this format:

### Success Response
```json
{
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": "Additional error details (optional)"
}
```

---

## Authentication Endpoints

### Register User

Create a new user account.

**Endpoint:** `POST /auth/register`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

**Success Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "storage_quota": 5368709120,
    "storage_used": 0,
    "storage_available": 5368709120,
    "created_at": "2024-01-15T10:30:00"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `400 Bad Request`: Invalid email format or weak password
- `409 Conflict`: Email already registered

---

### Login

Authenticate and receive a JWT token.

**Endpoint:** `POST /auth/login`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "storage_quota": 5368709120,
    "storage_used": 1048576,
    "storage_available": 5367660544,
    "created_at": "2024-01-15T10:30:00"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `400 Bad Request`: Missing email or password
- `401 Unauthorized`: Invalid credentials

---

### Get Profile

Get current user's profile information.

**Endpoint:** `GET /auth/profile`

**Authentication:** Required

**Success Response (200):**
```json
{
  "user": {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "storage_quota": 5368709120,
    "storage_used": 1048576,
    "storage_available": 5367660544,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `404 Not Found`: User not found

---

### Update Profile

Update user profile information.

**Endpoint:** `PUT /auth/profile`

**Authentication:** Required

**Request Body:**
```json
{
  "full_name": "John Smith"
}
```

**Success Response (200):**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Smith",
    "storage_quota": 5368709120,
    "storage_used": 1048576,
    "storage_available": 5367660544,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

---

## File Management Endpoints

### Upload File

Upload a file to the storage.

**Endpoint:** `POST /files/upload`

**Authentication:** Required

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file` (required): The file to upload
- `parent_folder_id` (optional): ID of parent folder

**Success Response (201):**
```json
{
  "message": "File uploaded successfully",
  "file": {
    "id": 42,
    "user_id": 1,
    "parent_folder_id": null,
    "file_name": "document.pdf",
    "file_path": "document.pdf",
    "file_size": 1048576,
    "mime_type": "application/pdf",
    "is_folder": false,
    "created_at": "2024-01-15T11:30:00",
    "updated_at": "2024-01-15T11:30:00"
  }
}
```

**Error Responses:**
- `400 Bad Request`: No file provided, invalid file type, or file too large
- `403 Forbidden`: Storage quota exceeded
- `404 Not Found`: Parent folder not found
- `409 Conflict`: File already exists

---

### Get Files

List files and folders.

**Endpoint:** `GET /files`

**Authentication:** Required

**Query Parameters:**
- `folder_id` (optional): Parent folder ID (omit for root)
- `page` (optional, default: 1): Page number
- `per_page` (optional, default: 50): Items per page

**Example:** `GET /files?folder_id=5&page=1&per_page=20`

**Success Response (200):**
```json
{
  "files": [
    {
      "id": 42,
      "user_id": 1,
      "parent_folder_id": null,
      "file_name": "document.pdf",
      "file_path": "document.pdf",
      "file_size": 1048576,
      "mime_type": "application/pdf",
      "is_folder": false,
      "icon": "pdf",
      "created_at": "2024-01-15T11:30:00",
      "updated_at": "2024-01-15T11:30:00"
    },
    {
      "id": 43,
      "user_id": 1,
      "parent_folder_id": null,
      "file_name": "Photos",
      "file_path": "Photos",
      "file_size": 0,
      "mime_type": null,
      "is_folder": true,
      "icon": "folder",
      "created_at": "2024-01-15T10:00:00",
      "updated_at": "2024-01-15T10:00:00"
    }
  ],
  "breadcrumb": [],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 2,
    "pages": 1
  }
}
```

---

### Get File Info

Get detailed information about a specific file or folder.

**Endpoint:** `GET /files/<file_id>`

**Authentication:** Required

**Success Response (200):**
```json
{
  "file": {
    "id": 42,
    "user_id": 1,
    "parent_folder_id": null,
    "file_name": "document.pdf",
    "file_path": "document.pdf",
    "file_size": 1048576,
    "mime_type": "application/pdf",
    "is_folder": false,
    "created_at": "2024-01-15T11:30:00",
    "updated_at": "2024-01-15T11:30:00"
  },
  "breadcrumb": [
    {
      "id": 42,
      "name": "document.pdf",
      "is_folder": false
    }
  ]
}
```

**Error Responses:**
- `404 Not Found`: File not found

---

### Download File

Download a file.

**Endpoint:** `GET /files/download/<file_id>`

**Authentication:** Required

**Success Response (200):**
- Returns the file as a binary stream
- Headers include:
  - `Content-Type`: File MIME type
  - `Content-Disposition`: attachment; filename="document.pdf"

**Error Responses:**
- `400 Bad Request`: Cannot download a folder
- `404 Not Found`: File not found or not on storage

---

### Delete File

Delete a file or folder (including all contents).

**Endpoint:** `DELETE /files/<file_id>`

**Authentication:** Required

**Success Response (200):**
```json
{
  "message": "File deleted successfully"
}
```

**Error Responses:**
- `404 Not Found`: File not found
- `500 Internal Server Error`: Failed to delete file

---

### Create Folder

Create a new folder.

**Endpoint:** `POST /files/folder`

**Authentication:** Required

**Request Body:**
```json
{
  "folder_name": "My Documents",
  "parent_folder_id": null
}
```

**Success Response (201):**
```json
{
  "message": "Folder created successfully",
  "folder": {
    "id": 44,
    "user_id": 1,
    "parent_folder_id": null,
    "file_name": "My Documents",
    "file_path": "My Documents",
    "file_size": 0,
    "mime_type": null,
    "is_folder": true,
    "created_at": "2024-01-15T12:00:00",
    "updated_at": "2024-01-15T12:00:00"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid folder name
- `404 Not Found`: Parent folder not found
- `409 Conflict`: Folder already exists

---

### Rename File

Rename a file or folder.

**Endpoint:** `PUT /files/<file_id>/rename`

**Authentication:** Required

**Request Body:**
```json
{
  "new_name": "renamed-document.pdf"
}
```

**Success Response (200):**
```json
{
  "message": "File renamed successfully",
  "file": {
    "id": 42,
    "user_id": 1,
    "parent_folder_id": null,
    "file_name": "renamed-document.pdf",
    "file_path": "renamed-document.pdf",
    "file_size": 1048576,
    "mime_type": "application/pdf",
    "is_folder": false,
    "created_at": "2024-01-15T11:30:00",
    "updated_at": "2024-01-15T12:30:00"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid name
- `404 Not Found`: File not found
- `409 Conflict`: Name already exists

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required or failed |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error |

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider implementing rate limiting on sensitive endpoints like login and registration.

## CORS

CORS is configured to allow requests from `http://localhost:3000` by default. Update the `CORS_ORIGINS` environment variable to add additional allowed origins.

## File Restrictions

### Allowed Extensions (Default)
pdf, doc, docx, txt, png, jpg, jpeg, gif, zip, rar, mp4, mp3

### Maximum File Size
100 MB (configurable via `MAX_FILE_SIZE` environment variable)

### Storage Quota
5 GB per user (configurable via `DEFAULT_STORAGE_QUOTA` environment variable)
