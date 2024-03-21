from typing import List, Optional, Type
import uuid
from ollama import Message
from sqlalchemy.orm import Session
from controllers import BaseController
from models import *
from ollamasubsystem import OllamaClient

noveler_chat_model = "llama2-uncensored"
noveler_image_model = "llava"


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
            "chat": ChatAssistant(session, owner),
            "image": ImageAssistant(session, owner)
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


class Assistant(BaseController):
    """Assistant"""

    def __init__(self, session: Session, owner: Type[User]):
        super().__init__(session, owner)

        uuid4 = str(uuid.uuid4())
        uuid_exists = session.query(Assistance).filter(
            Assistance.session_uuid == uuid4
        ).first()

        while uuid_exists:
            uuid4 = str(uuid.uuid4())
            uuid_exists = session.query(Assistance).filter(
                Assistance.session_uuid == uuid4
            ).first()

        self._session_uuid = uuid4
        self._client = OllamaClient()
        self._chat_model = noveler_chat_model
        self._image_model = noveler_image_model

    @property
    def session_uuid(self):
        return self._session_uuid


class ChatAssistant(Assistant):
    """Chat Assistant

    The Chat Assistant is a specialized assistant that uses the Ollama API to
    chat with the user.
    """

    def __init__(self, session: Session, owner: Type[User]):
        super().__init__(session, owner)

        self._name = "Chat Assistant"

    def chat(
            self,
            prompt: str,
            temperature: Optional[float] = 0.5,
            seed: Optional[int] = None,
            priming: str = None,
            options: Optional[dict] = None,
            session_uuid: str = None,
    ):
        """Chat with the Chat Assistant.

        The temperature parameter is a float value between 0 and 1. Anything
        greater than 0 will make the assistant more creative, but also more
        unpredictable. The seed parameter is an integer value that can be used
        to make the assistant's responses more predictable. If the temperature
        is set to 0, then the assistant's response will be reproducible, given
        the same seed value.

        Parameters
        ----------
        prompt : str
            The prompt to be used when chatting with the assistant.
        temperature : Optional[float]
            The temperature to be used when making the request. Defaults to
            0.5.
        seed : Optional[int]
            The seed to be used when making the request. Defaults to None.
        priming : Optional[str]
            The priming to be used when chatting with the assistant. Defaults to
            None.
        options : Optional[dict]
            The options to be used when making the request.
        session_uuid : str
            The UUID of the session to be used when making the request.
        """

        if not priming:
            priming = """Chat Assistant is an expert in creative writing, style, 
                and literary theory who can explain the fine points of plot and 
                the sophisticated nuance of tone, and who also knows the human 
                subject very well."""

        messages = [Message(role="system", content=priming)]

        session_uuid = self._session_uuid if not session_uuid else session_uuid

        for message in self.get_by_session_uuid(session_uuid):
            messages.append(Message(
                role="user", content=message.prompt
            ))
            messages.append(Message(
                role="assistant", content=message.content
            ))

        messages.append(Message(
            role="user", content=prompt
        ))

        if not options:
            options = {
                "temperature": temperature,
            }

        if not options.get("temperature"):
            options["temperature"] = temperature

        with self._session as session:

            try:

                response = self._client.chat(
                    model=self._chat_model,
                    messages=messages,
                    options=options,
                    keep_alive=0
                )

                assistance = Assistance(
                    user_id=self._owner.id,
                    session_uuid=session_uuid,
                    assistant=self._name,
                    model=self._chat_model,
                    priming=priming,
                    prompt=prompt,
                    temperature=temperature,
                    seed=seed,
                    content=response["message"]["content"] if response.get("message") else None,
                    done=response["done"],
                    total_duration=response["total_duration"] if response.get("total_duration") else None,
                    load_duration=response["load_duration"] if response.get("load_duration") else None,
                    prompt_eval_count=response["prompt_eval_count"] if response.get("prompt_eval_count") else None,
                    prompt_eval_duration=response["prompt_eval_duration"] if response.get("prompt_eval_duration") else None,
                    eval_count=response["eval_count"] if response.get("eval_count") else None,
                    eval_duration=response["eval_duration"] if response.get("eval_duration") else None,
                    created=datetime.now()
                )

                summary = f"{self._owner.username} used the Chat Assistant"
                activity = Activity(
                    user_id=self._owner.id, summary=summary,
                    created=datetime.now()
                )

                session.add(assistance)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return response

    def __str__(self):
        """Return the class string representation."""
        return f"Noveler Application [alpha] {self._name}"

    def __repr__(self):
        """Return the class representation."""
        return f"{self.__class__.__name__}()"

    def get_by_session_uuid(self, session_uuid: str):
        """Get all messages by session UUID."""

        with self._session as session:

            messages = session.query(Assistance).filter_by(
                session_uuid=session_uuid
            ).order_by(Assistance.created).all()

            return messages


