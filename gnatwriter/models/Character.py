from configparser import ConfigParser
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, Date, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import User, CharacterRelationship, CharacterEvent, CharacterTrait, CharacterImage, CharacterLink, \
    CharacterNote, CharacterStory, Base

mbti_types = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]
enneagram_types = [
    "Type 1", "Type 2", "Type 3", "Type 4",
    "Type 5", "Type 6", "Type 7", "Type 8", "Type 9"
]


class Character(Base):
    """The Character class represents a character in one or more stories.

    Attributes
    ----------
        id: int
            The Character ID
        user_id: int
            The id of the owner of this entry
        title: str
            The character's title
        honorific: str
            The character's honorific
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
        ethnicity: str
            The ethnicity of the character
        race: str
            The race of the character
        tribe_or_clan: str
            The tribe or clan of the character
        nationality: str
            The nationality of the character
        religion: str
            The religion of the character
        occupation: str
            The occupation of the character
        education: str
            The education of the character
        marital_status: str
            The marital status of the character
        children: bool
            Whether the character has children
        date_of_birth: str
            The character's date of birth in date form: yyyy-mm-dd
        date_of_death: str
            The character's date of death in date form: yyyy-mm-dd
        description: str
            The character's description
        mbti: str
            The Myers-Briggs Type Indicator of the character
        enneagram: str
            The Enneagram type of the character
        wounds: str
            The character's wounds
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
        validate_honorific(honorific: str)
            Validates the honorific's length
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
        validate_ethnicity(ethnicity: str)
            Validates the ethnicity's length
        validate_race(race: str)
            Validates the length of the race of the character
        validate_tribe_or_clan(tribe_or_clan: str)
            Validates the length of tribe or clan of the character
        validate_nationality(nationality: str)
            Validates the length of the nationality value
        validate_religion(religion: str)
            Validates the length of the religion value
        validate_occupation(occupation: str)
            Validates the length of the occupation value
        validate_education(education: str)
            Validates the length of the education value
        validate_marital_status(marital_status: str)
            Validates the length of the marital status value
        validate_date_of_birth(date_of_birth: str)
            Validates the date of birth's format
        validate_date_of_death(date_of_death: str)
            Validates the date of death's format
        validate_description(description: str)
            Validates the description's length
        validate_mbti(mbti: str)
            Validates the MBTI type of the character
        validate_enneagram(enneagram: str)
            Validates the Enneagram type of the character
        validate_wounds(wounds: str)
            Validates the wounds' length
    """

    __tablename__ = 'characters'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    honorific: Mapped[str] = mapped_column(String(50), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    nickname: Mapped[str] = mapped_column(String(100), nullable=True)
    gender: Mapped[str] = mapped_column(String(50), nullable=True)
    sex: Mapped[str] = mapped_column(String(50), nullable=True)
    ethnicity: Mapped[str] = mapped_column(String(50), nullable=True)
    race: Mapped[str] = mapped_column(String(50), nullable=True)
    tribe_or_clan: Mapped[str] = mapped_column(String(50), nullable=True)
    nationality: Mapped[str] = mapped_column(String(50), nullable=True)
    religion: Mapped[str] = mapped_column(String(50), nullable=True)
    occupation: Mapped[str] = mapped_column(String(50), nullable=True)
    education: Mapped[str] = mapped_column(Text, nullable=True)
    marital_status: Mapped[str] = mapped_column(String(50), nullable=True)
    children: Mapped[bool] = mapped_column(Integer, nullable=True)
    date_of_birth: Mapped[str] = mapped_column(Date, nullable=True)
    date_of_death: Mapped[str] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    mbti: Mapped[str] = mapped_column(String(50), nullable=True)
    enneagram: Mapped[str] = mapped_column(String(50), nullable=True)
    wounds: Mapped[str] = mapped_column(Text, nullable=True)
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
            'honorific': self.honorific,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'nickname': self.nickname,
            'full_name': self.full_name,
            'gender': self.gender,
            'sex': self.sex,
            'ethnicity': self.ethnicity,
            'race': self.race,
            'tribe_or_clan': self.tribe_or_clan,
            'nationality': self.nationality,
            'religion': self.religion,
            'occupation': self.occupation,
            'education': self.education,
            'marital_status': self.marital_status,
            'children': self.children,
            'age': self.age,
            'date_of_birth': str(self.date_of_birth),
            'date_of_death': str(self.date_of_death),
            'description' : self.description,
            'mbti': self.mbti,
            'enneagram': self.enneagram,
            'wounds': self.wounds,
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
        self.honorific = data.get('honorific', self.honorific)
        self.first_name = data.get('first_name', self.first_name)
        self.middle_name = data.get('middle_name', self.middle_name)
        self.last_name = data.get('last_name', self.last_name)
        self.nickname = data.get('nickname', self.nickname)
        self.gender = data.get('gender', self.gender)
        self.sex = data.get('sex', self.sex)
        self.ethnicity = data.get('ethnicity', self.ethnicity)
        self.nationality = data.get('nationality', self.nationality)
        self.religion = data.get('religion', self.religion)
        self.occupation = data.get('occupation', self.occupation)
        self.education = data.get('education', self.education)
        self.marital_status = data.get('marital_status', self.marital_status)
        self.children = data.get('children', self.children)
        self.date_of_birth = data.get('date_of_birth', self.date_of_birth)
        self.date_of_death = data.get('date_of_death', self.date_of_death)
        self.description = data.get('description', self.description)
        self.mbti = data.get('mbti', self.mbti)
        self.enneagram = data.get('enneagram', self.enneagram)
        self.wounds = data.get('wounds', self.wounds)
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

    @validates("honorific")
    def validate_honorific(self, key, honorific: str) -> str:
        """Validates the honorific's length.

        Parameters
        ----------
        honorific: str
            The character's honorific

        Returns
        -------
        str
            The validated honorific
        """

        if honorific and len(honorific) > 50:
            raise ValueError("The value of honorific must have no more than 50 characters.")

        return honorific

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

    @validates("ethnicity")
    def validate_ethnicity(self, key, ethnicity: str) -> str:
        """Validates the ethnicity's length.

        Parameters
        ----------
        ethnicity: str
            The character's ethnicity

        Returns
        -------
        str
            The validated ethnicity
        """

        if ethnicity and len(ethnicity) > 50:
            raise ValueError("The value of ethnicity must have no more than 50 characters.")

        return ethnicity

    @validates("race")
    def validate_race(self, key, race: str) -> str:
        """Validates the length of race of the character.

        Parameters
        ----------
        race: str
            The race of the character

        Returns
        -------
        str
            The validated race
        """

        if race and len(race) > 50:
            raise ValueError("The value of race must have no more than 50 characters.")

        return race

    @validates("tribe_or_clan")
    def validate_tribe_or_clan(self, key, tribe_or_clan: str) -> str:
        """Validates the length of tribe or clan of the character.

        Parameters
        ----------
        tribe_or_clan: str
            The tribe or clan of the character

        Returns
        -------
        str
            The validated tribe or clan
        """

        if tribe_or_clan and len(tribe_or_clan) > 50:
            raise ValueError("The value of tribe or clan must have no more than 50 characters.")

        return tribe_or_clan

    @validates("nationality")
    def validate_nationality(self, key, nationality: str) -> str:
        """Validates the length of the nationality value.

        Parameters
        ----------
        nationality: str
            The nationality of the character

        Returns
        -------
        str
            The character's validated nationality
        """

        if nationality and len(nationality) > 50:
            raise ValueError("The value of nationality must have no more than 50 characters.")

        return nationality

    @validates("religion")
    def validate_religion(self, key, religion: str) -> str:
        """Validates the length of the religion value.

        Parameters
        ----------
        religion: str
            The religion of the character

        Returns
        -------
        str
            The character's validated religion
        """

        if religion and len(religion) > 50:
            raise ValueError("The value of religion must have no more than 50 characters.")

        return religion

    @validates("occupation")
    def validate_occupation(self, key, occupation: str) -> str:
        """Validates the length of the occupation value.

        Parameters
        ----------
        occupation: str
            The occupation of the character

        Returns
        -------
        str
            The character's validated occupation
        """

        if occupation and len(occupation) > 50:
            raise ValueError("The value of occupation must have no more than 50 characters.")

        return occupation

    @validates("education")
    def validate_education(self, key, education: str) -> str:
        """Validates the length of the education value.

        Parameters
        ----------
        education: str
            The education of the character

        Returns
        -------
        str
            The character's validated education
        """

        if education and len(education) > 65535:
            raise ValueError("The value of education must have no more than 65535 characters.")

        return education

    @validates("marital_status")
    def validate_marital_status(self, key, marital_status: str) -> str:
        """Validates the length of the marital status value.

        Parameters
        ----------
        marital_status: str
            The marital status of the character

        Returns
        -------
        str
            The character's validated marital status
        """

        if marital_status and len(marital_status) > 50:
            raise ValueError("The value of marital status must have no more than 50 characters.")

        return marital_status

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

    @validates("mbti")
    def validate_mbti(self, key, mbti: str) -> str:
        """Validates the MBTI type of the character.

        Parameters
        ----------
        mbti: str
            The MBTI type of the character

        Returns
        -------
        str
            The validated MBTI type
        """

        if mbti and mbti not in mbti_types:
            raise ValueError("The MBTI type must be one of the following: INTJ, INTP, ENTJ, ENTP, INFJ, INFP, ENFJ, ENFP, ISTJ, ISFJ, ESTJ, ESFJ, ISTP, ISFP, ESTP, ESFP")

        return mbti

    @validates("enneagram")
    def validate_enneagram(self, key, enneagram: str) -> str:
        """Validates the Enneagram type of the character.

        Parameters
        ----------
        enneagram: str
            The Enneagram type of the character

        Returns
        -------
        str
            The validated Enneagram type
        """

        if enneagram and enneagram not in enneagram_types:
            raise ValueError("The Enneagram type must be one of the following: Type 1, Type 2, Type 3, Type 4, Type 5, Type 6, Type 7, Type 8, Type 9")

        return enneagram

    @validates("wounds")
    def validate_wounds(self, key, wounds: str) -> str:
        """Validates the wounds' length.

        Parameters
        ----------
        wounds: str
            The character's wounds

        Returns
        -------
        str
            The validated wounds
        """

        if wounds and len(wounds) > 65535:
            raise ValueError("The character wounds must have no more than 65535 characters.")

        return wounds

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
            full_name += f'({self.title})'

        if self.honorific:
            if len(full_name) > 0:
                full_name += " "
            full_name += f'{self.honorific}'

        if self.first_name:
            if len(full_name) > 0:
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
