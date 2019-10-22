from config import db
from flask_migrate import Migrate, MigrateCommand
from router import app
from flask_script import Manager, Command
from player.controllers import add_samples

migrate = Migrate(db=db, app=app)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def DropDB():
    db.drop_all()


@manager.command
def sample_players():
    add_samples()


if __name__ == '__main__':
    manager.run()