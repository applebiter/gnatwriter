from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import User, NoteStory, ChapterNote, NoteScene, CharacterNote, EventNote, LocationNote, Base


class Note(Base):
    """The Note class represents a note.

    Attributes
    ----------
        id: int
            The note's id
        user_id: int
            The id of the owner of this entry
        title: str
            The note's title
        content: str
            The note's content
        created: str
            The creation datetime of the note
        modified: str
            The last modification datetime of the note
        user: User
            The user who owns this entry
        stories: List[NoteStory]
            The stories that the note has
        chapters: List[ChapterNote]
            The chapters that the note has
        scenes: List[NoteScene]
            The scenes that the note has
        characters: List[CharacterNote]
            The characters that the note has
        events: List[EventNote]
            The events that the note has
        locations: List[LocationNote]
            The locations that the note has

    Methods
    -------
        __repr__()
            Returns a string representation of the note
        __str__()
            Returns a string representation of the note
        serialize()
            Returns a dictionary representation of the note
        unserialize(data: dict)
            Updates the note's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_content(content: str)
            Validates the content's length
    """

    __tablename__ = 'notes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship("User", back_populates="notes")
    stories: Mapped[Optional[List["NoteStory"]]] = relationship(
        "NoteStory", back_populates="note",
        cascade="all, delete, delete-orphan")
    chapters: Mapped[Optional[List["ChapterNote"]]] = relationship(
        "ChapterNote", back_populates="note",
        cascade="all, delete, delete-orphan")
    scenes: Mapped[Optional[List["NoteScene"]]] = relationship(
        "NoteScene", back_populates="note",
        cascade="all, delete, delete-orphan")
    characters: Mapped[Optional[List["CharacterNote"]]] = relationship(
        "CharacterNote", back_populates="note",
        cascade="all, delete, delete-orphan")
    events: Mapped[Optional[List["EventNote"]]] = relationship(
        "EventNote", back_populates="note",
        cascade="all, delete, delete-orphan")
    locations: Mapped[Optional[List["LocationNote"]]] = relationship(
        "LocationNote", back_populates="note",
        cascade="all, delete, delete-orphan")

    def __repr__(self):
        """Returns a string representation of the note.

        Returns
        -------
        str
            A string representation of the note
        """

        return f'<Note {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the note.

        Returns
        -------
        str
            A string representation of the note
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the note.

        Returns
        -------
        dict
            A dictionary representation of the note
        """

        escaped_title = self.title.replace('"', '\\"').replace('/', '\\/')
        escaped_content = self.content.replace('"', '\\"').replace('/', '\\/')

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': escaped_title,
            'content': escaped_content,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Note":
        """Updates the note's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the note

        Returns
        -------
        Note
            The unserialized note
        """

        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
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
            The note's title

        Returns
        -------
        str
            The validated title
        """

        if not title:
            raise ValueError("A note title is required.")

        if len(title) > 250:
            raise ValueError("The note title can have no more than 250 characters.")

        return title

    @validates("content")
    def validate_content(self, key, content: str) -> str:
        """Validates the content's length

        Parameters
        ----------
        content: str
            The note's content

        Returns
        -------
        str
            The validated content
        """

        if content and len(content) > 65535:
            raise ValueError("The note content can have no more than 65,535 characters.")

        return content
