from typing import Type
from sqlalchemy.orm import Session
from noveler.assistants import ChatAssistant, ImageAssistant, GenerativeAssistant
from noveler.controllers import BaseController
from noveler.models import User


class AssistantRegistry(BaseController):
    """Assistant Registry

    The Assistant Registry is a class that manages the various assistants
    available to the user. It is a singleton class that is responsible for
    creating and managing the various assistants available to the user.
    """

    _assistants = {}

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

        self._assistants = {
            "chat": '',  # ChatAssistant(session, owner),
            "image": '',  # ImageAssistant(session, owner),
            "generative": ''  # GenerativeAssistant(session, owner)
        }

    def __call__(self, *args, **kwargs):
        return self._assistants[args[0]]

    def __str__(self):
        return "Noveler Application [alpha] Assistant Registry"

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @property
    def assistants(self):
        return self._assistants
