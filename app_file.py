from flask_migrate import Migrate
from config import Config
from browsers_app import create_app, db
import unittest

app = create_app(Config)
migrate = Migrate(app, db)

@app.cli.command('test')
def test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
