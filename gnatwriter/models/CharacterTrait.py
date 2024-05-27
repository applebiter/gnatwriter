from datetime import datetime
from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import User, Character, Base


class CharacterTrait(Base):
    """The CharacterTrait class represents a trait of a character.

    Attributes
    ----------
        id: int
            The trait's id
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        position: int
            The position of the trait in the character's traits
        name: str
            The name of the trait
        magnitude: int
            The magnitude of the trait expressed as an integer between 0 and 100
        created: str
            The trait's creation date in datetime form: yyy-mm-dd hh:mm:ss
        modified: str
            The trait's last modification date in datetime form: yyy-mm-dd hh:mm:ss

    Methods
    -------
        __repr__()
            Returns a string representation of the trait
        __str__()
            Returns a string representation of the trait
        serialize()
            Returns a dictionary representation of the trait
        unserialize(data: dict)
            Updates the trait's attributes with the values from the dictionary
        validate_name(name: str)
            Validates the name's length
        validate_magnitude(magnitude: int)
            Validates the magnitude's value
    """

    __tablename__ = 'characters_traits'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('characters.id')
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    magnitude: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship(
        "Character", back_populates="traits", lazy="joined"
    )

    def __repr__(self):
        """Returns a string representation of the trait.

        Returns
        -------
        str
            A string representation of the trait
        """

        return f'{self.character.first_name!r} {self.character.last_name!r} - {self.name!r}'

    def __str__(self):
        """Returns a string representation of the trait.

        Returns
        -------
        str
            A string representation of the trait
        """

        return f'{self.character.first_name} {self.character.last_name} - {self.name}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the trait.

        Returns
        -------
        dict
            A dictionary representation of the trait
        """

        return {
            'user_id': self.user_id,
            'character_id': self.character_id,
            'position': self.position,
            'name': self.name,
            'magnitude': self.magnitude,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "CharacterTrait":
        """Updates the trait's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the trait

        Returns
        -------
        CharacterTrait
            The unserialized trait
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.position = data.get('position', self.position)
        self.name = data.get('name', self.name)
        self.magnitude = data.get('magnitude', self.magnitude)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("name")
    def validate_name(self, key, name: str) -> str:
        """Validates the name's length.

        Parameters
        ----------
        name: str
            The trait's name

        Returns
        -------
        str
            The validated name
        """

        if not name:
            raise ValueError("The trait name cannot be empty.")

        return name

    @validates("magnitude")
    def validate_magnitude(self, key, magnitude: int) -> int:
        """Validates the magnitude's value.

        Parameters
        ----------
        magnitude: int
            The trait's magnitude

        Returns
        -------
        str
            The validated magnitude
        """

        if magnitude < 0:
            raise ValueError("The trait magnitude cannot be negative.")

        if magnitude > 100:
            raise ValueError("The trait magnitude cannot be greater than 100.")

        return magnitude
