from datetime import datetime
from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import Bibliography, User, Base


class BibliographyAuthor(Base):
    """The BibliographyAuthor class represents an author of a reference.

    Attributes
    ----------
        id: int
            The author's id
        user_id: int
            The id of the owner of this entry
        bibliography_id: int
            The reference's id
        name: str
            The author's name
        initials: str
            The author's initials
        created: str
            The creation datetime of the link between the Bibliography reference and its Author
        user: User
            The user who owns this entry
        reference: Bibliography
            The reference that the author wrote

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

    __tablename__ = 'authors_bibliographies'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    bibliography_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('bibliographies.id')
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    initials: Mapped[str] = mapped_column(String(10), nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    reference: Mapped["Bibliography"] = relationship(
        "Bibliography", back_populates="authors"
    )

    def __repr__(self):
        """Returns a string representation of the author.

        Returns
        -------
        str
            A string representation of the author
        """

        return f'<BibliographyAuthor {self.bibliography.title!r} - {self.name!r}>'

    def __str__(self):
        """Returns a string representation of the author.

        Returns
        -------
        str
            A string representation of the author
        """

        return f'BibliographyAuthor: {self.bibliography.title} - {self.name}'

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
            'bibliography_id': self.bibliography_id,
            'name': self.name,
            'initials': self.initials,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "BibliographyAuthor":
        """Updates the author's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the author

        Returns
        -------
        BibliographyAuthor
            The updated author
        """

        self.id = data.get('id', self.id)
        self.user_id = data.get('user_id', self.user_id)
        self.bibliography_id = data.get('bibliography_id', self.bibliography_id)
        self.name = data.get('name', self.name)
        self.initials = data.get('initials', self.initials)
        self.created = data.get('created', self.created)

        return self

    @validates("name")
    def validate_name(self, key, name: str) -> str:
        """Validates the name's length.

        Parameters
        ----------
        name: str
            The author's name

        Returns
        -------
        str
            The validated name
        """

        if not name:
            raise ValueError("A author name is required.")

        if len(name) > 150:
            raise ValueError("The author's name must have no more than 150 characters.")

        return name

    @validates("initials")
    def validate_initials(self, key, initials: str) -> str:
        """Validates the initials' length.

        Parameters
        ----------
        initials: str
            The author's initials

        Returns
        -------
        str
            The validated initials
        """

        if initials and len(initials) > 10:
            raise ValueError("The author's initials must have no more than 10 characters.")

        return initials
