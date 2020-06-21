import flask
import pytest
from flask_ddd_repository import FlaskDDDRepository, get_managers, DB_MANAGER_SQLALCHEMY
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper


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
def repo(app, sqlalchemy_binds):
    app.config["SQLALCHEMY_BINDS"] = sqlalchemy_binds
    return FlaskDDDRepository(app)


@pytest.fixture
def Model(app, repo):
    class Model(repo.Model):
        def __init__(self, name, lastname):
            self.name = name
            self.lastname = lastname

    table_name = 'model'
    bind_name = 'test_sqlite_memory'
    manager = get_managers(repo.get_app())[DB_MANAGER_SQLALCHEMY]
    meta = manager.metadata()[bind_name]
    manager = get_managers(app)[DB_MANAGER_SQLALCHEMY]
    meta = manager.metadata()[bind_name]
    test_table = Table(
        table_name, meta,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('lastname', String),
    )
    mapper(Model, test_table)
    meta.create_all()
    yield Model
    meta.drop_all()
