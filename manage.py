from config import db
from flask_migrate import Migrate, MigrateCommand
from router import app
from flask_script import Manager, Command

migrate = Migrate(db=db, app=app)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def DropDB():
    db.drop_all()


if __name__ == '__main__':
    manager.run()