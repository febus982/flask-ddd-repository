from unittest.mock import patch, PropertyMock

from flask import Flask
from flask_ddd_repository import FlaskDDDRepository, DB_MANAGER_SQLALCHEMY, _FlaskDDDRepositoryState, _get_managers
from flask_ddd_repository.db_manager.sqlalchemy import SQLAlchemyManager


class TestFlaskDDDRepository:
    @patch.object(FlaskDDDRepository, 'init_app')
    def test_init_triggers_init_only_if_app_passed(self, mocked_init_app, app):
        FlaskDDDRepository()
        mocked_init_app.assert_not_called()
        FlaskDDDRepository(app)
        mocked_init_app.assert_called_once_with(app, (DB_MANAGER_SQLALCHEMY,))

    def test_init_app_adds_state_to_extensions(self, app):
        FlaskDDDRepository(app)
        assert isinstance(app.extensions['ddd_repository'], _FlaskDDDRepositoryState)

    @patch.object(SQLAlchemyManager, '__init__', return_value=None)
    def test_init_app_initialise_wanted_managers(self, mocked_manager_init, app):
        repo = FlaskDDDRepository()
        repo.init_app(app, (DB_MANAGER_SQLALCHEMY,))
        mocked_manager_init.assert_called_once()
        assert isinstance(_get_managers(app).get(DB_MANAGER_SQLALCHEMY), SQLAlchemyManager)

    @patch.object(FlaskDDDRepository, '_FlaskDDDRepository__db_managers_registry', new_callable=PropertyMock)
    @patch.object(SQLAlchemyManager, '__init__', return_value=None)
    def test_init_app_doesnt_initialise_managers_if_not_in_registry(self, mocked_manager_init, mocked_registry, app):
        mocked_registry.return_value = {}
        repo = FlaskDDDRepository()
        repo.init_app(app, (DB_MANAGER_SQLALCHEMY,))
        mocked_manager_init.assert_not_called()
        assert not _get_managers(app).get(DB_MANAGER_SQLALCHEMY)

    def test_init_app_add_context_teardown_function_to_app(self, app: Flask):
        repo = FlaskDDDRepository()
        repo.init_app(app, (DB_MANAGER_SQLALCHEMY,))
        assert repo.teardown in app.teardown_appcontext_funcs

