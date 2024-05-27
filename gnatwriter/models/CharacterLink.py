from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Character, Link, Base


class CharacterLink(Base):
    """The CharacterLink class represents the relationship between a character and a link.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        link_id: int
            The link's id
        created: str
            The creation datetime of the link between the Character and the Link
        user: User
            The user who owns this entry
        character: Character
            The character that the link belongs to
        link: Link
            The link that the character has

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

    __tablename__ = 'characters_links'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('characters.id'), primary_key=True
    )
    link_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('links.id'), primary_key=True
    )
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship(
        "Character", back_populates="links"
    )
    link: Mapped["Link"] = relationship(
        "Link", back_populates="characters", lazy='joined'
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<CharacterLink {self.character.first_name!r} {self.character.last_name!r} - {self.link.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.character.first_name} {self.character.last_name} - {self.link.title}'

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
            'link_id': self.link_id,
            'created': str(self.created),
            'link': self.link.serialize()
        }

    def unserialize(self, data: dict) -> "CharacterLink":
        """Updates the relationship's attributes with the values from the dictionary.

        Returns
        -------
        CharacterLink
            The updated relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.link_id = data.get('link_id', self.link_id)
        self.created = data.get('created', self.created)

        return self
