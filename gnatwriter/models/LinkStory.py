from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Link, Story, Base


class LinkStory(Base):
    """The LinkStory class represents the relationship between a link and a story.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        link_id: int
            The link's id
        story_id: int
            The story's id
        created: str
            The creation datetime of the link between the Link and the Story
        user: User
            The user who owns this entry
        link: Link
            The link that the story belongs to
        story: Story
            The story that the link has

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

    __tablename__ = 'links_stories'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    link_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('links.id'), primary_key=True
    )
    story_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('stories.id'), primary_key=True
    )
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    link: Mapped["Link"] = relationship(
        "Link", back_populates="stories", lazy="joined"
    )
    story: Mapped["Story"] = relationship(
        "Story", back_populates="links"
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<LinkStory {self.link.title!r} - {self.story.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.link.title} - {self.story.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'link_id': self.link_id,
            'story_id': self.story_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "LinkStory":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        LinkStory
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.link_id = data.get('link_id', self.link_id)
        self.story_id = data.get('story_id', self.story_id)
        self.created = data.get('created', self.created)

        return self
