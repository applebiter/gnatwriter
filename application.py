import json
import uuid as uniqueid
from sqlalchemy import create_engine
from controllers import *
from models import *


class Application:
    def __init__(self, engine: str, echo: bool = False):
        self._engine = create_engine(engine, echo=echo)
        Base.metadata.create_all(self._engine)
        self._session = Session(bind=self._engine, expire_on_commit=False)
        self._owner = self._session.query(User).filter(User.username == "noveler").first()
        if self._owner is None:
            new_uuid = str(uniqueid.uuid4())
            username = "noveler"
            password = hash_password("password")
            email = "noveler@example.com"
            is_active = True
            is_banned = False
            created = datetime.now()
            modified = created
            user = User(uuid=new_uuid, username=username, password=password, email=email, is_active=is_active,
                        is_banned=is_banned, created=created, modified=modified)
            self._session.add(user)
            self._session.commit()
        self._controllers = {
            "activity": ActivityController(self._session, self._owner),
            "author": AuthorController(self._session, self._owner),
            "bibliography": BibliographyController(self._session, self._owner),
            "chapter": ChapterController(self._session, self._owner),
            "character": CharacterController(self._session, self._owner),
            "event": EventController(self._session, self._owner),
            "image": ImageController(self._session, self._owner),
            "link": LinkController(self._session, self._owner),
            "location": LocationController(self._session, self._owner),
            "note": NoteController(self._session, self._owner),
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