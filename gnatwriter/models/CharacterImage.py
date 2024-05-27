from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Image, Base, Character


class CharacterImage(Base):
    """The CharacterImage class represents the relationship between a character and an image.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        image_id: int
            The image's id
        position: int
            The position of the image in the character's gallery
        is_default: bool
            Whether the image is the default image for the character
        created: str
            The creation datetime of the link between the Character and the Image
        modified: str
            The last modification datetime of the link between the Character and the Image
        user: User
            The user who owns this entry
        character: Character
            The character that the image belongs to
        image: Image
            The image that the character has

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
    __tablename__ = 'characters_images'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('characters.id'), primary_key=True
    )
    image_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('images.id'), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship(
        "Character", back_populates="images"
    )
    image: Mapped["Image"] = relationship(
        "Image", back_populates="character", lazy="joined"
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<CharacterImage {self.character.first_name!r} {self.character.last_name!r} - {self.image.caption!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.character.first_name} {self.character.last_name} - {self.image.caption}'

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
            'image_id': self.image_id,
            'position': self.position,
            'is_default': self.is_default,
            'created': str(self.created),
            'modified': str(self.modified),
            'image': self.image.serialize()
        }

    def unserialize(self, data: dict) -> "CharacterImage":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        CharacterImage
            The updated relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.image_id = data.get('image_id', self.image_id)
        self.position = data.get('position', self.position)
        self.is_default = data.get('is_default', self.is_default)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self
