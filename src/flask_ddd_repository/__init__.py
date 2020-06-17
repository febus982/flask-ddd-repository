from typing import List

from flask import _app_ctx_stack, Flask

from .model import Model
from .factory import Factory
from .db_manager.sqlalchemy import SQLAlchemyManager

__version__ = "1.0.0.dev"


class FlaskDDDRepository:
    DB_MANAGER_SQLALCHEMY = 'sqlalchemy'

    Model = Model
    Factory = Factory

    def __init__(self, app: Flask = None, db_managers: List[str] = [DB_MANAGER_SQLALCHEMY]):
        self.app = app
        if app is not None:
            self.init_app(app, db_managers)

    def init_app(self, app: Flask, db_managers: List[str] = [DB_MANAGER_SQLALCHEMY]):
        if self.DB_MANAGER_SQLALCHEMY in db_managers:
            SQLAlchemyManager.init()
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        pass
        # ctx = _app_ctx_stack.top
        # if hasattr(ctx, 'sqlite3_db'):
        #     ctx.sqlite3_db.close()
