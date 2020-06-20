from datetime import datetime

import flask
import pytest
from flask_ddd_repository import FlaskDDDRepository


@pytest.fixture
def sqlalchemy_binds():
    return [
        {
            'bind_name': 'test_sqlite_memory',
            'db_type': 'sqlite',
            'db_host': ':memory:',
            'db_port': None,
            'db_name': None,
            'db_user': None,
            'db_password': None,
        }
    ]


@pytest.fixture(scope='function')
def app(sqlalchemy_binds, request):
    app = flask.Flask(request.module.__name__)
    app.testing = True
    return app


@pytest.fixture
def repo(app):
    app.config["SQLALCHEMY_BINDS"] = sqlalchemy_binds
    return FlaskDDDRepository(app)

# @pytest.fixture
# def Todo(db):
#     class Todo(db.Model):
#         __tablename__ = "todos"
#         id = db.Column("todo_id", db.Integer, primary_key=True)
#         title = db.Column(db.String(60))
#         text = db.Column(db.String)
#         done = db.Column(db.Boolean)
#         pub_date = db.Column(db.DateTime)
#
#         def __init__(self, title, text):
#             self.title = title
#             self.text = text
#             self.done = False
#             self.pub_date = datetime.utcnow()
#
#     db.create_all()
#     yield Todo
#     db.drop_all()