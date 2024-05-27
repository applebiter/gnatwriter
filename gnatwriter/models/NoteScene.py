from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Note, Scene, Base


class NoteScene(Base):
    """The NoteScene class represents the relationship between a note and a scene.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        note_id: int
            The note's id
        scene_id: int
            The scene's id
        created: str
            The creation datetime of the link between the Note and the Scene
        user: User
            The user who owns this entry
        note: Note
            The note that the scene belongs to
        scene: Scene
            The scene that the note has

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

    __tablename__ = 'notes_scenes'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey('notes.id'), primary_key=True)
    scene_id: Mapped[int] = mapped_column(Integer, ForeignKey('scenes.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    note: Mapped["Note"] = relationship(
        "Note", back_populates="scenes", lazy="joined"
    )
    scene: Mapped["Scene"] = relationship(
        "Scene", back_populates="notes"
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<NoteScene {self.note.title!r} - {self.scene.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.note.title} - {self.scene.title}'

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
            'scene_id': self.scene_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "NoteScene":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        NoteScene
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.note_id = data.get('note_id', self.note_id)
        self.scene_id = data.get('scene_id', self.scene_id)
        self.created = data.get('created', self.created)

        return self
