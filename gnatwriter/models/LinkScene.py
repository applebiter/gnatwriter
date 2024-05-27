from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Link, Scene, Base


class LinkScene(Base):
    """The LinkScene class represents the relationship between a link and a scene.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        link_id: int
            The link's id
        scene_id: int
            The scene's id
        created: str
            The creation datetime of the link between the Link and the Scene
        user: User
            The user who owns this entry
        link: Link
            The link that the scene belongs to
        scene: Scene
            The scene that the link has

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

    __tablename__ = 'links_scenes'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    link_id: Mapped[int] = mapped_column(Integer, ForeignKey('links.id'), primary_key=True)
    scene_id: Mapped[int] = mapped_column(Integer, ForeignKey('scenes.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    link: Mapped["Link"] = relationship(
        "Link", back_populates="scenes", lazy='joined'
    )
    scene: Mapped["Scene"] = relationship(
        "Scene", back_populates="links"
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<LinkScene {self.link.title!r} - {self.scene.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.link.title} - {self.scene.title}'

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
            'scene_id': self.scene_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "LinkScene":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        LinkScene
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.link_id = data.get('link_id', self.link_id)
        self.scene_id = data.get('scene_id', self.scene_id)
        self.created = data.get('created', self.created)

        return self
