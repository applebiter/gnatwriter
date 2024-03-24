import uuid
from typing import Type
from sqlalchemy.orm import Session
from noveler.models import User, Assistance
from noveler.ollamasubsystem import OllamaClient

noveler_chat_model = "gemma:2b"
noveler_image_model = "llava:7b"
noveler_generate_model = "llama2:7b"
ollama_model_memory_duration = "1h"  # How long to keep the model in memory
ollama_context_window = 4096  # The number of tokens to use as context for the model


class BaseAssistant:
    """BaseAssistant"""

    _self = None
    _owner = None
    _session = None
    _templates = {}

    def __new__(cls, session: Session, owner: Type[User]):
        """Enforce Singleton pattern"""

        if cls._self is None:
            cls._self = super().__new__(cls)

        return cls._self

    def __init__(self, session: Session, owner: Type[User]):

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
        self._keep_alive = ollama_model_memory_duration
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
