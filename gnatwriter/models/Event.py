from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import User, EventLink, CharacterEvent, EventNote, Base


class Event(Base):
    """The Event class represents an event that is referenced by one or more stories.

    Attributes
    ----------
        id: int
            The event's id
        user_id: int
            The id of the owner of this entry
        title: str
            The event's title
        description: str
            A description of the event
        start_datetime: str
            The starting datetime of the event
        end_datetime: str
            The ending datetime of the event
        created: str
            The creation datetime of the event
        modified: str
            The last modification datetime of the event
        user: User
            The user who owns this entry
        links: List[EventLink]
            The links that the event has
        characters: List[CharacterEvent]
            The characters that the event has
        notes: List[EventNote]
            The notes that the event has

    Methods
    -------
        __repr__()
            Returns a string representation of the event
        __str__()
            Returns a string representation of the event
        serialize()
            Returns a dictionary representation of the event
        unserialize(data: dict)
            Updates the event's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_description(description: str)
            Validates the description's length
        validate_start_datetime(start_datetime: str)
            Validates the start datetime's format
        validate_end_datetime(end_datetime: str)
            Validates the end datetime's format
    """

    __tablename__ = 'events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    start_datetime: Mapped[str] = mapped_column(DateTime, nullable=True)
    end_datetime: Mapped[str] = mapped_column(DateTime, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="events"
    )
    links: Mapped[Optional[List["EventLink"]]] = relationship(
        "EventLink", back_populates="event", lazy="joined",
        cascade="all, delete, delete-orphan")
    characters: Mapped[Optional[List["CharacterEvent"]]] = relationship(
        "CharacterEvent", back_populates="event", lazy="joined",
        cascade="all, delete, delete-orphan")
    notes: Mapped[Optional[List["EventNote"]]] = relationship(
        "EventNote", back_populates="event", lazy="joined",
        cascade="all, delete, delete-orphan")

    def __repr__(self):
        """Returns a string representation of the event.

        Returns
        -------
        str
            A string representation of the event
        """

        return f'<Event {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the event.

        Returns
        -------
        str
            A string representation of the event
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the event.

        Returns
        -------
        dict
            A dictionary representation of the event
        """

        return {
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Event":
        """Updates the event's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the event

        Returns
        -------
        Event
            The unserialized event
        """

        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
        self.description = data.get('description', self.description)
        self.start_datetime = data.get('start_datetime', self.start_datetime)
        self.end_datetime = data.get('end_datetime', self.end_datetime)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length.

        Parameters
        ----------
        title: str
            The event's title

        Returns
        -------
        str
            The validated title
        """

        if not title:
            raise ValueError("Title cannot be empty")

        return title

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length.

        Parameters
        ----------
        description: str
            The event's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("Description cannot have more than 65,535 characters.")

        return description
