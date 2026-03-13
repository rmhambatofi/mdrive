"""
Custom Flask CLI commands.
"""
import click
from flask.cli import with_appcontext
from app import db
from app.models.user import User, UserRole
from app.utils.validators import validate_email, validate_password
from app.utils.helpers import ensure_directory_exists
from flask import current_app
import os


@click.command('create-admin')
@with_appcontext
def create_admin_command():
    """
    Interactively create an administrator account.

    Usage:
        flask create-admin
    """
    click.echo('')
    click.echo(click.style('=== Create Admin User ===', fg='cyan', bold=True))
    click.echo('')

    # --- Collect inputs ---

    # Full name
    full_name = click.prompt(
        click.style('Full name', fg='yellow'),
        default='',
    ).strip() or None

    # Email
    while True:
        email = click.prompt(click.style('Email', fg='yellow')).strip()
        if not validate_email(email):
            click.echo(click.style('  Invalid email format. Please try again.', fg='red'))
            continue
        if User.query.filter_by(email=email).first():
            click.echo(click.style(f'  A user with email "{email}" already exists.', fg='red'))
            continue
        break

    # Password
    while True:
        password = click.prompt(
            click.style('Password', fg='yellow'),
            hide_input=True
        )
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            click.echo(click.style(f'  {error_msg}', fg='red'))
            continue

        confirm = click.prompt(
            click.style('Confirm password', fg='yellow'),
            hide_input=True
        )
        if password != confirm:
            click.echo(click.style('  Passwords do not match. Please try again.', fg='red'))
            continue
        break

    # --- Create user ---
    click.echo('')

    try:
        user = User(
            email=email,
            password=password,
            full_name=full_name,
            role=UserRole.ADMIN,
        )
        db.session.add(user)
        db.session.commit()

        # Create user storage directory
        user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], user.uuid)
        ensure_directory_exists(user_dir)

        click.echo(click.style('Admin user created successfully!', fg='green', bold=True))
        click.echo(f"  UUID  : {user.uuid}")
        click.echo(f"  Name  : {user.full_name or '—'}")
        click.echo(f"  Email : {user.email}")
        click.echo(f"  Role  : {user.role.value}")
        click.echo('')

    except Exception as e:
        db.session.rollback()
        click.echo(click.style(f'Error: {str(e)}', fg='red', bold=True))
        raise SystemExit(1)


@click.command('cleanup-trash')
@click.option('--days', default=30, help='Delete items older than N days (default: 30)')
@with_appcontext
def cleanup_trash_command(days):
    """Permanently delete files in Recycle Bin older than N days. Usage: flask cleanup-trash"""
    from app.services.file_service import FileService

    click.echo(f'Cleaning up trash items older than {days} days...')
    try:
        count = FileService.cleanup_old_trash(days=days)
        click.echo(click.style(f'Done — {count} item(s) permanently deleted.', fg='green'))
    except Exception as e:
        click.echo(click.style(f'Error: {str(e)}', fg='red', bold=True))
        raise SystemExit(1)
