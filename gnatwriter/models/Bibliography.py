from configparser import ConfigParser
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import User, Story, BibliographyAuthor, Base


class Bibliography(Base):
    """The Bibliography class represents a reference to a story.

    Attributes
    ----------
        id: int
            The Bibliography ID
        user_id: int
            The ID of the user who created this Bibliography entry
        story_id: int
            The Story ID that this Bibliography references
        title: str
            The referenced work's title
        pages: str
            The pertinent pages of the referenced work
        publisher: str
            The referenced work's publisher
        publication_date: str
            The referenced work's publication date in date form: yyy-mm-dd
        editor: str
            The referenced work's editor
        created: str
            The referenced work's creation date in datetime form: yyy-mm-dd hh:mm:ss
        modified: str
            The referenced work's last modification date in datetime form: yyy-mm-dd hh:mm:ss
        user: User
            The user who created this Bibliography entry
        story: Story
            The Story to which this Bibliography entry belongs
        authors: List[BibliographyAuthor]
            The author(s) of the referenced work

    Methods
    -------
        __repr__()
            Returns a string representation of the reference
        __str__()
            Returns a string representation of the reference
        serialize()
            Returns a dictionary representation of the reference
        unserialize(data: dict)
            Updates the reference's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_pages(pages: str)
            Validates the pages' length
        validate_publication_date(publication_date: str)
            Validates the publication date's format
    """

    __tablename__ = 'bibliographies'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'))
    title: Mapped[str] = mapped_column(String(250), nullable=True)
    pages: Mapped[str] = mapped_column(String(50), nullable=True)
    publisher: Mapped[str] = mapped_column(String(100), nullable=True)
    publication_date: Mapped[str] = mapped_column(Date, nullable=True)
    editor: Mapped[str] = mapped_column(String(100), nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship("User")
    story: Mapped["Story"] = relationship("Story", back_populates="references")
    authors: Mapped[Optional[List["BibliographyAuthor"]]] = relationship(
        "BibliographyAuthor", back_populates="reference",
        lazy="joined", cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        """Returns a string representation of the reference.

        Returns
        -------
        str
            A string representation of the reference
        """

        return f'<Bibliography {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the reference.

        Returns
        -------
        str
            A string representation of the reference
        """

        return f'Bibliography: {self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the reference.

        Returns
        -------
        dict
            A dictionary representation of the reference
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'story_id': self.story_id,
            'title': self.title,
            'pages': self.pages,
            'publication_date': str(self.publication_date),
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Bibliography":
        """Updates the reference's attributes with the values from the dictionary.


        Returns
        -------
        Bibliography
            The updated reference
        """

        self.id = data.get('id', self.id)
        self.user_id = data.get('user_id', self.user_id)
        self.story_id = data.get('story_id', self.story_id)
        self.title = data.get('title', self.title)
        self.pages = data.get('pages', self.pages)
        self.publication_date = data.get('publication_date', self.publication_date)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length.

        Returns
        -------
        str
            The validated title
        """

        if not title:
            raise ValueError("Reference title must not be empty.")

        if len(title) > 250:
            raise ValueError("Reference title must not be longer than 250 characters.")

        return title

    @validates("pages")
    def validate_pages(self, key, pages: str) -> str:
        """Validates the pages' length.

        Returns
        -------
        str
            The validated pages
        """

        if pages and len(pages) > 50:
            raise ValueError("Reference pages data must not be longer than 50 characters.")

        return pages

    @validates("publisher")
    def validate_publisher(self, key, publisher: str) -> str:
        """Validates the publisher's length.

        Parameters
        ----------
        publisher: str
            The reference's publisher

        Returns
        -------
        str
            The validated publisher
        """

        if publisher and len(publisher) > 100:
            raise ValueError("Reference publisher data must not be longer than 100 characters.")

        return publisher

    @validates("publication_date")
    def validate_publication_date(self, key, publication_date: str) -> str | None:
        """Validates the publication date's format.

        Returns
        -------
        str
            The validated publication date
        """

        config = ConfigParser()
        config.read("config.cfg")
        date_format = config.get("formats", "date")

        if publication_date is not None and bool(datetime.strptime(publication_date, date_format)) is False:
            raise ValueError("Reference publication date must be in the format 'YYYY-MM-DD'.")

        return publication_date

    @validates("editor")
    def validate_editor(self, key, editor: str) -> str:
        """Validates the editor's length.

        Parameters
        ----------
        editor: str
            The reference's editor

        Returns
        -------
        str
            The validated editor
        """

        if editor and len(editor) > 100:
            raise ValueError("Reference editor data must not be longer than 100 characters.")

        return editor
