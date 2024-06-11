from configparser import ConfigParser
from typing import Type
from sqlalchemy.orm import Session
from gnatwriter.models import User


class BaseController:
    """Base controller encapsulates common functionality for all controllers

    Attributes
    ----------
    _instance : BaseController
        The instance of the base controller
    _config : ConfigParser
        The configuration parser
    _owner : User
        The current user of the base controller
    _session : Session
        The database session
    """
    _instance = None
    _config = None
    _owner = None
    _session = None

    def __new__(cls, config: ConfigParser, session: Session, owner: Type[User]):
        """Enforce Singleton pattern"""

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        self._config = config
        self._session = session
        self._owner = owner
