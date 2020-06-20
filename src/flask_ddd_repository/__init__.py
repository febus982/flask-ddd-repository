from __future__ import annotations

from typing import Dict, Tuple, Union, Optional

from flask import Flask, current_app

from .db_manager.base import StorageManager
from .db_manager.sqlalchemy import SQLAlchemyManager
from .model import Model

__version__ = "1.0.0.dev"

DB_MANAGER_SQLALCHEMY = 'sqlalchemy'


class FlaskDDDRepository:
    Model = Model

    __db_managers_registry: Dict[str, type] = {
        DB_MANAGER_SQLALCHEMY: SQLAlchemyManager,
    }

    def __init__(self, app: Flask = None, db_managers: Tuple[str] = (DB_MANAGER_SQLALCHEMY,)):
        self.app = app
        if app is not None:
            self.init_app(app, db_managers)

    def init_app(self, app: Flask, db_managers: Tuple[str] = (DB_MANAGER_SQLALCHEMY,)):
        app.extensions['ddd_repository'] = state = _FlaskDDDRepositoryState(self)
        for manager in db_managers:
            validated_manager = self.__db_managers_registry.get(manager)
            if validated_manager:
                state.managers[manager] = validated_manager(app)
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        for manager in _get_state(self.get_app()).managers.values():
            # TODO: implement managers teardown
            pass

    def get_app(self):
        if current_app:
            return current_app._get_current_object()

        if self.app is not None:
            return self.app

        raise RuntimeError("No application found. Either work inside a view function or push an application context")


def _get_state(app: Flask) -> _FlaskDDDRepositoryState:
    if 'ddd_repository' not in app.extensions.keys():
        raise RuntimeError("flask_ddd_repository has not been initialised.")

    return app.extensions['ddd_repository']


def _get_managers(app: Flask, manager: Optional[str] = None) -> Union[StorageManager, Dict[str, StorageManager]]:
    managers = _get_state(app).managers
    if manager:
        assert manager in managers.keys()
        return managers.get(manager)

    return managers


class _FlaskDDDRepositoryState:
    """Configuration state for the flask_ddd_repository extension."""

    def __init__(self, repo: FlaskDDDRepository):
        self.repo = repo
        self.managers: Dict[str, StorageManager] = {}
