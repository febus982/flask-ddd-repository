from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import List, Union

from flask import current_app
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.orm import Session, Query

from . import get_managers, DB_MANAGER_SQLALCHEMY
from .db_manager.sqlalchemy import SQLAlchemyManager
from .exceptions import ModelNotFoundException
from .model import Model


class AbstractRepository(ABC):
    """
    Base class to be used for all repositories.
    """

    def __init__(self, model_class: type) -> None:
        super().__init__()
        self._model_class = model_class

    @abstractmethod
    def find_one(self, primary_key_value: Union[str, int], include_soft_deleted=False):
        pass

    @abstractmethod
    def find_many(self, search_filter: dict, limit: int = 50, offset: int = 0, include_soft_deleted: bool = False):
        pass

    @abstractmethod
    def insert_one(self, model: Model):
        pass

    @abstractmethod
    def insert_many(self, models: List[Model]):
        pass

    @abstractmethod
    def update_one(self, model: Model, upsert=False):
        pass

    @abstractmethod
    def update_many(self, models: List[Model], upsert=False):
        pass

    @abstractmethod
    def delete_one(self, primary_key_value: Union[str, int], soft_delete: bool = True):
        pass

    @abstractmethod
    def delete_many(self, primary_key_value: Union[List[str], List[int]], soft_delete: bool = True):
        pass

    @abstractmethod
    def restore_one(self, primary_key_value: Union[str, int]):
        pass

    @abstractmethod
    def restore_many(self, primary_key_value: Union[List[str], List[int]]):
        pass


class SQLAlchemyRepository(AbstractRepository):
    """
    Generic repository which uses SQLAlchemy ORM persistence layer
    """

    @contextmanager
    def _managed_session(self, parent_session: Session = None):
        if not parent_session:
            session = self._get_manager().create_session()
            assert isinstance(session.get_bind(self._model_class), (Engine, Connection))
            try:
                yield session
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()
        else:
            assert isinstance(parent_session.get_bind(self._model_class), (Engine, Connection))
            # Should we flush here?
            yield parent_session

    def _get_manager(self) -> SQLAlchemyManager:
        return get_managers(current_app._get_current_object())[DB_MANAGER_SQLALCHEMY]

    def _query(self, session: Session) -> Query:
        return session.query(self._model_class)

    def _find_model_or_fail(self, session: Session, primary_key_value: Union[str, int],
                            include_soft_deleted: bool = False):
        model = self._query(session).get(primary_key_value)
        if not model:
            raise ModelNotFoundException(f"Model not found with primary key value: {primary_key_value}")

        # if model is None \
        #         or (not include_soft_deleted and isinstance(model, AbstractSoftDeleteMixin) and model.is_deleted):
        #     raise EntityNotFoundException(f"Entity not found with primary key value: {primary_key_value}")
        #
        return model

    def find_one(self, primary_key_value: Union[str, int], include_soft_deleted: bool = False):
        with self._managed_session() as managed_session:
            return self._find_model_or_fail(managed_session, primary_key_value)

    def find_many(self, search_filter: dict, limit: int = 50, offset: int = 0, include_soft_deleted=False):
        limit = int(max(0, limit))
        offset = int(min(offset, 0))
        with self._managed_session() as session:
            query = self._query(session)
            query.filter_by(**search_filter)
            query.limit(limit)
            query.offset(offset)
            return query.all()

    def insert_one(self, model: Model, session: Session = None):
        with self._managed_session(session) as managed_session:
            managed_session.add(model)
        return model

    def insert_many(self, models: List[Model], session: Session = None):
        with self._managed_session(session) as managed_session:
            for model in models:
                managed_session.add(model)
        return models

    def update_one(self, model: Model, upsert=False, session: Session = None):
        pass
        # with self._managed_session(session) as managed_session:
        #     model_from_db = self._find_model_or_fail(managed_session, getattr(model, model.primary_key))
        #     managed_session.add(model)
        # return self.find_one(getattr(model, model.primary_key))

    def update_many(self, models: List[Model], upsert=False) -> List[Model]:
        pass

    def delete_one(self, primary_key_value: Union[str, int], soft_delete=True) -> bool:
        pass

    def delete_many(self, primary_key_value: Union[List[str], List[int]], soft_delete=True) -> bool:
        pass

    def restore_one(self, primary_key_value: Union[str, int]) -> Model:
        pass

    def restore_many(self, primary_key_value: Union[List[str], List[int]]) -> List[Model]:
        pass
