import os
from unittest.mock import patch

from flask import Flask
from flask_ddd_repository.db_manager.sqlalchemy import SQLAlchemyManager
from pytest import raises
from sqlalchemy import MetaData
from sqlalchemy.engine.base import Engine


class TestSQLAlchemyManager:
    init_params = {
        'db_type': 'sqlite',
        'db_host': ':memory:',
        'db_port': None,
        'db_name': None,
        'db_user': None,
        'db_password': None,
    }

    @patch.object(SQLAlchemyManager, 'init_bind')
    def test_init_uses_config_if_available(self, mocked_init_bind, app: Flask):
        app.config['SQLALCHEMY_BINDS'] = [self.init_params]
        SQLAlchemyManager(app)
        mocked_init_bind.assert_called_once_with(**self.init_params)

    @patch.object(SQLAlchemyManager, '_init_from_env_vars', return_value=None)
    def test_init_uses_env_vars_if_config_not_available(self, mocked_init_from_env_vars, app: Flask):
        SQLAlchemyManager(app)
        mocked_init_from_env_vars.assert_called_once()

    @patch.dict(os.environ, {
        'SQLALCHEMY_0_BIND_NAME': 'test_bind',
        'SQLALCHEMY_0_DB_TYPE': 'sqlite',
        'SQLALCHEMY_0_DB_HOST': ':memory:',
    })
    @patch.object(SQLAlchemyManager, 'init_bind')
    def test_init_from_env_vars_parses_environment(self, mocked_init_bind, app):
        SQLAlchemyManager(app)
        mocked_init_bind.assert_called_once_with(
            bind_name='test_bind',
            db_type='sqlite',
            db_host=':memory:',
        )

    @patch.object(SQLAlchemyManager, '_create_engine')
    def test_init_bind_creates_db_engine_and_metadata(self, mocked_create_engine, app: Flask):
        manager = SQLAlchemyManager(app)
        manager.init_bind(bind_name='test_bind', **self.init_params)
        mocked_create_engine.assert_called_once_with(**self.init_params)
        assert isinstance(manager.metadata()['test_bind'], MetaData)

    def test_init_bind_fails_when_bind_is_already_initialised(self, app: Flask):
        manager = SQLAlchemyManager(app)
        manager.init_bind(bind_name='test_bind', **self.init_params)
        with raises(Exception):
            manager.init_bind(bind_name='test_bind', **self.init_params)

    @patch.object(SQLAlchemyManager, '_create_engine')
    def test_init_bind_initialise_correctly_multiple_binds(self, mocked_create_engine, app: Flask):
        manager = SQLAlchemyManager(app)
        manager.init_bind(bind_name='test_bind', **self.init_params)
        manager.init_bind(bind_name='additional_bind', **self.init_params)
        mocked_create_engine.assert_called_with(**self.init_params)
        assert mocked_create_engine.call_count == 2
        assert isinstance(manager.metadata()['test_bind'], MetaData)
        assert isinstance(manager.metadata()['additional_bind'], MetaData)

    @patch('flask_ddd_repository.db_manager.sqlalchemy.create_engine')
    def test_create_engine_forwards_correctly_sqlite_parameters(self, mocked_sqlalchemy_create_engine, app):
        manager = SQLAlchemyManager(app)
        manager._create_engine(**self.init_params)
        mocked_sqlalchemy_create_engine.assert_called_once_with(
            f'{self.init_params["db_type"]}:///{self.init_params["db_host"]}',
            echo=app.debug,
            echo_pool=app.debug,
        )

    @patch('flask_ddd_repository.db_manager.sqlalchemy.create_engine')
    def test_create_engine_forwards_correctly_db_parameters(self, mocked_sqlalchemy_create_engine, app):
        db_init_params = {
            'db_type': 'postgres',
            'db_host': ':memory:',
            'db_port': None,
            'db_name': None,
            'db_user': None,
            'db_password': None,
        }
        manager = SQLAlchemyManager(app)
        manager._create_engine(**db_init_params)
        mocked_sqlalchemy_create_engine.assert_called_once_with(
            f'{db_init_params["db_type"]}://{db_init_params["db_user"]}:{db_init_params["db_password"]}@{db_init_params["db_host"]}:{db_init_params["db_port"]}/{db_init_params["db_name"]}',
            echo=app.debug,
            echo_pool=app.debug,
            max_overflow=5,
            pool_size=10,
            pool_recycle=120,
        )

    def test_create_session_return_unbound_session_by_default(self, app: Flask):
        manager = SQLAlchemyManager(app)
        manager.init_bind(bind_name='test_bind', **self.init_params)
        session = manager.create_session()
        assert session.bind is None

    def test_create_session_return_bound_session_if_bind_initialised(self, app: Flask):
        manager = SQLAlchemyManager(app)
        manager.init_bind(bind_name='test_bind', **self.init_params)
        session = manager.create_session('test_bind')
        assert isinstance(session.bind, Engine)

    def test_create_session_raises_exception_if_bind_not_initialised(self, app: Flask):
        manager = SQLAlchemyManager(app)
        manager.init_bind(bind_name='test_bind', **self.init_params)
        with raises(Exception):
            manager.create_session("not_initialised_bind_name")
