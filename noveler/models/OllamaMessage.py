from typing import Optional, List


class OllamaMessage:
    def __init__(
            self, role: str, content: str, images: Optional[List[str]] = None
    ):
        self._role = role
        self._content = content
        self._images = images

    def __repr__(self):
        return f'<OllamaMessage {self._role!r}: {self._content[:50]!r}>'

    def __str__(self):
        return f"{self._role}: {self._content[:50]}"

    def serialize(self) -> dict:
        return {
            'role': self._role,
            'content': self._content,
            'images': self._images,
        }

    def unserialize(self, data: dict) -> "OllamaMessage":
        self._role = data.get('role', self._role)
        self._content = data.get('content', self._content)
        self._images = data.get('images', self._images)

        return self
