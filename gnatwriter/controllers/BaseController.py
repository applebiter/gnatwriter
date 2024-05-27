from typing import Type
from sqlalchemy.orm import Session
from gnatwriter.models import User


class BaseController:
    """Base controller encapsulates common functionality for all controllers

    Attributes
    ----------
    _instance : BaseController
        The instance of the base controller
    _owner : User
        The current user of the base controller
    _session : Session
        The database session
    """
    _instance = None
    _path_to_config = None
    _owner = None
    _session = None

    def __new__(cls, path_to_config: str, session: Session, owner: Type[User]):
        """Enforce Singleton pattern"""

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(
        self, path_to_config: str, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        self._path_to_config = path_to_config
        self._session = session
        self._owner = owner
