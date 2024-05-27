from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Image, Location, Base


class ImageLocation(Base):
    """The ImageLocation class represents the relationship between an image and a location.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        image_id: int
            The image's id
        location_id: int
            The location's id
        position: int
            The position of the image in the location's gallery
        is_default: bool
            Whether the image is the default image for the location
        created: str
            The creation datetime of the link between the Image and the Location
        modified: str
            The last modification datetime of the link between the Image and the Location
        user: User
            The user who owns this entry
        image: Image
            The image that the location has
        location: Location
            The location that the image belongs to

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

    __tablename__ = 'images_locations'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey('images.id'), primary_key=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey('locations.id'), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    image: Mapped["Image"] = relationship("Image", back_populates="location")
    location: Mapped["Location"] = relationship("Location", back_populates="images")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<ImageLocation {self.image.caption!r} - {self.location.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.image.caption} - {self.location.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'image_id': self.image_id,
            'location_id': self.location_id,
            'position': self.position,
            'is_default': self.is_default,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "ImageLocation":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        ImageLocation
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.image_id = data.get('image_id', self.image_id)
        self.location_id = data.get('location_id', self.location_id)
        self.position = data.get('position', self.position)
        self.is_default = data.get('is_default', self.is_default)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self
