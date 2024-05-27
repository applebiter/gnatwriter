from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Character, Story, Base


class CharacterStory(Base):
    """The CharacterStory class represents the relationship between a character and a story.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        story_id: int
            The story's id
        created: str
            The creation datetime of the link between the Character and the Story
        user: User
            The user who owns this entry
        character: Character
            The character that the story belongs to
        story: Story
            The story that the character has

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

    __tablename__ = 'characters_stories'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('characters.id'), primary_key=True
    )
    story_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('stories.id'), primary_key=True
    )
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship(
        "Character", back_populates="stories"
    )
    story: Mapped["Story"] = relationship(
        "Story", back_populates="characters", lazy="joined"
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<CharacterStory {self.character.__str__()!r} - {self.story.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.character.__str__()} - {self.story.title}'

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
            'story_id': self.story_id,
            'created': str(self.created),
            'story_name': self.story.title,
        }

    def unserialize(self, data: dict) -> "CharacterStory":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        CharacterStory
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.story_id = data.get('story_id', self.story_id)
        self.created = data.get('created', self.created)

        return self
