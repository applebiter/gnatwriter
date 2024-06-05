from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, Boolean, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import User, AuthorStory, Base


class Author(Base):
    """The Author class represents an author of a story.

    Attributes
    ----------
        id: int
            The author's id
        user_id: int
            The id of the owner of this entry
        is_pseudonym: bool
            Whether the author is a pseudonym or not
        name: str
            The author's name
        initials: str
            The author's initials
        created: str
            The author's creation date in datetime form: yyy-mm-dd hh:mm:ss
        modified: str
            The author's last modification date in datetime form: yyy-mm-dd hh:mm:ss
        user: User
            The user who owns this entry
        stories: List[AuthorStory]
            The stories that the author has written

    Methods
    -------
        __repr__()
            Returns a string representation of the author
        __str__()
            Returns a string representation of the author
        serialize()
            Returns a dictionary representation of the author
        unserialize(data: dict)
            Updates the author's attributes with the values from the dictionary
        validate_name(name: str)
            Validates the name's length
        validate_initials(initials: str)
            Validates the initials' length
    """

    __tablename__ = 'authors'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    is_pseudonym: Mapped[bool] = mapped_column(Boolean, default=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    initials: Mapped[str] = mapped_column(String(10), nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship("User", back_populates="authors")
    stories: Mapped[Optional[List["AuthorStory"]]] = relationship(
        "AuthorStory", back_populates="author",
        cascade="all, delete, delete-orphan", lazy="joined")

    def __repr__(self):
        """Returns a string representation of the author.

        Returns
        -------
        str
            A string representation of the author
        """

        return f'<Author {self.name!r}>'

    def __str__(self):
        """Returns a string representation of the author.

        Returns
        -------
        str
            A string representation of the author
        """

        return f'Author: {self.name}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the author.

        Returns
        -------
        dict
            A dictionary representation of the author
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'is_pseudonym': self.is_pseudonym,
            'name': self.name,
            'initials': self.initials,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Author":
        """Updates the author's attributes with the values from the dictionary.

        Returns
        -------
        Author
            The updated author
        """

        self.id = data.get('id', self.id)
        self.user_id = data.get('user_id', self.user_id)
        self.is_pseudonym = data.get('is_pseudonym', self.is_pseudonym)
        self.name = data.get('name', self.name)
        self.initials = data.get('initials', self.initials)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("name")
    def validate_name(self, key, name: str) -> str:
        """Validates the name's length.

        Returns
        -------
        str
            The validated name
        """

        if not name:
            raise ValueError("The author name must not be empty.")

        if len(name) > 150:
            raise ValueError("The author's name must not have more than 150 characters.")

        return name

    @validates("initials")
    def validate_initials(self, key, initials: str) -> str:
        """Validates the initials' length.

        Returns
        -------
        str
            The validated initials
        """

        if initials and len(initials) > 10:
            raise ValueError("The author's initials must not have more than 10 characters.")

        return initials
