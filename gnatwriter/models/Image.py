from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import ImageMimeTypes, User, CharacterImage, ImageLocation, Base


class Image(Base):
    """The Image class represents an image in the application.

    Attributes
    ----------
        id: int
            The image's id
        user_id: int
            The id of the owner of this entry
        caption: str
            The image's caption
        filename: str
            The image's filename
        dirname: str
            The image's directory name
        size_in_bytes: int
            The image's size in bytes
        mime_type: str
            The image's mime type
        created: str
            The creation datetime of the image
        modified: str
            The last modification datetime of the image
        user: User
            The user who owns this entry
        character: List[CharacterImage]
            The characters that the image has
        location: List[ImageLocation]
            The locations that the image has

    Methods
    -------
        __repr__()
            Returns a string representation of the image
        __str__()
            Returns a string representation of the image
        serialize()
            Returns a dictionary representation of the image
        unserialize(data: dict)
            Updates the image's attributes with the values from the dictionary
        validate_caption(caption: str)
            Validates the caption's length
        validate_filename(filename: str)
            Validates the filename's length
        validate_dirname(dirname: str)
            Validates the dirname's length
        validate_size_in_bytes(size_in_bytes: int)
            Validates the size in bytes
        validate_mime_type(mime_type: str)
            Validates the mime type
    """

    __tablename__ = 'images'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    filename: Mapped[str] = mapped_column(String(150), nullable=False)
    dirname: Mapped[str] = mapped_column(String(150), nullable=False)
    size_in_bytes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    mime_type: Mapped[ImageMimeTypes] = mapped_column(
        String(50), nullable=False
    )
    caption: Mapped[str] = mapped_column(String(250), nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship("User", back_populates="images")
    character: Mapped[Optional[List["CharacterImage"]]] = relationship(
        "CharacterImage", back_populates="image",
        cascade="all, delete, delete-orphan")
    location: Mapped[Optional[List["ImageLocation"]]] = relationship(
        "ImageLocation", back_populates="image",
        cascade="all, delete, delete-orphan")

    def __repr__(self):
        """Returns a string representation of the image.

        Returns
        -------
        str
            A string representation of the image
        """

        return f'<Image {self.caption!r}>'

    def __str__(self):
        """Returns a string representation of the image.

        Returns
        -------
        str
            A string representation of the image
        """

        return f'{self.caption}' if self.caption else f'{self.filename}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the image.

        Returns
        -------
        dict
            A dictionary representation of the image
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'caption': self.caption,
            'filename': self.filename,
            'dirname': self.dirname,
            'size_in_bytes': self.size_in_bytes,
            'mime_type': self.mime_type,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Image":
        """Updates the image's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the image

        Returns
        -------
        Image
            The unserialized image
        """

        self.user_id = data.get('user_id', self.user_id)
        self.caption = data.get('caption', self.caption)
        self.filename = data.get('filename', self.filename)
        self.dirname = data.get('dirname', self.dirname)
        self.size_in_bytes = data.get('size_in_bytes', self.size_in_bytes)
        self.mime_type = data.get('mime_type', self.mime_type)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("caption")
    def validate_caption(self, key, caption: str) -> str:
        """Validates the caption's length.

        Parameters
        ----------
        caption: str
            The image's caption

        Returns
        -------
        str
            The validated caption
        """

        if caption and len(caption) > 250:
            raise ValueError("The image caption cannot have more than 250 characters.")
        return caption

    @validates("filename")
    def validate_filename(self, key, filename: str) -> str:
        """Validates the filename's length.

        Parameters
        ----------
        filename: str
            The image's filename

        Returns
        -------
        str
            The validated filename
        """

        if not filename:
            raise ValueError("A filename is required.")

        if len(filename) > 150:
            raise ValueError("The filename cannot have more than 150 characters.")

        return filename

    @validates("dirname")
    def validate_dirname(self, key, dirname: str) -> str:
        """Validates the dirname's length.

        Parameters
        ----------
        dirname: str
            The image's directory name

        Returns
        -------
        str
            The validated directory name
        """

        if not dirname:
            raise ValueError("A directory name is required.")

        if len(dirname) > 150:
            raise ValueError("The directory name cannot have more than 150 characters.")

        return dirname

    @validates("size_in_bytes")
    def validate_size_in_bytes(self, key, size_in_bytes: int) -> int:
        """Validates the size in bytes.

        Parameters
        ----------
        size_in_bytes: int
            The image's size in bytes

        Returns
        -------
        int
            The validated size in bytes
        """

        if size_in_bytes < 0:
            raise ValueError("The size in bytes cannot be negative.")

        return size_in_bytes

    @validates("mime_type")
    def validate_mime_type(self, key, mime_type: str) -> str:
        """Validates the mime type.

        Parameters
        ----------
        mime_type: str
            The image's mime type

        Returns
        -------
        str
            The validated mime type
        """

        if mime_type not in [e.value for e in ImageMimeTypes]:
            raise ValueError("Invalid mime type.")

        return mime_type
