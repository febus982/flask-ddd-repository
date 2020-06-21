from abc import ABC
from datetime import datetime
from typing import Optional, Type

from .factory import Factory


class Model(ABC):
    """
    Base model class to be used for all entities.
    """

    __factory: Type = Factory
    # TODO: Implement metaclass to check for variables assignment
    __repository: Type

    @classmethod
    def get_factory(cls):
        """
        Returns the factory for this model

        :return:
        """
        return cls.__factory(cls)

    @classmethod
    def get_repository(cls):
        """
        Returns the repository for this model

        :return:
        """
        return cls.__repository(cls)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
