from typing import List, Optional
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
        """Describe the contents of an image using the Ollama API.

        This is an example of the JSON response from the Ollama API:
            {
                'model': 'llava',
                'created_at': '2024-03-20T02:52:27.742885501Z',
                'message': {
                    'role': 'assistant',
                    'content': {
                        "text":"In the image, there is a bearded man with gray
                            hair, wearing a brown apron over a white shirt. He
                            appears to be working in a workshop setting. The man is
                            standing next to an open metal safe or box, which has a
                            key inserted into it. Inside the safe, we can see
                            various tools and equipment. The background suggests a
                            well-equipped workshop with wooden shelves and what
                            looks like machinery or machinery parts. Natural light
                            seems to be coming from a window on the left side of the
                            image. The man is focused on his task, possibly related
                            to crafting or repair work.",
                    },
                },
                'done': True,
                'total_duration': 78227562692,
                'load_duration': 3307143035,
                'prompt_eval_count': 1,
                'prompt_eval_duration': 15251524000,
                'eval_count': 128,
                'eval_duration': 59658313000
            }
        """
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
                "temperature": 0.5,
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
