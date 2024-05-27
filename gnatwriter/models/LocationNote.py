from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Location, Note, Base


class LocationNote(Base):
    """The LocationNote class represents the relationship between a location and a note.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        location_id: int
            The location's id
        note_id: int
            The note's id
        created: str
            The creation datetime of the link between the Location and the Note
        user: User
            The user who owns this entry
        location: Location
            The location that the note belongs to
        note: Note
            The note that the location has

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

    __tablename__ = 'locations_notes'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey('locations.id'), primary_key=True)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey('notes.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    location: Mapped["Location"] = relationship("Location", back_populates="notes")
    note: Mapped["Note"] = relationship("Note", back_populates="locations")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<LocationNote {self.location.title!r} - {self.note.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.location.title} - {self.note.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'location_id': self.location_id,
            'note_id': self.note_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "LocationNote":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.location_id = data.get('location_id', self.location_id)
        self.note_id = data.get('note_id', self.note_id)
        self.created = data.get('created', self.created)

        return self
