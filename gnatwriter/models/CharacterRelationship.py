from datetime import datetime
from sqlalchemy import Integer, ForeignKey, String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import User, Character, CharacterRelationshipTypes, Base


class CharacterRelationship(Base):
    """The CharacterRelationship class represents the relationship between two characters.

    Attributes
    ----------
        id: int
            The character relationship's id
        user_id: int
            The id of the owner of this entry
        parent_id: int
            The parent character's id
        position: int
            The position of the related character in the parent character's life
        related_id: int
            The related character's id
        relationship_type: str
            The type of relationship between the characters
        description: str
            A description of the relationship
        start_date: str
            The starting date of the relationship
        end_date: str
            The ending date of the relationship
        created: str
            The creation datetime of the relationship
        modified: str
            The last modification datetime of the relationship
        user: User
            The user who owns this entry
        parent_character: Character
            The parent character in the relationship
        related_character: Character
            The related character in the relationship

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
        validate_relationship_type(relationship_type: str)
            Validates the relationship type
        validate_description(description: str)
            Validates the description
        validate_start_date(start_date: str)
            Validates the start date
        validate_end_date(end_date: str)
            Validates the end date
    """

    __tablename__ = 'character_relationships'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'))
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    related_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('characters.id')
    )
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    start_date: Mapped[str] = mapped_column(Date, nullable=True)
    end_date: Mapped[str] = mapped_column(Date, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship("User")
    parent_character: Mapped["Character"] = relationship(
        "Character", foreign_keys="CharacterRelationship.parent_id"
    )
    related_character: Mapped["Character"] = relationship(
        "Character", back_populates="character_relationships",
        lazy="joined", foreign_keys="[CharacterRelationship.related_id]"
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return (f'<CharacterRelationship {self.parent_character.first_name!r} {self.parent_character.last_name!r} - '
                f'{self.description!r} - {self.related_character.first_name!r} {self.related_character.last_name!r}>')

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return (f'{self.parent_character.first_name} {self.parent_character.last_name} - '
                f'{self.description!r} - {self.related_character.first_name} {self.related_character.last_name}')

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        related_name = ""

        if self.related_character:
            related_name = self.related_character.full_name

        return {
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'position': self.position,
            'related_id': self.related_id,
            'related_name': related_name,
            'relationship_type': self.relationship_type,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "CharacterRelationship":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        CharacterRelationship
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.parent_id = data.get('parent_id', self.parent_id)
        self.position = data.get('position', self.position)
        self.related_id = data.get('related_id', self.related_id)
        self.relationship_type = data.get('relationship_type', self.relationship_type)
        self.description = data.get('description', self.description)
        self.start_date = data.get('start_date', self.start_date)
        self.end_date = data.get('end_date', self.end_date)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("relationship_type")
    def validate_relationship_type(self, key, relationship_type: str) -> str:
        """Validates the relationship type.

        Parameters
        ----------
        relationship_type: str
            The character relationship type

        Returns
        -------
        str
            The validated relationship type
        """

        if not relationship_type:
            raise ValueError("A character relationship type is required.")

        rtypes = [str(rt.value) for rt in CharacterRelationshipTypes]

        if relationship_type not in rtypes:
            raise ValueError("The character relationship type is invalid.")

        return relationship_type

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description.

        Parameters
        ----------
        description: str
            The character relationship description

        Returns
        -------
        str
            The validated description
        """

        if not description:
            raise ValueError("A character relationship description is required.")

        if len(description) > 250:
            raise ValueError("The character relationship description must have no more than 250 characters.")

        return description
