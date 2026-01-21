"""
Helper utilities module.
Provides miscellaneous helper functions.
"""
import os
import mimetypes


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"


def get_mime_type(filename):
    """
    Get MIME type from filename.

    Args:
        filename (str): Name of the file

    Returns:
        str: MIME type or 'application/octet-stream' if unknown
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def get_file_icon(mime_type, is_folder=False):
    """
    Get appropriate icon name for file type.

    Args:
        mime_type (str): MIME type of the file
        is_folder (bool): Whether this is a folder

    Returns:
        str: Icon identifier
    """
    if is_folder:
        return 'folder'

    if not mime_type:
        return 'file'

    icon_mapping = {
        'image/': 'image',
        'video/': 'video',
        'audio/': 'audio',
        'application/pdf': 'pdf',
        'application/msword': 'document',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document',
        'application/vnd.ms-excel': 'spreadsheet',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'spreadsheet',
        'application/zip': 'archive',
        'application/x-rar-compressed': 'archive',
        'text/': 'text',
    }

    for pattern, icon in icon_mapping.items():
        if mime_type.startswith(pattern):
            return icon

    return 'file'


def ensure_directory_exists(directory_path):
    """
    Ensure a directory exists, create if it doesn't.

    Args:
        directory_path (str): Path to directory

    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory_path}: {str(e)}")
        return False
