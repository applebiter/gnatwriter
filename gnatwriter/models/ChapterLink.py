from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Story, Chapter, Link, Base


class ChapterLink(Base):
    """The ChapterLink class represents the relationship between a chapter and a link.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        story_id: int
            The story's id
        chapter_id: int
            The chapter's id
        link_id: int
            The link's id
        created: str
            The creation datetime of the link between the Chapter and the Link
        user: User
            The user who owns this entry
        story: Story
            The story that the chapter belongs to
        chapter: Chapter
            The chapter that the link belongs to
        link: Link
            The link that the chapter has

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

    __tablename__ = 'chapters_links'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'))
    chapter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('chapters.id'), primary_key=True
    )
    link_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('links.id'), primary_key=True
    )
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    story: Mapped["Story"] = relationship("Story")
    chapter: Mapped["Chapter"] = relationship(
        "Chapter", back_populates="links"
    )
    link: Mapped["Link"] = relationship(
        "Link", back_populates="chapters", lazy="joined"
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<ChapterLink {self.chapter.title!r} - {self.link.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.chapter.title} - {self.link.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'story_id': self.story_id,
            'chapter_id': self.chapter_id,
            'link_id': self.link_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "ChapterLink":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        ChapterLink
            The updated relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.story_id = data.get('story_id', self.story_id)
        self.chapter_id = data.get('chapter_id', self.chapter_id)
        self.link_id = data.get('link_id', self.link_id)
        self.created = data.get('created', self.created)

        return self
