from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Character, Note, Base


class CharacterNote(Base):
    """The CharacterNote class represents the relationship between a character and a note.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        note_id: int
            The note's id
        created: str
            The creation datetime of the link between the Character and the Note
        user: User
            The user who owns this entry
        character: Character
            The character that the note belongs to
        note: Note
            The note that the character has

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

    __tablename__ = 'characters_notes'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('characters.id'), primary_key=True
    )
    note_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('notes.id'), primary_key=True
    )
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship(
        "Character", back_populates="notes"
    )
    note: Mapped["Note"] = relationship(
        "Note", back_populates="characters", lazy='joined'
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<CharacterNote {self.character.first_name!r} {self.character.last_name!r} - {self.note.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.character.first_name} {self.character.last_name} - {self.note.title}'

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
            'note_id': self.note_id,
            'created': str(self.created),
            'note': self.note.serialize()
        }

    def unserialize(self, data: dict) -> "CharacterNote":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        CharacterNote
            The updated relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.note_id = data.get('note_id', self.note_id)
        self.created = data.get('created', self.created)

        return self
