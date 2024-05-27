from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Character, Event, Base


class CharacterEvent(Base):
    """The CharacterEvent class represents the relationship between a character and an event.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        event_id: int
            The event's id
        created: str
            The creation datetime of the link between the Character and the Event
        user: User
            The user who owns this entry
        character: Character
            The character that the event belongs to
        event: Event
            The event that the character has

    Methods
    -------
        __repr__()
            Returns a string representation of the relationship
        __str__()
            Returns a string representation of the relationship
        serialize():
            Returns a dictionary representation of the relationship
        unserialize(data: dict)
            Updates the relationship's attributes with the values from the dictionary
    """

    __tablename__ = 'characters_events'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'), primary_key=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship("Character", back_populates="events")
    event: Mapped["Event"] = relationship(
        "Event", back_populates="characters", lazy='joined'
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<CharacterEvent {self.character.first_name!r} {self.character.last_name!r} - {self.event.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.character.first_name} {self.character.last_name} - {self.event.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'character_id': self.character_id,
            'event_id': self.event_id,
            'created': str(self.created),
            'event': self.event.title,
        }

    def unserialize(self, data: dict) -> "CharacterEvent":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        CharacterEvent
            The updated relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.event_id = data.get('event_id', self.event_id)
        self.created = data.get('created', self.created)

        return self
