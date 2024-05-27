from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Event, Note, Base


class EventNote(Base):
    """The EventNote class represents the relationship between an event and a note.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        event_id: int
            The event's id
        note_id: int
            The note's id
        created: str
            The creation datetime of the link between the Event and the Note
        user: User
            The user who owns this entry
        event: Event
            The event that the note belongs to
        note: Note
            The note that the event has

    Methods
    -------
        __repr__()
            Returns a string representation of the relationship
        __str__()
            Returns a string representation of the relationship
        serialize()
            Returns a dictionary representation of the relationship
        unserialize(data: dict)
            Updates the relationship's attributes with the values from the dictionary
    """

    __tablename__ = 'events_notes'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('events.id'), primary_key=True
    )
    note_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('notes.id'), primary_key=True
    )
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    event: Mapped["Event"] = relationship("Event", back_populates="notes")
    note: Mapped["Note"] = relationship("Note", back_populates="events")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<EventNote {self.event.title!r} - {self.note.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.event.title} - {self.note.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'event_id': self.event_id,
            'note_id': self.note_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "EventNote":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        EventNote
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.event_id = data.get('event_id', self.event_id)
        self.note_id = data.get('note_id', self.note_id)
        self.created = data.get('created', self.created)

        return self

