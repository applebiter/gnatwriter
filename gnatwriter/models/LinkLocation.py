from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Link, Location, Base


class LinkLocation(Base):
    """The LinkLocation class represents the relationship between a link and a location.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        link_id: int
            The link's id
        location_id: int
            The location's id
        created: str
            The creation datetime of the link between the Link and the Location
        user: User
            The user who owns this entry
        link: Link
            The link that the location belongs to
        location: Location
            The location that the link belongs to

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

    __tablename__ = 'links_locations'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    link_id: Mapped[int] = mapped_column(Integer, ForeignKey('links.id'), primary_key=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey('locations.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    link: Mapped["Link"] = relationship("Link", back_populates="locations")
    location: Mapped["Location"] = relationship("Location", back_populates="links")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<LinkLocation {self.link.title!r} - {self.location.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.link.title} - {self.location.title}'

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
            'location_id': self.location_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "LinkLocation":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        LinkLocation
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.link_id = data.get('link_id', self.link_id)
        self.location_id = data.get('location_id', self.location_id)
        self.created = data.get('created', self.created)

        return self
