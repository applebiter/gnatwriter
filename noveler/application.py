import os
import time
import uuid as uniqueid
from configparser import ConfigParser
from datetime import datetime
from os.path import realpath

import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from noveler.controllers import ActivityController, AuthorController, BibliographyController, ChapterController, \
    CharacterController, EventController, ImageController, LinkController, AssistantController, \
    LocationController, NoteController, SceneController, StoryController, SubmissionController, UserController, \
    OllamaModelController, ExportController
from noveler.models import Base, User


def hash_password(password: str) -> str:
    """Hash a password, return hashed password"""

    if password == '':
        raise ValueError('The password cannot be empty.')

    if len(password) < 8:
        raise ValueError('The password must be at least 8 characters.')

    if len(password) > 24:
        raise ValueError('The password cannot be more than 24 characters.')

    return bcrypt.hashpw(
        password.encode('utf8'), bcrypt.gensalt(rounds=12)
    ).decode('utf8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password, return true if verified, false if not"""

    return bcrypt.checkpw(
        password.encode('utf8'), hashed_password.encode('utf8')
    )


def get_tick_count() -> int:
    """Return the current number of milliseconds that have elapsed since the app started"""
    return int(time.time() * 1000)


class Noveler:
    """Main application class for Noveler
    """
    _instance = None
    project_root: str = None
    database_type: str = None
    
    def __new__(cls):
        """Enforce Singleton pattern"""

        if cls._instance is None:
            cls._instance = super(Noveler, cls).__new__(cls)

        return cls._instance

    def __init__(self):

        filepath = realpath(__file__)
        self.project_root = os.path.dirname(os.path.dirname(filepath))
        config = ConfigParser()
        config.read(f"{self.project_root}/noveler.cfg")
        self.database_type = config.get("default_database", "type")

        if self.database_type == "sqlite":
            database = config.get("default_database", "database")
            self._engine = create_engine(f"sqlite:///{database}")
        elif self.database_type == "postgresql":
            user = config.get("default_database", "user")
            password = config.get("default_database", "password")
            host = config.get("default_database", "host")
            port = config.get("default_database", "port")
            database = config.get("default_database", "database")
            self._engine = create_engine(
                f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"
            )
        elif self.database_type == "mysql":
            user = config.get("default_database", "user")
            password = config.get("default_database", "password")
            host = config.get("default_database", "host")
            port = config.get("default_database", "port")
            database = config.get("default_database", "database")
            self._engine = create_engine(
                f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
            )

        Base.metadata.create_all(self._engine)
        self._session = Session(bind=self._engine, expire_on_commit=False)
        self._owner = self._session.query(User).filter(
            User.username == "noveler"
        ).first()

        if self._owner is None:
            new_uuid = str(uniqueid.uuid4())
            username = "noveler"
            password = hash_password("password")
            email = "noveler@example.com"
            is_active = True
            is_banned = False
            created = datetime.now()
            modified = created
            user = User(
                uuid=new_uuid, username=username, password=password,
                email=email, is_active=is_active, is_banned=is_banned,
                created=created, modified=modified
            )
            self._session.add(user)
            self._session.commit()

        self._controllers = {
            "activity": ActivityController(self._session, self._owner),
            "assistant": AssistantController(self._session, self._owner),
            "author": AuthorController(self._session, self._owner),
            "bibliography": BibliographyController(self._session, self._owner),
            "chapter": ChapterController(self._session, self._owner),
            "character": CharacterController(self._session, self._owner),
            "event": EventController(self._session, self._owner),
            "export": ExportController(self._session, self._owner),
            "image": ImageController(self._session, self._owner),
            "link": LinkController(self._session, self._owner),
            "location": LocationController(self._session, self._owner),
            "note": NoteController(self._session, self._owner),
            "ollama-model": OllamaModelController(self._session, self._owner),
            "scene": SceneController(self._session, self._owner),
            "story": StoryController(self._session, self._owner),
            "submission": SubmissionController(self._session, self._owner),
            "user": UserController(self._session, self._owner)
        }

    def __call__(self, *args, **kwargs):
        return self._controllers[args[0]]

    def __str__(self):
        return "Noveler Application [alpha]"

    def __repr__(self):
        return f"{self.__class__.__name__}()"