class ImageAssistant(Assistant):
    """Image Assistant

    The Image Assistant is a specialized assistant that uses the Ollama API to
    describe the contents of an image.
    """

    def __init__(self, session: Session, owner: Type[User]):
        super().__init__(session, owner)

        self._name = "Image Assistant"

    def describe(
            self,
            images: List[str],
            prompt: Optional[str] = "Describe the image",
            temperature: Optional[float] = 0.5,
            seed: Optional[int] = None,
            priming: Optional[str] = None,
            options: Optional[dict] = None,
            session_uuid: str = None,
    ):
        """Describe the contents of an image using the Ollama API.

        Parameters
        ----------
        images : List[str]
            A list of image file paths to be described.
        temperature : Optional[float]
            The temperature to be used when making the request. Defaults to
            0.5.
        seed : Optional[int]
            The seed to be used when making the request. Defaults to None.
        prompt : Optional[str]
            The prompt to be used when requesting the description. Defaults to
            "Describe the contents of the image:".
        priming : Optional[str]
            The priming to be used when describing the image.
        options : Optional[dict]
            The options to be used when making the request.
        session_uuid : str
            The UUID of the session to be used when making the request.
        """
        encoded = []

        for image in images:
            with open(image, "rb") as file:
                encoded.append(file.read())

        if not priming:
            priming = """Image Assistant is ready to describe the image."""

        messages = [Message(role="system", content=priming)]

        session_uuid = self._session_uuid if not session_uuid else session_uuid

        for message in self.get_by_session_uuid(session_uuid):
            messages.append(Message(
                role="user", content=message.prompt
            ))
            messages.append(Message(
                role="assistant", content=message.content
            ))

        messages.append(Message(
            role="user", content=prompt
        ))

        if not options:
            options = {
                "temperature": temperature,
            }

        if not options.get("temperature"):
            options["temperature"] = temperature

        with self._session as session:

            try:

                response = self._client.chat(
                    model=self._image_model,
                    messages=messages,
                    options=options,
                    keep_alive=0
                )

                assistance = Assistance(
                    user_id=self._owner.id,
                    session_uuid=session_uuid,
                    assistant=self._name,
                    model=self._image_model,
                    priming=priming,
                    prompt=prompt,
                    temperature=temperature,
                    seed=seed,
                    content=response["message"]["content"] if response.get("message") else None,
                    done=response["done"],
                    total_duration=response["total_duration"] if response.get("total_duration") else None,
                    load_duration=response["load_duration"] if response.get("load_duration") else None,
                    prompt_eval_count=response["prompt_eval_count"] if response.get("prompt_eval_count") else None,
                    prompt_eval_duration=response["prompt_eval_duration"] if response.get("prompt_eval_duration") else None,
                    eval_count=response["eval_count"] if response.get("eval_count") else None,
                    eval_duration=response["eval_duration"] if response.get("eval_duration") else None,
                    created=datetime.now()
                )

                summary = f"{self._owner.username} used the Image Assistant"
                activity = Activity(
                    user_id=self._owner.id, summary=summary,
                    created=datetime.now()
                )

                session.add(assistance)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return response

    def __str__(self):
        return f"Noveler Application [alpha] {self._name}"

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def get_by_session_uuid(self, session_uuid: str):
        """Get all messages by session UUID."""

        with self._session as session:

            messages = session.query(Assistance).filter_by(
                session_uuid=session_uuid
            ).order_by(Assistance.created).all()

            return messages
