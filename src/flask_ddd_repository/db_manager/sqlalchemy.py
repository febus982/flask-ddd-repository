import os
import re
from typing import Dict, Optional, Union

from flask import current_app as app, g
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql.schema import MetaData


class SQLAlchemyManager:
    @classmethod
    def init(cls):
        if not app.config.get('SQLALCHEMY_BINDS'):
            cls._init_from_env_vars()
        else:
            for bind in app.config.get('SQLALCHEMY_BINDS', []):
                cls.init_bind(**bind)

    @classmethod
    def init_bind(
            cls,
            bind_name: str,
            db_type: str = 'sqlite',
            db_host: str = ':memory',
            db_port: Optional[int] = None,
            db_name: Optional[str] = None,
            db_user: Optional[str] = None,
            db_password: Optional[str] = None,
    ):
        if not cls.metadata().get(bind_name):
            cls.metadata()[bind_name] = MetaData(
                bind=cls._create_engine(
                    db_type=db_type,
                    db_host=db_host,
                    db_port=db_port,
                    db_name=db_name,
                    db_user=db_user,
                    db_password=db_password,
                )
            )
        else:
            # TODO: Create specific Exception
            raise Exception("Already defined")

    @classmethod
    def _create_engine(
            cls,
            db_type: str,
            db_host: str,
            db_port: Optional[int] = None,
            db_name: Optional[str] = None,
            db_user: Optional[str] = None,
            db_password: Optional[str] = None,
    ) -> Engine:
        if db_type == 'sqlite':
            sqlalchemy_db_uri = f'{db_type}://{"/" if db_host else ""}{db_host}'
            return create_engine(
                sqlalchemy_db_uri,
                echo=app.debug,
                echo_pool=app.debug,
                # execution_options=app.config.get('SQLALCHEMY_EXECUTION_OPTIONS', {}),
            )
        else:
            sqlalchemy_db_uri = f'{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
            return create_engine(
                sqlalchemy_db_uri,
                echo=app.debug,
                echo_pool=app.debug,
                # execution_options=app.config.get('SQLALCHEMY_EXECUTION_OPTIONS', {}),
                max_overflow=5,
                pool_size=10,
                pool_recycle=120,
            )

    @classmethod
    def create_session(cls, bind_name: str = None) -> Session:
        if not bind_name:
            session = sessionmaker(
                binds={
                    table: meta.bind
                    for meta in cls.metadata().values()
                    for table in meta.tables.values()
                }
            )
        elif cls.binds().get(bind_name):
            session = sessionmaker(bind=cls.binds().get(bind_name))
        else:
            # TODO: Create specific Exception
            raise Exception(f"Bind '{bind_name}' not initialised")

        return session()

    @classmethod
    def binds(cls) -> Dict[str, Union[Engine, Connection, None]]:
        return {key: metadata.bind for key, metadata in cls.metadata().items()}

    @classmethod
    def metadata(cls) -> Dict[str, MetaData]:
        app_context_key = f'{cls.__qualname__}_metadata'
        if app_context_key not in g:
            setattr(g, app_context_key, {})
        return getattr(g, app_context_key)

    @classmethod
    def _init_from_env_vars(cls) -> None:
        regex = re.compile(r'SQLALCHEMY_(\d*)_(\w*)')
        binds: Dict[int, dict] = {}
        for key, value in os.environ.items():
            match = regex.match(key)
            if match:
                if not isinstance(binds.get(int(match.group(1))), dict):
                    binds[int(match.group(1))] = {}
                binds[int(match.group(1))][match.group(2).lower()] = os.path.expandvars(value)

        for bind in binds.values():
            cls.init_bind(**bind)
