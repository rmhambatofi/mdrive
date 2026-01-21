"""
Validation utilities module.
Provides validation functions for user inputs.
"""
import re
import os
from werkzeug.utils import secure_filename


def validate_email(email):
    """
    Validate email format.

    Args:
        email (str): Email address to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not email or len(email) > 255:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Validate password strength.
    Requirements: At least 8 characters, 1 uppercase, 1 lowercase, 1 number

    Args:
        password (str): Password to validate

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    return True, ""


def validate_filename(filename, allowed_extensions=None):
    """
    Validate and sanitize filename.

    Args:
        filename (str): Original filename
        allowed_extensions (set, optional): Set of allowed extensions

    Returns:
        tuple: (bool, str, str) - (is_valid, sanitized_filename, error_message)
    """
    if not filename:
        return False, None, "Filename is required"

    # Sanitize filename
    sanitized = secure_filename(filename)

    if not sanitized:
        return False, None, "Invalid filename"

    # Check for dangerous patterns
    dangerous_patterns = ['..', '/', '\\', '\0']
    if any(pattern in filename for pattern in dangerous_patterns):
        return False, None, "Filename contains invalid characters"

    # Validate extension if required
    if allowed_extensions:
        extension = sanitized.rsplit('.', 1)[1].lower() if '.' in sanitized else ''
        if extension not in allowed_extensions:
            return False, None, f"File type .{extension} is not allowed"

    return True, sanitized, ""


def validate_file_size(file_size, max_size):
    """
    Validate file size.

    Args:
        file_size (int): File size in bytes
        max_size (int): Maximum allowed size in bytes

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if file_size <= 0:
        return False, "File is empty"

    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        return False, f"File size exceeds maximum allowed size of {max_mb:.0f}MB"

    return True, ""


def sanitize_path(path):
    """
    Sanitize file path to prevent path traversal attacks.

    Args:
        path (str): Path to sanitize

    Returns:
        str: Sanitized path
    """
    # Remove any path traversal attempts
    path = path.replace('..', '').replace('~', '')

    # Normalize path separators
    path = os.path.normpath(path)

    # Remove leading slashes
    path = path.lstrip('/\\')

    return path
