from app.config import Config
from app.extensions import db, login_manager
from app.blueprints.admin import admin_bp
from app.blueprints.users import user_bp
import click
from app.models import Role
from app.dummies import fake_admin, fake_user, add_service
from flask import Flask

# Registering blueprints and system configs
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_blueprints(app)
    register_extensions(app)
    return app


def register_blueprints(app):
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)

# add terminal commands for simple manipulations
def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Drop before create.')
    def initdb(drop):
        if drop:
            click.confirm('This operation will delete the database, are you sure to continue', abort=True)
            db.drop_all()
            click.echo('Drop tables')
        db.create_all()
        click.echo('Initialized database')

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Drop before create')
    def init(drop):
        if drop:
            click.confirm('This operation will delete the database, are you sure to continue', abort=True)
            db.drop_all()
            click.echo('Drop tables')
        click.echo('Initializing database')
        db.create_all()

        click.echo('Initializing roles')
        Role.insert_roles()

        click.echo('Done.')

# register dummy users for testing
def register_dummies(app, drop=False):
    if drop:
        click.echo('Dropping tables...')
        db.drop_all()
        click.echo('Creating database...')
        db.create_all()
        click.echo('Initializing roles and permissions...')
        Role.insert_roles()
        db.session.commit()
    click.echo('Generating administrator...')
    fake_admin()
    click.echo('Generating user...')
    fake_user()
    click.echo('Initializing service...')
    add_service('haircut', 10.00)
    add_service('hair wash & dry', 20.00)
    add_service('hair color', 40.00)
    click.echo('Done')


app = create_app()

if __name__ == '__main__':
    app.run()
