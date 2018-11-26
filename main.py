from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from info import create_app

app = create_app("dev")
mgr = Manager(app)
mgr.add_command("mc", MigrateCommand)

if __name__ == '__main__':
    mgr.run()