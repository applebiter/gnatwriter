from typing import List
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
            prompt: str = "Describe the contents of the image:"
    ):
        encoded = []

        for image in images:
            with open(image, "rb") as file:
                encoded.append(file.read())

        return self._client.chat(
            model=self._model,
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                    'images': encoded
                },
            ],
            return_format='json'
        )

    def __str__(self):
        return f"Noveler Application [alpha] Image Assistant"

    def __repr__(self):
        return f"{self.__class__.__name__}()"
