from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Author, Story, Base


class AuthorStory(Base):
    """The AuthorStory class represents the relationship between an Author and a Story.

    Attributes
    ----------
        author_id: int
            The author's id
        story_id: int
            The story's id
        user_id: int
            The id of the owner of this entry
        created: str
            The creation datetime of the link between the Author and the Story
        user: User
            The user who owns this entry
        author: Author
            The author name assigned to the story
        story: Story
            The story that the author (user) wrote

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

    __tablename__ = 'authors_stories'
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('authors.id'), primary_key=True)
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    author: Mapped["Author"] = relationship(
        "Author", back_populates="stories", lazy="joined"
    )
    story: Mapped["Story"] = relationship(
        "Story", back_populates="authors"
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<AuthorStory {self.author.name!r} - {self.story.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'AuthorStory: {self.author.name} - {self.story.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'author_id': self.author_id,
            'story_id': self.story_id,
            'user_id': self.user_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "AuthorStory":
        """Updates the relationship's attributes with the values from the dictionary.

        Returns
        -------
        AuthorStory
            The updated relationship
        """

        self.author_id = data.get('author_id', self.author_id)
        self.story_id = data.get('story_id', self.story_id)
        self.user_id = data.get('user_id', self.user_id)
        self.created = data.get('created', self.created)

        return self
