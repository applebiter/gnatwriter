from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import User, LinkStory, ChapterLink, LinkScene, CharacterLink, EventLink, LinkLocation, Base
from validators import url as url_validator


class Link(Base):
    """The Link class represents a web link in the application.

    Attributes
    ----------
        id: int
            The link's id
        user_id: int
            The id of the owner of this entry
        title: str
            The link's title
        url: str
            The link's URL
        created: str
            The creation datetime of the link
        modified: str
            The last modification datetime of the link
        user: User
            The user who owns this entry
        stories: List[LinkStory]
            The stories that the link has
        chapters: List[ChapterLink]
            The chapters that the link has
        scenes: List[LinkScene]
            The scenes that the link has
        characters: List[CharacterLink]
            The characters that the link has
        events: List[EventLink]
            The events that the link has
        locations: List[LinkLocation]
            The locations that the link has

    Methods
    -------
        __repr__()
            Returns a string representation of the link
        __str__()
            Returns a string representation of the link
        serialize()
            Returns a dictionary representation of the link
        unserialize(data: dict)
            Updates the link's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_url(url: str)
            Validates the URL's length and format
    """

    __tablename__ = 'links'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    url: Mapped[str] = mapped_column(String(200), nullable=False)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship("User", back_populates="links")
    stories: Mapped[Optional[List["LinkStory"]]] = relationship(
        "LinkStory", back_populates="link",
        cascade="all, delete, delete-orphan")
    chapters: Mapped[Optional[List["ChapterLink"]]] = relationship(
        "ChapterLink", back_populates="link",
        cascade="all, delete, delete-orphan")
    scenes: Mapped[Optional[List["LinkScene"]]] = relationship(
        "LinkScene", back_populates="link",
        cascade="all, delete, delete-orphan")
    characters: Mapped[Optional[List["CharacterLink"]]] = relationship(
        "CharacterLink", back_populates="link",
        cascade="all, delete, delete-orphan")
    events: Mapped[Optional[List["EventLink"]]] = relationship(
        "EventLink", back_populates="link",
        cascade="all, delete, delete-orphan")
    locations: Mapped[Optional[List["LinkLocation"]]] = relationship(
        "LinkLocation", back_populates="link",
        cascade="all, delete, delete-orphan")

    def __repr__(self):
        """Returns a string representation of the link.

        Returns
        -------
        str
            A string representation of the link
        """

        return f'<Link {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the link.

        Returns
        -------
        str
            A string representation of the link
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the link.

        Returns
        -------
        dict
            A dictionary representation of the link
        """

        escaped_title = self.title.replace('"', '\\"').replace('/', '\\/')
        escaped_url = self.description.replace('"', '\\"').replace('/', '\\/')

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': escaped_title,
            'url': escaped_url,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Link":
        """Updates the link's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the link

        Returns
        -------
        Link
            The unserialized link
        """

        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
        self.url = data.get('url', self.url)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length.

        Parameters
        ----------
        title: str
            The link's title

        Returns
        -------
        str
            The validated title
        """

        if not title:
            raise ValueError("A link title is required.")

        if len(title) > 250:
            raise ValueError("The link title can have no more than 250 characters.")

        return title

    @validates("url")
    def validate_url(self, key, url: str) -> str:
        """Validates the URL's length and format.

        Parameters
        ----------
        url: str
            The link's URL

        Returns
        -------
        str
            The validated URL
        """

        if not url:
            raise ValueError("A link URL is required.")

        if len(url) > 200:
            raise ValueError("The link URL can have no more than 200 characters.")

        if not url_validator(url):
            raise ValueError("The link URL is not valid.")

        return url
