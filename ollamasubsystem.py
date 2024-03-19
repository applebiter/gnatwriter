from os import PathLike
from typing import Any, AnyStr, Union, Optional, Sequence, Mapping, Literal, \
    Iterator
import ollama
from ollama import Options, Message


class OllamaClient:
    """Singleton class for the Ollama client

    This class is a Singleton class that wraps the Ollama client. It is used to
    interact with the Ollama API. It is a Singleton class to ensure that only
    one instance of the Ollama client is created and used throughout the
    application.
    """
    _self = None
    _client = None

    def __new__(cls):
        """Enforce Singleton pattern"""

        if cls._self is None:
            cls._self = super().__new__(cls)

        return cls._self

    def __init__(self):
        """Initialize the class"""

        self._client = ollama.Client()

    def generate(
        self,
        model: str = '',
        prompt: str = '',
        system: str = '',
        template: str = '',
        context: Optional[Sequence[int]] = None,
        stream: bool = False,
        raw: bool = False,
        return_format: Literal['', 'json'] = '',
        images: Optional[Sequence[AnyStr]] = None,
        options: Optional[Options] = None,
        keep_alive: Optional[Union[float, str]] = None,
    ) -> Union[Mapping[str, Any], Iterator[Mapping[str, Any]]]:
        """Generate text using the Ollama API"""
        try:
            return self._client.generate(
                model=model,
                prompt=prompt,
                system=system,
                template=template,
                context=context,
                stream=stream,
                raw=raw,
                format=return_format,
                images=images,
                options=options,
                keep_alive=keep_alive
            )

        except Exception as e:
            raise e

    def chat(
        self,
        model: str = '',
        messages: Optional[Sequence[Message]] = None,
        stream: bool = False,
        return_format: Literal['', 'json'] = '',
        options: Optional[Options] = None,
        keep_alive: Optional[Union[float, str]] = None,
    ) -> Union[Mapping[str, Any], Iterator[Mapping[str, Any]]]:
        """Chat with the Ollama API"""
        try:
            return self._client.chat(
                model=model,
                messages=messages,
                stream=stream,
                format=return_format,
                options=options,
                keep_alive=keep_alive
            )

        except Exception as e:
            raise e

    def embeddings(
        self,
        model: str = '',
        prompt: str = '',
        options: Optional[Options] = None,
        keep_alive: Optional[Union[float, str]] = None,
    ) -> Sequence[float]:
        """Set embeddings using the Ollama API"""
        try:
            return self._client.embeddings(
                model=model,
                prompt=prompt,
                options=options,
                keep_alive=keep_alive
            )

        except Exception as e:
            raise e

    def pull(
        self,
        model: str,
        insecure: bool = False,
        stream: bool = False,
    ) -> Union[Mapping[str, Any], Iterator[Mapping[str, Any]]]:
        """Pull a model from the Ollama API"""
        try:
            return self._client.pull(
                model=model,
                insecure=insecure,
                stream=stream
            )

        except Exception as e:
            raise e

    def push(
        self,
        model: str,
        insecure: bool = False,
        stream: bool = False,
    ) -> Union[Mapping[str, Any], Iterator[Mapping[str, Any]]]:
        """Push a model to the Ollama API"""
        try:
            return self._client.push(
                model=model,
                insecure=insecure,
                stream=stream
            )

        except Exception as e:
            raise e

    def create(
        self,
        model: str,
        path: Optional[Union[str, PathLike]] = None,
        modelfile: Optional[str] = None,
        stream: bool = False,
    ) -> Union[Mapping[str, Any], Iterator[Mapping[str, Any]]]:
        """Create a model using the Ollama API"""
        try:
            return self._client.create(
                model=model,
                path=path,
                modelfile=modelfile,
                stream=stream
            )

        except Exception as e:
            raise e

    def delete(self, model: str) -> Mapping[str, Any]:
        """Delete a model using the Ollama API"""
        try:
            return self._client.delete(model)

        except Exception as e:
            raise e

    def list(self) -> Mapping[str, Any]:
        """List models using the Ollama API"""
        try:
            return self._client.list()

        except Exception as e:
            raise e

    def copy(self, source: str, destination: str) -> Mapping[str, Any]:
        """Copy a model using the Ollama API"""
        try:
            return self._client.copy(source, destination)

        except Exception as e:
            raise e

    def show(self, model: str) -> Mapping[str, Any]:
        """Show a model using the Ollama API"""
        try:
            return self._client.show(model)

        except Exception as e:
            raise e
