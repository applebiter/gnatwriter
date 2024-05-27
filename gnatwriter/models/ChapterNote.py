from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Story, Chapter, Note, Base


class ChapterNote(Base):
    """The ChapterNote class represents the relationship between a chapter and a note.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        story_id: int
            The story's id
        chapter_id: int
            The chapter's id
        note_id: int
            The note's id
        created: int
            The creation datetime of the link between the Chapter and the Note
        user: User
            The user who owns this entry
        story: Story
            The story that the chapter belongs to
        chapter: Chapter
            The chapter that the note belongs to
        note: Note
            The note that the chapter has

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

    __tablename__ = 'chapters_notes'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'))
    chapter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('chapters.id'), primary_key=True
    )
    note_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('notes.id'), primary_key=True
    )
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    story: Mapped["Story"] = relationship("Story")
    chapter: Mapped["Chapter"] = relationship(
        "Chapter", back_populates="notes"
    )
    note: Mapped["Note"] = relationship(
        "Note", back_populates="chapters", lazy="joined"
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<ChapterNote {self.chapte.title!r} - {self.note.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.chapter.title} - {self.note.title}'

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
            'note_id': self.note_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "ChapterNote":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        ChapterNote
            The updated relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.story_id = data.get('story_id', self.story_id)
        self.chapter_id = data.get('chapter_id', self.chapter_id)
        self.note_id = data.get('note_id', self.note_id)
        self.created = data.get('created', self.created)

        return self
