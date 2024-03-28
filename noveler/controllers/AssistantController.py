import base64
import os
import uuid
from configparser import ConfigParser
from datetime import datetime
from typing import Type, Optional, Union, List, Literal

from ollama import Client, Message
from sqlalchemy.orm import Session
from noveler.controllers.BaseController import BaseController
from noveler.models import User, Assistance, Activity, OllamaModel


class AssistantController(BaseController):
    """Assistant Controller

    Attributes
    ----------
    _name : str
        The name of the assistant.
    _session_uuid : str
        The UUID of the session.
    _client : OllamaClient
        The Ollama client to be used when making requests.
    _chat_model : str
        The model to be used when chatting.
    _multimodal_model : str
        The model to be used when describing images.
    _generative_model : str
        The model to be used when generating text.
    _num_ctx : int
        The number of tokens to use as context for the model.
    _keep_alive : Union[float, str]
        The duration to keep the model in memory.
    _templates : dict
        The templates to be used when generating text.

    Methods
    -------
    chat(
        prompt: str,
        temperature: Optional[float] = 0.5,
        seed: Optional[int] = None,
        priming: str = None,
        options: Optional[dict] = None,
        session_uuid: str = None,
        keep_alive: Optional[Union[float, str]] = None
    )
    generate(
        prompt: str = None,
        temperature: Optional[float] = 0.5,
        seed: Optional[int] = None,
        priming: Optional[str] = None,
        options: Optional[dict] = None,
        session_uuid: str = None,
        keep_alive: Optional[Union[float, str]] = None
    )
        Generate text based on a prompt.
    describe_image(
        images: List[str],
        prompt: Optional[str] = "Describe the image",
        temperature: Optional[float] = 0.5,
        seed: Optional[int] = None,
        priming: Optional[str] = None,
        options: Optional[dict] = None,
        session_uuid: str = None,
        keep_alive: Optional[Union[float, str]] = None
    )
        Describe the contents of an image using the Ollama API.
    get_by_session_uuid(session_uuid: str)
        Get all Assistance messages by session UUID.
    """

    _templates = {}

    def __init__(self, session: Session, owner: Type[User]):

        super().__init__(session, owner)

        self._name = "Generative Assistant"

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
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        print(f"{project_root}/config.cfg")
        config.read(f"{project_root}/config.cfg")
        ollama_host = config.read("ollama", "host")
        ollama_port = str(config.read("ollama", "port"))

        self._client = Client(host="http://violet:11434")
        self._session_uuid = uuid4
        self._chat_model = config.get("ollama", "chat_model")
        self._generative_model = config.get("ollama", "generative_model")
        self._multimodal_model = config.get("ollama", "multimodal_model")
        self._num_ctx = config.getint("ollama", "context_window")
        self._keep_alive = config.get("ollama", "model_memory_duration")

        with self._session as session:
            self._templates = session.query(OllamaModel).all()

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

        messages = [Message(role="system", content=priming)]
        session_uuid = self._session_uuid if not session_uuid else session_uuid

        with self._session as session:

            assistances = session.query(Assistance).filter_by(
                session_uuid=session_uuid
            ).order_by(Assistance.created).all()

            if assistances:
                for assistance in assistances:
                    messages.append(Message(role="user", content=assistance.prompt))
                    messages.append(Message(role="assistant", content=assistance.content))

        messages.append(Message(role="user", content=prompt))

        if not options:
            options = {
                "temperature": temperature,
                "num_ctx": self._num_ctx
            }

        if not options.get("temperature"):
            options["temperature"] = temperature

        if not options.get("num_ctx"):
            options["num_ctx"] = self._num_ctx

        keep_alive = self._keep_alive if not keep_alive else keep_alive

        with self._session as session:

            try:

                response = self._client.chat(
                    model=self._chat_model,
                    messages=messages,
                    stream=False,
                    format="",
                    options=options,
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

    def describe_image(
            self,
            images: List[str],
            prompt: Optional[str] = "Describe the image",
            temperature: Optional[float] = 0.5,
            seed: Optional[int] = None,
            priming: Optional[str] = None,
            return_format: Literal['', 'json'] = '',
            options: Optional[dict] = None,
            session_uuid: str = None,
            keep_alive: Optional[Union[float, str]] = None
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
        return_format : str
            The format to be used to return the request.
        options : Optional[dict]
            The options to be used when making the request.
        session_uuid : str
            The UUID of the session to be used when making the request.
        keep_alive : Optional[Union[float, str]]
            The keep alive value to be used when making the request.
        """
        encoded_images = []

        for image in images:
            with open(image, "rb") as file:
                encoded_images.append(base64.b64encode(file.read()).decode())

        template = [template for template in self._templates if template.model == self._multimodal_model][0]

        if not priming:
            priming = template.priming

        session_uuid = self._session_uuid if not session_uuid else session_uuid

        if not options:
            options = {
                "temperature": temperature,
                "num_ctx": self._num_ctx
            }

        if not options.get("temperature"):
            options["temperature"] = temperature

        if not options.get("num_ctx"):
            options["num_ctx"] = self._num_ctx

        keep_alive = self._keep_alive if not keep_alive else keep_alive

        with self._session as session:

            try:

                response = self._client.generate(
                    model=self._multimodal_model, prompt=prompt, system=priming,
                    template=template.template, context=None, stream=False,
                    raw=False, format=return_format, images=encoded_images,
                    options=options, keep_alive=keep_alive
                )

                content = response["response"] if response.get("response") else None

                assistance = Assistance(
                    user_id=self._owner.id,
                    session_uuid=session_uuid,
                    assistant=self._name,
                    model=self._multimodal_model,
                    priming=priming,
                    prompt=prompt,
                    temperature=temperature,
                    seed=seed,
                    content=content,
                    done=response["done"],
                    total_duration=response["total_duration"] if response.get("total_duration") else None,
                    load_duration=response["load_duration"] if response.get("load_duration") else None,
                    prompt_eval_count=response["prompt_eval_count"] if response.get("prompt_eval_count") else None,
                    prompt_eval_duration=response["prompt_eval_duration"] if response.get("prompt_eval_duration") else None,
                    eval_count=response["eval_count"] if response.get("eval_count") else None,
                    eval_duration=response["eval_duration"] if response.get("eval_duration") else None,
                    created=datetime.now()
                )

                summary = f"{self._owner.username} used the Multimodal Assistant"
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

    def generate(
            self,
            prompt: str = None,
            temperature: Optional[float] = 0.5,
            seed: Optional[int] = None,
            priming: Optional[str] = None,
            return_format: Literal['', 'json'] = '',
            options: Optional[dict] = None,
            session_uuid: str = None,
            keep_alive: Optional[Union[float, str]] = None
    ):
        """Describe the contents of an image using the Ollama API.

        Parameters
        ----------
        prompt : str
            The prompt to be used when requesting the description.
        temperature : Optional[float]
            The temperature to be used when making the request. Defaults to
            0.5.
        seed : Optional[int]
            The seed to be used when making the request. Defaults to None.
        priming : Optional[str]
            The priming to be used prior to the prompt.
        return_format : str
            The format to be used to return the request.
        options : Optional[dict]
            The options to be used when making the request.
        session_uuid : str
            The UUID of the session to be used when making the request.
        keep_alive : Optional[Union[float, str]]
            The keep alive value to be used when making the request.
        """
        template = [template for template in self._templates if template.model == self._generative_model][0]

        if not priming:
            priming = """Generative Assistant is ready to perform a task."""

        session_uuid = self._session_uuid if not session_uuid else session_uuid

        if not options:
            options = {
                "temperature": temperature,
                "num_ctx": self._num_ctx
            }

        if not options.get("temperature"):
            options["temperature"] = temperature

        if not options.get("num_ctx"):
            options["num_ctx"] = self._num_ctx

        keep_alive = self._keep_alive if not keep_alive else keep_alive

        with self._session as session:

            try:

                response = self._client.generate(
                    model=self._generative_model, prompt=prompt, system=priming,
                    template=template.template, context=None, stream=False,
                    raw=False, format=return_format, images=None,
                    options=options, keep_alive=keep_alive
                )

                assistance = Assistance(
                    user_id=self._owner.id,
                    session_uuid=session_uuid,
                    assistant=self._name,
                    model=self._generative_model,
                    priming=priming,
                    prompt=prompt,
                    temperature=temperature,
                    seed=seed,
                    content=response["response"] if response.get("response") else None,
                    done=response["done"],
                    total_duration=response["total_duration"] if response.get("total_duration") else None,
                    load_duration=response["load_duration"] if response.get("load_duration") else None,
                    prompt_eval_count=response["prompt_eval_count"] if response.get("prompt_eval_count") else None,
                    prompt_eval_duration=response["prompt_eval_duration"] if response.get("prompt_eval_duration") else None,
                    eval_count=response["eval_count"] if response.get("eval_count") else None,
                    eval_duration=response["eval_duration"] if response.get("eval_duration") else None,
                    created=datetime.now()
                )

                summary = f"{self._owner.username} used the Generative Assistant"
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
