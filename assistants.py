from typing import List, Optional, Type, Union
import uuid
from ollama import Message
from sqlalchemy.orm import Session
from controllers import BaseController
from models import *
from ollamasubsystem import OllamaClient

noveler_chat_model = "gemma:2b"
noveler_image_model = "llava:7b"
noveler_generate_model = "llama2:7b"
ollama_model_memory = "1h"  # How long to keep the model in memory
ollama_context_window = 4096  # The number of tokens to use as context for the model


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
            "image": ImageAssistant(session, owner),
            "generative": GenerativeAssistant(session, owner)
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

    _templates = {}

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
        self._generative_model = noveler_generate_model
        self._num_ctx = ollama_context_window
        self._keep_alive = ollama_model_memory
        self._templates = {
            "codellama:13b": """[INST] <<SYS>>{{ .System }}<</SYS>>

{{ .Prompt }} [/INST]
            """,
            "codellama:7b": """[INST] <<SYS>>{{ .System }}<</SYS>>

{{ .Prompt }} [/INST]
            """,
            "dolphin-phi:2.7b": """<|im_start|>system
{{ .System }}<|im_end|>
<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
            """,
            "gemma:2b": """<start_of_turn>user
{{ if .System }}{{ .System }} {{ end }}{{ .Prompt }}<end_of_turn>
<start_of_turn>model
{{ .Response }}<end_of_turn>
            """,
            "llama2:13b": """[INST] <<SYS>>{{ .System }}<</SYS>>

{{ .Prompt }} [/INST]
            """,
            "llama2:7b": """[INST] <<SYS>>{{ .System }}<</SYS>>

{{ .Prompt }} [/INST]
            """,
            "llama2-uncensored:7b": """[INST] <<SYS>>{{ .System }}<</SYS>>

{{ .Prompt }} [/INST]
            """,
            "llava:13b": """[INST] {{ if .System }}{{ .System }} {{ end }}{{ .Prompt }} [/INST]
            """,
            "llava:7b": """[INST] {{ if .System }}{{ .System }} {{ end }}{{ .Prompt }} [/INST]
            """,
            "mistral:7b": """[INST] {{ .System }} {{ .Prompt }} [/INST]
            """,
            "orca2:13b": """<|im_start|>system
{{ .System }}<|im_end|>
<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
            """,
            "orca2:7b": """<|im_start|>system
{{ .System }}<|im_end|>
<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
            """,
            "phi:2.7b": """{{ if .System }}System: {{ .System }}{{ end }}
User: {{ .Prompt }}
Assistant:
            """,
            "wizard-vicuna-uncensored:13b": """{{ .System }}
USER: {{ .Prompt }}
ASSISTANT:
            """,
            "wizardcoder:13b-python": """{{ .System }}

### Instruction:
{{ .Prompt }}

### Response:
            """,
            "wizardcoder:7b-python": """{{ .System }}

### Instruction:
{{ .Prompt }}

### Response:
            """,
            "writer:7b": """<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant
            """
        }

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
            priming = """Chat Assistant is an expert in creative writing, style, 
                and literary theory who can explain the fine points of plot and 
                the sophisticated nuance of tone, and who also knows the human 
                subject very well."""

        session_uuid = self._session_uuid if not session_uuid else session_uuid
        messages = [
            Message(role="system", content=priming),
            Message(role="user", content=prompt)
        ]

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
        options : Optional[dict]
            The options to be used when making the request.
        session_uuid : str
            The UUID of the session to be used when making the request.
        keep_alive : Optional[Union[float, str]]
            The keep alive value to be used when making the request.
        """
        encoded = []

        for image in images:
            with open(image, "rb") as file:
                encoded.append(file.read())

        if not priming:
            priming = """Image Assistant is ready to describe the image."""

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
                    model=self._image_model,
                    prompt=prompt,
                    system=priming,
                    template=self._templates[self._image_model],
                    images=encoded,
                    options=options,
                    keep_alive=keep_alive
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


class GenerativeAssistant(Assistant):
    def __init__(self, session: Session, owner: Type[User]):
        super().__init__(session, owner)

        self._name = "Generative Assistant"

    def generate(
            self,
            prompt: str = None,
            temperature: Optional[float] = 0.5,
            seed: Optional[int] = None,
            priming: Optional[str] = None,
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
        options : Optional[dict]
            The options to be used when making the request.
        session_uuid : str
            The UUID of the session to be used when making the request.
        keep_alive : Optional[Union[float, str]]
            The keep alive value to be used when making the request.
        """
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
                    model=self._generative_model,
                    prompt=prompt,
                    system=priming,
                    template=self._templates[self._image_model],
                    options=options,
                    keep_alive=keep_alive
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
