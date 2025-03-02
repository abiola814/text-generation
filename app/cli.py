import click
from flask.cli import with_appcontext
from .models import db

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.create_all()
    click.echo('Initialized the database.')

def register_commands(app):
    app.cli.add_command(init_db_command)