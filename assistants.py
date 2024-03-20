from typing import List, Literal, Optional

from ollama import Message

from ollamasubsystem import OllamaClient


class AssistantRegistry:

    _self = None
    _assistants = {}

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self):
        self._assistants = {
            "image": ImageAssistant()
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


class Assistant:
    def __init__(self, name: str, model: str):
        self._name = name
        self._model = model
        self._client = OllamaClient()

    def __str__(self):
        return f"Noveler Application [alpha] Assistant: {self._name}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self._name}, {self._model})"


class ImageAssistant(Assistant):
    def __init__(self):
        super().__init__("Image Assistant", "llava")

    def describe(
            self,
            images: List[str],
            prompt: Optional[str] = "Describe the contents of the image:",
            options: Optional[dict] = None
    ):
        encoded = []

        for image in images:
            with open(image, "rb") as file:
                encoded.append(file.read())

        priming = """Image Assistant is ready to describe the contents of the \
                    image ."""
        message0 = Message(role="system", content=priming)
        message1 = Message(role="user", content=prompt, images=encoded)

        if not options:
            options = {
                "max_tokens": 100,
                "temperature": 0.5,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stop": ["\n"]
            }

        return self._client.chat(
            model=self._model,
            messages=[message0, message1],
            options=options,
            return_format="json"
        )

    def __str__(self):
        return f"Noveler Application [alpha] Image Assistant"

    def __repr__(self):
        return f"{self.__class__.__name__}()"
