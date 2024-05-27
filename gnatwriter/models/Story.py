from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import User, Chapter, AuthorStory, Bibliography, Submission, LinkStory, NoteStory, CharacterStory, \
    Base


class Story(Base):
    """The Story class represents a story in the application.

    Attributes
    ----------
        id: int
            The story's id
        user_id: int
            The id of the owner of this entry
        title: str
            The story's title
        description: str
            The story's description
        created: str
            The creation datetime of the story
        modified: str
            The last modification datetime of the story
        user: User
            The user who owns this entry
        chapters: List[Chapter]
            The chapters that the story has
        authors: List[AuthorStory]
            The authors that the story has
        references: List[Bibliography]
            The references that the story has
        submissions: List[Submission]
            The submissions that the story has
        links: List[LinkStory]
            The links that the story has
        notes: List[NoteStory]
            The notes that the story has

    Methods
    -------
        __repr__()
            Returns a string representation of the story
        __str__()
            Returns a string representation of the story
        serialize()
            Returns a dictionary representation of the story
        unserialize(data: dict)
            Updates the story's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_description(description: str)
            Validates the description's length
    """

    __tablename__ = 'stories'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship("User", back_populates="stories")
    chapters: Mapped[Optional[List["Chapter"]]] = relationship(
        "Chapter", back_populates="story", lazy="joined",
        cascade="all, delete, delete-orphan")
    authors: Mapped[Optional[List["AuthorStory"]]] = relationship(
        "AuthorStory", back_populates="story", lazy="joined",
        cascade="all, delete, delete-orphan")
    references: Mapped[Optional[List["Bibliography"]]] = relationship(
        "Bibliography", back_populates="story", lazy="joined",
        cascade="all, delete, delete-orphan")
    submissions: Mapped[Optional[List["Submission"]]] = relationship(
        "Submission", back_populates="story", lazy="joined",
        cascade="all, delete, delete-orphan")
    links: Mapped[Optional[List["LinkStory"]]] = relationship(
        "LinkStory", back_populates="story", lazy="joined",
        cascade="all, delete, delete-orphan")
    notes: Mapped[Optional[List["NoteStory"]]] = relationship(
        "NoteStory", back_populates="story", lazy="joined",
        cascade="all, delete, delete-orphan")
    characters: Mapped[Optional[List["CharacterStory"]]] = relationship(
        "CharacterStory", back_populates="story",
        cascade="all, delete, delete-orphan")

    def __repr__(self):
        """Returns a string representation of the story.

        Returns
        -------
        str
            A string representation of the story
        """

        return f'<Story {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the story.

        Returns
        -------
        str
            A string representation of the story
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the story.

        Returns
        -------
        dict
            A dictionary representation of the story
        """

        authors = []
        if self.authors:
            for author_story in self.authors:
                authors.append(author_story.author.serialize())

        links = []
        if self.links:
            for link_story in self.links:
                links.append(link_story.link.serialize())

        notes = []
        if self.notes:
            for note_story in self.notes:
                notes.append(note_story.note.serialize())

        chapters = []
        if self.chapters:
            for chapter in self.chapters:
                chapters.append(chapter.serialize())

        escaped_title = self.title.replace('"', "'").replace('/', '\\/')
        escaped_description = None

        if self.description:
            escaped_description = self.description.replace('"', '\\"').replace('/', '\\/')

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': escaped_title,
            'description': escaped_description,
            'created': str(self.created),
            'modified': str(self.modified),
            'authors': authors,
            'links': links,
            'notes': notes,
            'chapters': chapters
        }

    def unserialize(self, data: dict) -> "Story":
        """Updates the story's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the story

        Returns
        -------
        Story
            The unserialized story
        """

        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
        self.description = data.get('description', self.description)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length.

        Parameters
        ----------
        title: str
            The story's title

        Returns
        -------
        str
            The validated title
            :param key:
        """

        if not title:
            raise ValueError("A story title is required.")

        if len(title) > 250:
            raise ValueError("The story title can have no more than 250 characters.")

        return title

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length.

        Parameters
        ----------
        description: str
            The story's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("The story description can have no more than 65,535 characters.")

        return description
