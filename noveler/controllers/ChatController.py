import uuid
from configparser import ConfigParser
from datetime import datetime
from typing import Type, Optional, Union
from sqlalchemy.orm import Session
from noveler.controllers.BaseController import BaseController
from noveler.models import User, Assistance, Activity, OllamaTemplate
from noveler.ollama import Client, OllamaMessage


class ChatController(BaseController):

    _templates = []

    """Chat Controller

    The Chat Controller is a specialized controller that uses the Ollama API to
    chat with the user.

    Attributes
    ----------
    _name : str
        The name of the Chat Assistant.
    _session_uuid : str
        The UUID of the session to be used when making the request.
    _client : OllamaClient
        The Ollama client to be used when making the request.
    _chat_model : str
        The model to be used when making the request.
    _multimodal_model : str
        The image model to be used when making the request.
    _generative_model : str
        The generative model to be used when making the request.
    _num_ctx : int
        The number of tokens to use as context for the model.
    _keep_alive : str
        How long to keep the model in memory.
    _templates : dict
        The templates to be used when making the request.

    Methods
    -------
    chat(prompt: str, temperature: Optional[float] = 0.5, seed: Optional[int] = None, priming: str = None, options: Optional[dict] = None, session_uuid: str = None, keep_alive: Optional[Union[float, str]] = None)
        Chat with the Chat Assistant.
    get_by_session_uuid(session_uuid: str)
        Get all Assistance messages by session UUID.
    """
    def __init__(self, session: Session, owner: Type[User]):

        super().__init__(session, owner)

        self._name = "Chat Assistant"

        uuid4 = str(uuid.uuid4())
        uuid_exists = session.query(Assistance).filter(
            Assistance.session_uuid == uuid4
        ).first()

        while uuid_exists:
            uuid4 = str(uuid.uuid4())
            uuid_exists = session.query(Assistance).filter(
                Assistance.session_uuid == uuid4
            ).first()

        config = ConfigParser()
        config.read("config.cfg")

        self._session_uuid = uuid4
        self._client = Client()
        self._chat_model = config.get("ollama", "chat_model")
        self._multimodal_model = config.get("ollama", "multimodal_model")
        self._generative_model = config.get("ollama", "generative_model")
        self._num_ctx = config.getint("ollama", "context_window")
        self._keep_alive = config.get("ollama", "model_memory_duration")

        with self._session as session:
            self._templates = session.query(OllamaTemplate).all()

    def chat(
            self,
            prompt: str,
            temperature: Optional[float] = 0.5,
            seed: Optional[int] = None,
            priming: str = None,
            options: Optional[dict] = None,
            session_uuid: str = None,
            keep_alive: Optional[Union[float, str]] = None
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
            The UUID of the LM session to be used when making the request.
        keep_alive : Optional[Union[float, str]]
            The keep alive value to be used when making the request.
        """

        if not priming:
            priming = [template for template in self._templates if template.model == self._chat_model][0].priming

        session_uuid = self._session_uuid if not session_uuid else session_uuid
        messages = [OllamaMessage(role="system", content=priming)]

        with self._session as session:

            assistances = session.query(Assistance).filter_by(
                session_uuid=session_uuid
            ).order_by(Assistance.created).all()

            if assistances:
                for assistance in assistances:
                    messages.append(OllamaMessage(role="user", content=assistance.prompt))
                    messages.append(OllamaMessage(role="assistant", content=assistance.content))

        messages.append(OllamaMessage(role="user", content=prompt))

        if not options:
            options = {
                "temperature": temperature,
                "num_ctx": self._num_ctx
            }

        if not options.get("temperature"):
            options["temperature"] = temperature

        if not options.get("num_ctx"):
            options["num_ctx"] = self._num_ctx

        template = [template for template in self._templates if template.model == self._chat_model][0].template
        keep_alive = self._keep_alive if not keep_alive else keep_alive

        with self._session as session:

            try:

                response = self._client.chat(
                    model=self._chat_model,
                    messages=messages,
                    options=options,
                    template=template,
                    keep_alive=keep_alive
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
