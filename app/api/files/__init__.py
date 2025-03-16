from flask import Blueprint

files = Blueprint('files', __name__)

# Import all controllers
from app.api.files.file_controller import *
from app.api.files.folder_controller import *