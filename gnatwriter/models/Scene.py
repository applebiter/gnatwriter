from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import Chapter, User, LinkScene, NoteScene, Base


class Scene(Base):
    """The Scene class represents a scene in a chapter of a story.

    Attributes
    ----------
        id: int
            The scene's id
        user_id: int
            The id of the owner of this entry
        story_id: int
            The story's id
        chapter_id: int
            The chapter's id
        position: int
            The scene's position in the chapter
        title: str
            The scene's title
        description: str
            The scene's description
        content: str
            The scene's content
        created: str
            The creation datetime of the scene
        modified: str
            The last modification datetime of the scene
        user: User
            The user who owns this entry
        links: List[LinkScene]
            The links that the scene has
        notes: List[NoteScene]
            The notes that the scene has

    Methods
    -------
        __repr__()
            Returns a string representation of the scene
        __str__()
            Returns a string representation of the scene
        serialize()
            Returns a dictionary representation of the scene
        unserialize(data: dict)
            Updates the scene's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_description(description: str)
            Validates the description's length
        validate_content(content: str)
            Validates the content's length
    """

    __tablename__ = 'scenes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'))
    chapter_id: Mapped[int] = mapped_column(Integer, ForeignKey('chapters.id'))
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(String(250), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="scenes")
    user: Mapped["User"] = relationship("User")
    links: Mapped[Optional[List["LinkScene"]]] = relationship(
        "LinkScene", back_populates="scene", lazy="joined",
        cascade="all, delete, delete-orphan")
    notes: Mapped[Optional[List["NoteScene"]]] = relationship(
        "NoteScene", back_populates="scene", lazy="joined",
        cascade="all, delete, delete-orphan")

    def __repr__(self):
        """Returns a string representation of the scene.

        Returns
        -------
        str
            A string representation of the scene
        """

        return f'<Scene {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the scene.

        Returns
        -------
        str
            A string representation of the scene
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the scene.

        Returns
        -------
        dict
            A dictionary representation of the scene
        """

        links = []
        if self.links:
            for link_scene in self.links:
                links.append(link_scene.link.serialize())

        notes = []
        if self.notes:
            for note_scene in self.notes:
                notes.append(note_scene.note.serialize())

        escaped_title = self.title.replace('"', '\\"').replace('/', '\\/')

        escaped_description = None
        escaped_content = None

        if self.description:
            escaped_description = self.description.replace('"', "'").replace('/', '\\/')

        if self.content:
            escaped_content = self.content.replace('"', "'").replace('/', '\\/')

        return {
            'id': self.id,
            'user_id': self.user_id,
            'story_id': self.story_id,
            'chapter_id': self.chapter_id,
            'position': self.position,
            'title': escaped_title,
            'description': escaped_description,
            'content': escaped_content,
            'created': str(self.created),
            'modified': str(self.modified),
            'links': links,
            'notes': notes
        }

    def unserialize(self, data: dict) -> "Scene":
        """Updates the scene's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the scene

        Returns
        -------
        Scene
            The unserialized scene
        """

        self.user_id = data.get('user_id', self.user_id)
        self.story_id = data.get('story_id', self.story_id)
        self.chapter_id = data.get('chapter_id', self.chapter_id)
        self.position = data.get('position', self.position)
        self.title = data.get('title', self.title)
        self.description = data.get('description', self.description)
        self.content = data.get('content', self.content)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length

        Parameters
        ----------
        title: str
            The scene's title

        Returns
        -------
        str
            The validated title
        """

        if title and len(title) > 250:
            raise ValueError("The scene title can have no more than 250 characters.")

        return title

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length

        Parameters
        ----------
        description: str
            The scene's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("The scene description can have no more than 65,535 characters.")

        return description

    @validates("content")
    def validate_content(self, key, content: str) -> str:
        """Validates the content's length

        Parameters
        ----------
        content: str
            The scene's content

        Returns
        -------
        str
            The validated content
        """

        if content and len(content) > 65535:
            raise ValueError("The scene content can have no more than 65,535 characters.")

        return content
