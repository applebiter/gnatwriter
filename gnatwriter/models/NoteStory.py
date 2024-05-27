from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Note, Story, Base


class NoteStory(Base):
    """The NoteStory class represents the relationship between a note and a story.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        note_id: int
            The note's id
        story_id: int
            The story's id
        created: str
            The creation datetime of the link between the Note and the Story
        user: User
            The user who owns this entry
        note: Note
            The note that the story belongs to
        story: Story
            The story that the note has

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

    __tablename__ = 'notes_stories'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    note_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('notes.id'), primary_key=True
    )
    story_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('stories.id'), primary_key=True
    )
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    note: Mapped["Note"] = relationship(
        "Note", back_populates="stories", lazy="joined"
    )
    story: Mapped["Story"] = relationship(
        "Story", back_populates="notes"
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<NoteStory {self.note.title!r} - {self.story.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.note.title} - {self.story.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'note_id': self.note_id,
            'story_id': self.story_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "NoteStory":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        NoteStory
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.note_id = data.get('note_id', self.note_id)
        self.story_id = data.get('story_id', self.story_id)
        self.created = data.get('created', self.created)

        return self
