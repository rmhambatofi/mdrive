import os
from app import create_app, db
from app.models.user import User
from app.models.file import File

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, File=File)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
