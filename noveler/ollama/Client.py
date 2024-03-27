from configparser import ConfigParser
from typing import Optional, List, Union
import requests

from noveler.models import OllamaMessage


class Client:
    """Client is a wrapper for the Ollama REST API.

    Methods
    -------
    generate (
        model: str, prompt: str, images: Optional[List[str]],
        options: Optional[dict], system: Optional[str], template: Optional[str],
        context: Optional[str], raw: Optional[bool],
        keep_alive: Optional[Union[float, str]]
    )
        Generate a completion
    chat (
        model: str, messages: List[dict], options: Optional[dict],
        template: Optional[str], keep_alive: Optional[Union[float, str]]
    )
        Generate a chat completion
    create (
        name: str, modelfile: Optional[str], path: Optional[str]
    )
        Create a model
    list ()
        List local models
    show ( name: str )
        Show a model's information
    copy ( source: str, destination: str )
        Copy a model
    delete ( name: str )
        Delete a model
    pull ( name: str, insecure: Optional[bool] )
        Pull a model
    push ( name: str )
        Push a model
    embeddings (
        model: str, prompt: str, options: dict,
        keep_alive: Optional[Union[float, str]]
    )
        Generate embeddings
    """

    _host: str
    _port: int

    def __init__(self):
        """Initialize the Client with the provided URL."""

        config = ConfigParser()
        config.read("config.cfg")

        host = config.get("ollama", "host")
        port = config.getint("ollama", "port")

        self._host = host
        self._port = port

    def generate(
        self, model: str, prompt: str,
        images: Optional[List[str]] = None,
        options: Optional[dict] = None, system: Optional[str] = None,
        template: Optional[str] = None, context: Optional[str] = None,
        raw: Optional[bool] = False,
        keep_alive: Optional[Union[float, str]] = "5m"
    ) -> dict:
        """Generate a completion.

        Parameters
        ----------
        model : str
            The name of the model to use.
        prompt : str
            The prompt to generate a completion for.
        images : Optional[List[str]] (default=None)
            An optional list of base64-encoded images (for multimodal models such as llava)
        options : Optional[dict] (default=None)
            additional model parameters listed in the documentation for the Modelfile such as temperature
        system : Optional[str] (default=None)
            Also referred to as "priming" in Noveler's internal code, also known as "instructions". If present, this
            will override what is defined in the Modelfile
        template : Optional[str] (default=None)
            The interaction template to use. Overrides the default template defined in the Modelfile.
        context : Optional[str] (default=None)
            The context parameter returned from a previous request to /generate. This can be used to keep a short
            conversational memory
        raw : Optional[bool] (default=False)
            If true no formatting will be applied to the prompt. You may choose to use the raw parameter if you are
            specifying a full templated prompt in your request to the API
        keep_alive : Optional[Union[float, str]] (default="5m")
            Controls how long the model will stay loaded into memory following the request (default: 5m)

        Returns
        -------
        dict
            A dictionary containing the completion.
        """

        try:

            data = {
                "model": model,
                "prompt": prompt,
                "images": images,
                "format": "json",
                "options": options,
                "system": system,
                "template": template,
                "context": context,
                "stream": False,
                "raw": raw,
                "keep_alive": keep_alive
            }
            api_url = f"http://{self._host}:{self._port}/api/generate"
            response = requests.post(api_url, data=data)

            return response.json()

        except requests.exceptions.HTTPError as e:
            return e.response.json()

    def chat(
        self, model: str, messages: List[OllamaMessage],
        options: Optional[dict] = None, template: str = None,
        keep_alive: Optional[Union[float, str]] = "5m"
    ) -> dict:
        """Generate a chat completion.

        Parameters
        ----------
        model : str
            The name of the model to use.
        messages : List[dict]
            A list of messages to use for the chat.
        options : Optional[dict] (default=None)
            additional model parameters listed in the documentation for the Modelfile such as temperature
        template : Optional[str] (default=None)
            The interaction template to use. Overrides the default template defined in the Modelfile.
        keep_alive : Optional[Union[float, str]] (default="5m")
            Controls how long the model will stay loaded into memory following the request (default: 5m)

        Returns
        -------
        dict
            A dictionary containing the chat completion.
        """

        try:

            data = {
                "model": model,
                "messages": messages,
                "format": "json",
                "options": options if options is not None else {},
                "template": template,
                "stream": False,
                "keep_alive": keep_alive
            }
            api_url = f"http://{self._host}:{self._port}/api/chat"
            response = requests.post(api_url, data=data)

            return response.json()

        except requests.exceptions.HTTPError as e:
            return e.response.json()

    def create(
        self, name: str, modelfile: Optional[str] = None,
        path: Optional[str] = None
    ) -> dict:
        """Create a model.

        Parameters
        ----------
        name : str
            The name of the model to create.
        modelfile : Optional[str] (default=None)
            The path to the modelfile to use.
        path : Optional[str] (default=None)
            The path to the directory to save the model in.

        Returns
        -------
        dict
            A dictionary containing the model's information.
        """

        try:

            data = {
                "name": name,
                "modelfile": modelfile,
                "stream": False,
                "path": path
            }
            api_url = f"http://{self._host}:{self._port}/api/create"
            response = requests.post(api_url, data=data)

            return response.json()

        except requests.exceptions.HTTPError as e:
            return e.response.json()

    def list(self) -> dict:
        """List local models.

        Returns
        -------
        dict
            A dictionary containing the local models.
        """

        try:

            api_url = f"http://{self._host}:{self._port}/api/tags"
            response = requests.get(api_url)

            return response.json()

        except requests.exceptions.HTTPError as e:
            return e.response.json()

    def show(self, name: str) -> dict:
        """Show a model's information.

        Parameters
        ----------
        name : str
            The name of the model to show.

        Returns
        -------
        dict
            A dictionary containing the model's information.
        """

        try:
            api_url = f"http://{self._host}:{self._port}/api/show"
            response = requests.post(api_url, data={"name": name})

            return response.json()

        except requests.exceptions.HTTPError as e:
            return e.response.json()

    def copy(self, source: str, destination: str) -> dict:
        """Copy a model.

        Parameters
        ----------
        source : str
            The name of the model to copy.
        destination : str
            The name of the new model.

        Returns
        -------
        dict
            A dictionary containing the new model's information.
        """

        try:
            data = {
                "source": source,
                "destination": destination
            }
            api_url = f"http://{self._host}:{self._port}/api/copy"
            response = requests.post(api_url, data=data)

            return response.json()

        except requests.exceptions.HTTPError as e:
            return e.response.json()

    def delete(self, name: str) -> dict:
        """Delete a model.

        Parameters
        ----------
        name : str
            The name of the model to delete.

        Returns
        -------
        dict
            A dictionary containing the model's information.
        """

        try:
            params = {
                "name": name
            }
            api_url = f"http://{self._host}:{self._port}/api/delete"
            response = requests.delete(api_url, params=params)

            return response.json()

        except requests.exceptions.HTTPError as e:
            return e.response.json()

    def pull(self, name: str, insecure: Optional[bool] = False) -> dict:
        """Pull a model.

        Parameters
        ----------
        name : str
            The name of the model to pull.
        insecure : Optional[bool] (default=False)
            Whether to use insecure connections.

        Returns
        -------
        dict
            A dictionary containing the model's information.
        """

        try:
            data = {
                "name": name,
                "insecure": insecure,
                "stream": False
            }
            api_url = f"http://{self._host}:{self._port}/api/pull"
            response = requests.post(api_url, data=data)

            return response.json()

        except requests.exceptions.HTTPError as e:
            return e.response.json()

    def push(self, name: str, insecure: Optional[str] = False) -> dict:
        """Push a model

        Parameters
        ----------
        name : str
            The name of the model to push.
        insecure : Optional[str] (default=False)
            Whether to use insecure connections.

        Returns
        -------
        dict
            A dictionary containing the model's information.
        """

        try:
            data = {
                "name": name,
                "insecure": insecure,
                "stream": False
            }
            api_url = f"http://{self._host}:{self._port}/api/push"
            response = requests.post(api_url, data=data)

            return response.json()

        except requests.exceptions.HTTPError as e:
            return e.response.json()

    def embeddings(
        self, model: str, prompt: str, options: dict,
        keep_alive: Optional[Union[float, str]]
    ) -> dict:
        """Generate embeddings.

        Parameters
        ----------
        model : str
            The name of the model to use.
        prompt : str
            The prompt to generate embeddings for.
        options : dict
            additional model parameters listed in the documentation for the Modelfile such as temperature
        keep_alive : Optional[Union[float, str]]
            Controls how long the model will stay loaded into memory following the request

        Returns
        -------
        dict
            A dictionary containing the embeddings.
        """

        try:
            if options is None:
                options = {}

            data = {
                "model": model,
                "prompt": prompt,
                "options": options if options is not None else {},
                "keep_alive": keep_alive
            }
            api_url = f"http://{self._host}:{self._port}/api/embeddings"
            response = requests.post(api_url, data=data)

            return response.json()

        except requests.exceptions.HTTPError as e:
            return e.response.json()
