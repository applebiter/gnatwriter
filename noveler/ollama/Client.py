from typing import Optional, List, Union
# import requests


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
        model: str, messages: Optional[List[dict]], options: dict,
        template: str, keep_alive: Optional[Union[float, str]]
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

    _url: str

    def __init__(self, url: str):
        """Initialize the Client with the provided URL."""
        self._url = url

    def generate(
        self, model: str, prompt: str, images: Optional[List[str]],
        options: Optional[dict], system: Optional[str], template: Optional[str],
        context: Optional[str], raw: Optional[bool],
        keep_alive: Optional[Union[float, str]]
    ):
        """Generate a completion."""
        pass

    def chat(
        self, model: str, messages: Optional[List[dict]],
        options: dict, template: str, keep_alive: Optional[Union[float, str]]
    ):
        """Generate a chat completion."""
        pass

    def create(
        self, name: str, modelfile: Optional[str], path: Optional[str]
    ):
        """Create a model."""
        pass

    def list(self):
        """List local models."""
        pass

    def show(self, name: str):
        """Show a model's information."""
        pass

    def copy(self, source: str, destination: str):
        """Copy a model."""
        pass

    def delete(self, name: str):
        """Delete a model."""
        pass

    def pull(self, name: str, insecure: Optional[bool]):
        """Pull a model."""
        pass

    def push(self, name: str):
        """Push a model."""
        pass

    def embeddings(
        self, model: str, prompt: str, options: dict,
        keep_alive: Optional[Union[float, str]]
    ):
        """Generate embeddings."""
        pass
