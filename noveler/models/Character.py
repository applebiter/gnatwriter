from configparser import ConfigParser
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, Date, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from noveler.models import User, CharacterRelationship, CharacterEvent, CharacterTrait, CharacterImage, CharacterLink, \
    CharacterNote, CharacterStory, Base


class Character(Base):
    """The Character class represents a character in a story.

    Attributes
    ----------
        id: int
            The character's id
        user_id: int
            The id of the owner of this entry
        title: str
            The character's title
        first_name: str
            The character's first name
        middle_name: str
            The character's middle name
        last_name: str
            The character's last name
        nickname: str
            The character
        gender: str
            The gender of the character
        sex: str
            The sex of the character
        date_of_birth: str
            The character's date of birth in date form: yyy-mm-dd
        date_of_death: str
            The character's date of death in date form: yyy-mm-dd
        created: str
            The character's creation date in datetime form: yyy-mm-dd hh:mm:ss
        modified: str
            The character's last modification date in datetime form: yyy-mm-dd hh:mm:ss

    Methods
    -------
        __repr__()
            Returns a string representation of the character
        __str__()
            Returns a string representation of the character
        serialize()
            Returns a dictionary representation of the character
        unserialize(data: dict)
            Updates the character's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_first_name(first_name: str):
            Validates the first name's length
        validate_middle_name(middle_name: str)
            Validates the middle name's length
        validate_last_name(last_name: str)
            Validates the last name's length
        validate_nickname(nickname: str)
            Validates the nickname's length
        validate_gender(gender: str)
            Validates the gender's length
        validate_sex(sex: str)
            Validates the sex's length
        validate_date_of_birth(date_of_birth: str)
            Validates the date of birth's format
        validate_date_of_death(date_of_death: str)
            Validates the date of death's format
    """

    __tablename__ = 'characters'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    nickname: Mapped[str] = mapped_column(String(100), nullable=True)
    gender: Mapped[str] = mapped_column(String(50), nullable=True)
    sex: Mapped[str] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[str] = mapped_column(Date, nullable=True)
    date_of_death: Mapped[str] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship("User", back_populates="characters")
    character_relationships: Mapped[Optional[List["CharacterRelationship"]]] = relationship(
        "CharacterRelationship", back_populates="related_character",
        foreign_keys="[CharacterRelationship.related_id]", lazy="joined",
        cascade="all, delete, delete-orphan"
    )
    traits: Mapped[Optional[List["CharacterTrait"]]] = relationship(
        "CharacterTrait", back_populates="character", lazy="joined",
        cascade="all, delete, delete-orphan"
    )
    events: Mapped[Optional[List["CharacterEvent"]]] = relationship(
        "CharacterEvent", back_populates="character",
        cascade="all, delete, delete-orphan", lazy="joined"
    )
    images: Mapped[Optional[List["CharacterImage"]]] = relationship(
        "CharacterImage", back_populates="character", lazy="joined",
        cascade="all, delete, delete-orphan"
    )
    links: Mapped[Optional[List["CharacterLink"]]] = relationship(
        "CharacterLink", back_populates="character", lazy="joined",
        cascade="all, delete, delete-orphan"
    )
    notes: Mapped[Optional[List["CharacterNote"]]] = relationship(
        "CharacterNote", back_populates="character", lazy="joined",
        cascade="all, delete, delete-orphan"
    )
    stories: Mapped[Optional[List["CharacterStory"]]] = relationship(
        "CharacterStory", back_populates="character", lazy="joined",
        cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        """Returns a string representation of the character.

        Returns
        -------
        str
            A string representation of the character
        """

        return f'<Character {self.title!r} {self.first_name!r} {self.last_name!r}>'

    def __str__(self):
        """Returns a string representation of the character.

        Returns
        -------
        str
            A string representation of the character
        """

        title = f'{self.title}' if self.title else ""
        first_name = f' {self.first_name}' if self.first_name else ""
        middle_name = f' {self.middle_name}' if self.middle_name else ""
        last_name = f' {self.last_name}' if self.last_name else ""
        nickname = f' ({self.nickname})' if self.nickname else ""

        return f'{title}{first_name}{middle_name}{last_name}{nickname}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the character.

        Returns
        -------
        dict
            A dictionary representation of the character
        """

        relationships = []
        for character_relationship in self.character_relationships:
            relationships.append(
                character_relationship.serialize()
            )

        traits = []
        for trait in self.traits:
            traits.append(
                trait.serialize()
            )

        images = []
        for character_image in self.images:
            images.append(
                character_image.serialize()
            )

        events = []
        for event in self.events:
            events.append(
                event.serialize()
            )

        links = []
        for character_link in self.links:
            links.append(
                character_link.serialize()
            )

        notes = []
        for character_note in self.notes:
            notes.append(
                character_note.serialize()
            )

        stories = []
        for character_story in self.stories:
            stories.append(
                character_story.serialize()
            )

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'nickname': self.nickname,
            'full_name': self.full_name,  # 'title first_name middle_name last_name (nickname)
            'gender': self.gender,
            'sex': self.sex,
            'age': self.age,
            'date_of_birth': str(self.date_of_birth),
            'date_of_death': str(self.date_of_death),
            'description' : self.description,
            'created': str(self.created),
            'modified': str(self.modified),
            'relationships': relationships,
            'traits': traits,
            'events': events,
            'images': images,
            'links': links,
            'notes': notes,
            'stories': stories
        }

    def unserialize(self, data: dict) -> "Character":
        """Updates the character's attributes with the values from the dictionary.

        Returns
        -------
        Character
            The updated character
        """

        self.id = data.get('id', self.id)
        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
        self.first_name = data.get('first_name', self.first_name)
        self.middle_name = data.get('middle_name', self.middle_name)
        self.last_name = data.get('last_name', self.last_name)
        self.nickname = data.get('nickname', self.nickname)
        self.gender = data.get('gender', self.gender)
        self.sex = data.get('sex', self.sex)
        self.date_of_birth = data.get('date_of_birth', self.date_of_birth)
        self.date_of_death = data.get('date_of_death', self.date_of_death)
        self.description = data.get('description', self.description)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length.

        Parameters
        ----------
        title: str
            The character's title

        Returns
        -------
        str
            The validated title
        """

        if title and len(title) > 100:
            raise ValueError("The character title must have no more than 100 characters.")

        return title

    @validates("first_name")
    def validate_first_name(self, key, first_name: str) -> str:
        """Validates the first name's length.

        Parameters
        ----------
        first_name: str
            The character's first name

        Returns
        -------
        str
            The validated first name
        """

        if first_name and len(first_name) > 100:
            raise ValueError("The character first name must have no more than 100 characters.")

        return first_name

    @validates("middle_name")
    def validate_middle_name(self, key, middle_name: str) -> str:
        """Validates the middle name's length.

        Parameters
        ----------
        middle_name: str
            The character's middle name

        Returns
        -------
        str
            The validated middle name
        """

        if middle_name and len(middle_name) > 100:
            raise ValueError("The character middle name must have no more than 100 characters.")

        return middle_name

    @validates("last_name")
    def validate_last_name(self, key, last_name: str) -> str:
        """Validates the last name's length.

        Parameters
        ----------
        last_name: str
            The character's last name

        Returns
        -------
        str
            The validated last name
        """

        if last_name and len(last_name) > 100:
            raise ValueError("The character last name must have no more than 100 characters.")

        return last_name

    @validates("nickname")
    def validate_nickname(self, key, nickname: str) -> str:
        """Validates the nickname's length.

        Parameters
        ----------
        nickname: str
            The character's nickname

        Returns
        -------
        str
            The validated nickname
        """

        if nickname and len(nickname) > 100:
            raise ValueError("The character nickname must have no more than 100 characters.")

        return nickname

    @validates("gender")
    def validate_gender(self, key, gender: str) -> str:
        """Validates the gender's length.

        Parameters
        ----------
        gender: str
            The character's gender

        Returns
        -------
        str
            The validated gender
        """

        if gender and len(gender) > 50:
            raise ValueError("The gender value must have no more than 50 characters.")

        return gender

    @validates("sex")
    def validate_sex(self, key, sex: str) -> str:
        """Validates the sex's length.

        Parameters
        ----------
        sex: str
            The character's sex

        Returns
        -------
        str
            The validated sex
        """

        if sex and len(sex) > 50:
            raise ValueError("The value of sex must have no more than 50 characters.")

        return sex

    @validates("date_of_birth")
    def validate_date_of_birth(self, key, date_of_birth: str) -> datetime | None:
        """Validates the date of birth's format.

        Parameters
        ----------
        date_of_birth: str
            The character's date of birth in date form: yyy-mm-dd

        Returns
        -------
        str
            The validated date of birth
        """

        config = ConfigParser()
        config.read("config.cfg")
        date_format = config.get("datetime", "date_format")

        if date_of_birth and bool(datetime.strptime(date_of_birth, date_format)) is False:
            raise ValueError("The date of birth must be in the format 'YYYY-MM-DD'.")

        if date_of_birth:
            return datetime.strptime(date_of_birth, date_format)

        else:
            return None

    @validates("date_of_death")
    def validate_date_of_death(self, key, date_of_death: str) -> datetime | None:
        """Validates the date of death's format.

        Parameters
        ----------
        date_of_death: str
            The character's date of death in date form: yyy-mm-dd

        Returns
        -------
        str
            The validated date of death
        """

        config = ConfigParser()
        config.read("config.cfg")
        date_format = config.get("datetime", "date_format")

        if date_of_death and bool(datetime.strptime(date_of_death, date_format)) is False:
            raise ValueError("The date of death must be in the format 'YYYY-MM-DD'.")

        if date_of_death:
            return datetime.strptime(date_of_death, date_format)

        else:
            return None

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length.

        Parameters
        ----------
        description: str
            The character's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("The character description must have no more than 65535 characters.")

        return description

    @property
    def age(self) -> int:
        """Returns the character's age.

        Returns
        -------
        int
            The character's age
        """

        if self.date_of_birth:
            if self.date_of_death:
                return self.date_of_death.year - self.date_of_birth.year

            else:
                return datetime.now().year - self.date_of_birth.year

        else:
            return 0

    @property
    def full_name(self) -> str:
        """Returns the character's full name.

        Returns
        -------
        str
            The character's full name
        """

        full_name = ""

        if self.title:
            full_name += f'{self.title} '

        if self.first_name:
            if self.title:
                full_name += " "
            full_name += f'{self.first_name}'

        if self.middle_name:
            if self.first_name or self.title:
                full_name += " "
            full_name += f'{self.middle_name}'

        if self.last_name:
            if self.middle_name or self.first_name or self.title:
                full_name += " "
            full_name += f'{self.last_name}'

        if self.nickname:
            if len(full_name) > 0:
                full_name += " "
            full_name += f'({self.nickname})'

        return f'{full_name}'
