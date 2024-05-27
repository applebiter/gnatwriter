from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import Scene, User, Story, ChapterLink, ChapterNote, Base


class Chapter(Base):
    """The Chapter class represents a chapter of a story.

    Attributes
    ----------
        id: int
            The chapter's id
        user_id: int
            The id of the owner of this entry
        story_id: int
            The story's id
        position: int
            The chapter's position in the story
        title: str
            The chapter's title
        description: str
            The chapter's description
        created: str
            The chapter's creation date in datetime form: yyy-mm-dd hh:mm:ss
        modified: str
            The chapter's last modification date in datetime form: yyy-mm-dd hh:mm:ss
        user: User
            The user who owns this entry
        story: Story
            The story that the chapter belongs to
        links: List[ChapterLink]
            The links of the chapter
        notes: List[ChapterNote]
            The notes of the chapter

    Methods
    -------
        __repr__()
            Returns a string representation of the chapter
        __str__()
            Returns a string representation of the chapter
        serialize()
            Returns a dictionary representation of the chapter
        unserialize(data: dict)
            Updates the chapter's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_description(description: str)
            Validates the description's length
    """

    __tablename__ = 'chapters'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'))
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    scenes: Mapped[Optional[List["Scene"]]] = relationship(
        "Scene", back_populates="chapter", lazy="joined",
        cascade="all, delete, delete-orphan")
    user: Mapped["User"] = relationship("User")
    story: Mapped["Story"] = relationship("Story", back_populates="chapters")
    links: Mapped[Optional[List["ChapterLink"]]] = relationship(
        "ChapterLink", back_populates="chapter", lazy="joined",
        cascade="all, delete, delete-orphan")
    notes: Mapped[Optional[List["ChapterNote"]]] = relationship(
        "ChapterNote", back_populates="chapter", lazy="joined",
        cascade="all, delete, delete-orphan")

    def __repr__(self):
        """Returns a string representation of the chapter.

        Returns
        -------
        str
            A string representation of the chapter
        """

        return f'<Chapter {self.position}: {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the chapter.

        Returns
        -------
        str
            A string representation of the chapter
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the chapter.

        Returns
        -------
        dict
            A dictionary representation of the chapter
        """

        links = []
        if self.links:
            for chapter_link in self.links:
                links.append(chapter_link.link.serialize())

        notes = []
        if self.notes:
            for chapter_note in self.notes:
                notes.append(chapter_note.note.serialize())

        scenes = []
        if self.scenes:
            for scene in self.scenes:
                scenes.append(scene.serialize())

        escaped_title = self.title.replace('"', "'").replace('/', '\\/')
        escaped_description = None

        if self.description:
            escaped_description = self.description.replace('"', "'").replace('/', '\\/')

        return {
            'id': self.id,
            'user_id': self.user_id,
            'story_id': self.story_id,
            'position': self.position,
            'title': escaped_title,
            'description': escaped_description,
            'created': str(self.created),
            'modified': str(self.modified),
            'links': links,
            'notes': notes,
            'scenes': scenes
        }

    def unserialize(self, data: dict) -> "Chapter":
        """Updates the chapter's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the chapter

        Returns
        -------
        Chapter
            The updated chapter
        """

        self.id = data.get('id', self.id)
        self.user_id = data.get('user_id', self.user_id)
        self.story_id = data.get('story_id', self.story_id)
        self.position = data.get('position', self.position)
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
            The chapter's title

        Returns
        -------
        str
            The validated title
        """

        if not title:
            raise ValueError("A chapter title is required.")

        if len(title) > 250:
            raise ValueError("The chapter title must have no more than 250 characters.")

        return title

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length.

        Parameters
        ----------
        description: str
            The chapter's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("The chapter description must have no more than 65535 characters.")

        return description
