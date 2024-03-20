from datetime import datetime
from enum import Enum
from typing import Optional, List

import validators
from validators import url as url_validator
from validators import uuid as uuid_validator
from sqlalchemy import Integer, ForeignKey, String, DateTime, Boolean, Date, Text, Float
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship, validates

Base = declarative_base()
datetime_format = "%Y-%m-%d %H:%M:%S.%f"
date_format = "%Y-%m-%d"


class Activity(Base):
    """The Activity class represents an activity that a user has done.

    Attributes
    ----------
        id: int
            The activity's id
        user_id: int
            The id of the owner of this entry
        summary: str
            The activity's summary
        created: str
            The activity's creation date in datetime form: yyy-mm-dd hh:mm:ss
        user: User
            The user who owns this entry

    Methods
    -------
        __repr__()
            Returns a string representation of the activity
        __str__()
            Returns a string representation of the activity
        serialize()
            Returns a dictionary representation of the activity
        unserialize(data: dict)
            Updates the activity's attributes with the values from the dictionary
        validate_summary(summary: str)
            Validates the summary's length
    """

    __tablename__ = 'activities'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    summary: Mapped[str] = mapped_column(String(250), nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User", back_populates="activities")

    def __repr__(self):
        """Returns a string representation of the activity.

        Returns
        -------
        str
            A string representation of the activity
        """

        return f'<Activity {self.summary[:50]!r}>'

    def __str__(self):
        """Returns a string representation of the activity.

        Returns
        -------
        str
            A string representation of the activity
        """

        return f'Activity: {self.summary[:50]}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the activity.

        Returns
        -------
        dict
            A dictionary representation of the activity
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'summary': self.summary,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "Activity":
        """Updates the activity's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the activity

        Returns
        -------
        Activity
            The updated activity
        """

        self.id = data.get('id', self.id)
        self.user_id = data.get('user_id', self.user_id)
        self.summary = data.get('summary', self.summary)
        self.created = data.get('created', self.created)

        return self

    @validates("summary")
    def validate_summary(self, key, summary: str) -> str:
        """Validates the summary's length."""

        if len(summary) > 250:
            raise ValueError("The activity summary must not have more than 250 characters.")

        return summary


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
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User", back_populates="authors")
    stories: Mapped[Optional[List["AuthorStory"]]] = relationship("AuthorStory", back_populates="author")

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


class AuthorStory(Base):
    """The AuthorStory class represents the relationship between an author and a story.

    Attributes
    ----------
        author_id: int
            The author's id
        story_id: int
            The story's id
        user_id: int
            The id of the owner of this entry
        created: str
            The creation datetime of the link between the Author and the Story
        user: User
            The user who owns this entry
        author: Author
            The author name assigned to the story
        story: Story
            The story that the author (user) wrote

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

    __tablename__ = 'authors_stories'
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('authors.id'), primary_key=True)
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    author: Mapped["Author"] = relationship("Author", back_populates="stories")
    story: Mapped["Story"] = relationship("Story", back_populates="authors")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<AuthorStory {self.author.name!r} - {self.story.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'AuthorStory: {self.author.name} - {self.story.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'author_id': self.author_id,
            'story_id': self.story_id,
            'user_id': self.user_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "AuthorStory":
        """Updates the relationship's attributes with the values from the dictionary.

        Returns
        -------
        AuthorStory
            The updated relationship
        """

        self.author_id = data.get('author_id', self.author_id)
        self.story_id = data.get('story_id', self.story_id)
        self.user_id = data.get('user_id', self.user_id)
        self.created = data.get('created', self.created)

        return self


class Bibliography(Base):
    """The Bibliography class represents a reference to a story.

    Attributes
    ----------
        id: int
            The reference's id
        user_id: int
            The id of the owner of this entry
        story_id: int
            The story's id
        title: str
            The reference's title
        pages: str
            The reference's pages
        publication_date: str
            The reference's publication date in date form: yyy-mm-dd
        created: str
            The reference's creation date in datetime form: yyy-mm-dd hh:mm:ss
        modified: str
            The reference's last modification date in datetime form: yyy-mm-dd hh:mm:ss
        user: User
            The user who owns this entry
        story: Story
            The story that the reference refers to
        authors: List[BibliographyAuthor]
            The authors of the reference

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
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    story: Mapped["Story"] = relationship("Story", back_populates="references")
    authors: Mapped[Optional[List["BibliographyAuthor"]]] = relationship(
        "BibliographyAuthor", back_populates="reference", lazy="joined"
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
            'publication_date': self.publication_date,
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

    __tablename__ = 'bibliographies_authors'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    bibliography_id: Mapped[int] = mapped_column(Integer, ForeignKey('bibliographies.id'))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    initials: Mapped[str] = mapped_column(String(10), nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    reference: Mapped["Bibliography"] = relationship("Bibliography", back_populates="authors")

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


class Chapter(Base):
    """The Chapter class represents a chapter of a story.

    Attributes
    ----------
        id: int
            The chapter's id
        user_id: int
            The id of the owner of this entry
        story_id: int
            The story's id
        position: int
            The chapter's position in the story
        title: str
            The chapter's title
        description: str
            The chapter's description
        created: str
            The chapter's creation date in datetime form: yyy-mm-dd hh:mm:ss
        modified: str
            The chapter's last modification date in datetime form: yyy-mm-dd hh:mm:ss
        user: User
            The user who owns this entry
        story: Story
            The story that the chapter belongs to
        links: List[ChapterLink]
            The links of the chapter
        notes: List[ChapterNote]
            The notes of the chapter

    Methods
    -------
        __repr__()
            Returns a string representation of the chapter
        __str__()
            Returns a string representation of the chapter
        serialize()
            Returns a dictionary representation of the chapter
        unserialize(data: dict)
            Updates the chapter's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_description(description: str)
            Validates the description's length
    """

    __tablename__ = 'chapters'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'))
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    scenes: Mapped[Optional[List["Scene"]]] = relationship("Scene", back_populates="chapter", lazy="joined")
    user: Mapped["User"] = relationship("User")
    story: Mapped["Story"] = relationship("Story", back_populates="chapters")
    links: Mapped[Optional[List["ChapterLink"]]] = relationship("ChapterLink", back_populates="chapter", lazy="joined")
    notes: Mapped[Optional[List["ChapterNote"]]] = relationship("ChapterNote", back_populates="chapter", lazy="joined")

    def __repr__(self):
        """Returns a string representation of the chapter.

        Returns
        -------
        str
            A string representation of the chapter
        """

        return f'<Chapter {self.position}: {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the chapter.

        Returns
        -------
        str
            A string representation of the chapter
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the chapter.

        Returns
        -------
        dict
            A dictionary representation of the chapter
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'story_id': self.story_id,
            'position': self.position,
            'title': self.title,
            'description': self.description,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Chapter":
        """Updates the chapter's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the chapter

        Returns
        -------
        Chapter
            The updated chapter
        """

        self.id = data.get('id', self.id)
        self.user_id = data.get('user_id', self.user_id)
        self.story_id = data.get('story_id', self.story_id)
        self.position = data.get('position', self.position)
        self.title = data.get('title', self.title)
        self.description = data.get('description', self.description)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length.

        Parameters
        ----------
        title: str
            The chapter's title

        Returns
        -------
        str
            The validated title
        """

        if not title:
            raise ValueError("A chapter title is required.")

        if len(title) > 250:
            raise ValueError("The chapter title must have no more than 250 characters.")

        return title

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length.

        Parameters
        ----------
        description: str
            The chapter's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("The chapter description must have no more than 65535 characters.")

        return description


class ChapterLink(Base):
    """The ChapterLink class represents the relationship between a chapter and a link.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        story_id: int
            The story's id
        chapter_id: int
            The chapter's id
        link_id: int
            The link's id
        created: str
            The creation datetime of the link between the Chapter and the Link
        user: User
            The user who owns this entry
        story: Story
            The story that the chapter belongs to
        chapter: Chapter
            The chapter that the link belongs to
        link: Link
            The link that the chapter has

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

    __tablename__ = 'chapters_links'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'))
    chapter_id: Mapped[int] = mapped_column(Integer, ForeignKey('chapters.id'), primary_key=True)
    link_id: Mapped[int] = mapped_column(Integer, ForeignKey('links.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    story: Mapped["Story"] = relationship("Story")
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="links")
    link: Mapped["Link"] = relationship("Link", back_populates="chapters")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<ChapterLink {self.chapter.title!r} - {self.link.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.chapter.title} - {self.link.title}'

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
            'link_id': self.link_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "ChapterLink":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        ChapterLink
            The updated relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.story_id = data.get('story_id', self.story_id)
        self.chapter_id = data.get('chapter_id', self.chapter_id)
        self.link_id = data.get('link_id', self.link_id)
        self.created = data.get('created', self.created)

        return self


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
    chapter_id: Mapped[int] = mapped_column(Integer, ForeignKey('chapters.id'), primary_key=True)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey('notes.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    story: Mapped["Story"] = relationship("Story")
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="notes")
    note: Mapped["Note"] = relationship("Note", back_populates="chapters")

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


class Character(Base):
    """The Character class represents a character in a story.

    Attributes
    ----------
        id: int
            The character's id
        user_id: int
            The id of the owner of this entry
        title: str
            The character's title
        first_name: str
            The character's first name
        middle_name: str
            The character's middle name
        last_name: str
            The character's last name
        nickname: str
            The character
        gender: str
            The gender of the character
        sex: str
            The sex of the character
        date_of_birth: str
            The character's date of birth in date form: yyy-mm-dd
        date_of_death: str
            The character's date of death in date form: yyy-mm-dd
        created: str
            The character's creation date in datetime form: yyy-mm-dd hh:mm:ss
        modified: str
            The character's last modification date in datetime form: yyy-mm-dd hh:mm:ss

    Methods
    -------
        __repr__()
            Returns a string representation of the character
        __str__()
            Returns a string representation of the character
        serialize()
            Returns a dictionary representation of the character
        unserialize(data: dict)
            Updates the character's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_first_name(first_name: str):
            Validates the first name's length
        validate_middle_name(middle_name: str)
            Validates the middle name's length
        validate_last_name(last_name: str)
            Validates the last name's length
        validate_nickname(nickname: str)
            Validates the nickname's length
        validate_gender(gender: str)
            Validates the gender's length
        validate_sex(sex: str)
            Validates the sex's length
        validate_date_of_birth(date_of_birth: str)
            Validates the date of birth's format
        validate_date_of_death(date_of_death: str)
            Validates the date of death's format
    """

    __tablename__ = 'characters'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    nickname: Mapped[str] = mapped_column(String(100), nullable=True)
    gender: Mapped[str] = mapped_column(String(50), nullable=True)
    sex: Mapped[str] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[str] = mapped_column(Date, nullable=True)
    date_of_death: Mapped[str] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User", back_populates="characters")
    character_relationships: Mapped[Optional[List["CharacterRelationship"]]] = relationship(
        "CharacterRelationship", back_populates="related_character", foreign_keys="[CharacterRelationship.related_id]",
        lazy="joined"
    )
    traits: Mapped[Optional[List["CharacterTrait"]]] = relationship(
        "CharacterTrait", back_populates="character", lazy="joined"
    )
    events: Mapped[Optional[List["CharacterEvent"]]] = relationship(
        "CharacterEvent", back_populates="character"
    )
    images: Mapped[Optional[List["CharacterImage"]]] = relationship(
        "CharacterImage", back_populates="character", lazy="joined"
    )
    links: Mapped[Optional[List["CharacterLink"]]] = relationship(
        "CharacterLink", back_populates="character", lazy="joined"
    )
    notes: Mapped[Optional[List["CharacterNote"]]] = relationship(
        "CharacterNote", back_populates="character", lazy="joined"
    )
    stories: Mapped[Optional[List["CharacterStory"]]] = relationship(
        "CharacterStory", back_populates="character", lazy="joined"
    )

    def __repr__(self):
        """Returns a string representation of the character.

        Returns
        -------
        str
            A string representation of the character
        """

        return f'<Character {self.title!r} {self.first_name!r} {self.last_name!r}>'

    def __str__(self):
        """Returns a string representation of the character.

        Returns
        -------
        str
            A string representation of the character
        """

        title = f'{self.title}' if self.title else ""
        first_name = f' {self.first_name}' if self.first_name else ""
        middle_name = f' {self.middle_name}' if self.middle_name else ""
        last_name = f' {self.last_name}' if self.last_name else ""
        nickname = f' ({self.nickname})' if self.nickname else ""

        return f'{title}{first_name}{middle_name}{last_name}{nickname}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the character.

        Returns
        -------
        dict
            A dictionary representation of the character
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'nickname': self.nickname,
            'gender': self.gender,
            'sex': self.sex,
            'date_of_birth': str(self.date_of_birth),
            'date_of_death': str(self.date_of_death),
            'description' : self.description,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Character":
        """Updates the character's attributes with the values from the dictionary.

        Returns
        -------
        Character
            The updated character
        """

        self.id = data.get('id', self.id)
        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
        self.first_name = data.get('first_name', self.first_name)
        self.middle_name = data.get('middle_name', self.middle_name)
        self.last_name = data.get('last_name', self.last_name)
        self.nickname = data.get('nickname', self.nickname)
        self.gender = data.get('gender', self.gender)
        self.sex = data.get('sex', self.sex)
        self.date_of_birth = data.get('date_of_birth', self.date_of_birth)
        self.date_of_death = data.get('date_of_death', self.date_of_death)
        self.description = data.get('description', self.description)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length.

        Parameters
        ----------
        title: str
            The character's title

        Returns
        -------
        str
            The validated title
        """

        if title and len(title) > 100:
            raise ValueError("The character title must have no more than 100 characters.")

        return title

    @validates("first_name")
    def validate_first_name(self, key, first_name: str) -> str:
        """Validates the first name's length.

        Parameters
        ----------
        first_name: str
            The character's first name

        Returns
        -------
        str
            The validated first name
        """

        if first_name and len(first_name) > 100:
            raise ValueError("The character first name must have no more than 100 characters.")

        return first_name

    @validates("middle_name")
    def validate_middle_name(self, key, middle_name: str) -> str:
        """Validates the middle name's length.

        Parameters
        ----------
        middle_name: str
            The character's middle name

        Returns
        -------
        str
            The validated middle name
        """

        if middle_name and len(middle_name) > 100:
            raise ValueError("The character middle name must have no more than 100 characters.")

        return middle_name

    @validates("last_name")
    def validate_last_name(self, key, last_name: str) -> str:
        """Validates the last name's length.

        Parameters
        ----------
        last_name: str
            The character's last name

        Returns
        -------
        str
            The validated last name
        """

        if last_name and len(last_name) > 100:
            raise ValueError("The character last name must have no more than 100 characters.")

        return last_name

    @validates("nickname")
    def validate_nickname(self, key, nickname: str) -> str:
        """Validates the nickname's length.

        Parameters
        ----------
        nickname: str
            The character's nickname

        Returns
        -------
        str
            The validated nickname
        """

        if nickname and len(nickname) > 100:
            raise ValueError("The character nickname must have no more than 100 characters.")

        return nickname

    @validates("gender")
    def validate_gender(self, key, gender: str) -> str:
        """Validates the gender's length.

        Parameters
        ----------
        gender: str
            The character's gender

        Returns
        -------
        str
            The validated gender
        """

        if gender and len(gender) > 50:
            raise ValueError("The gender value must have no more than 50 characters.")

        return gender

    @validates("sex")
    def validate_sex(self, key, sex: str) -> str:
        """Validates the sex's length.

        Parameters
        ----------
        sex: str
            The character's sex

        Returns
        -------
        str
            The validated sex
        """

        if sex and len(sex) > 50:
            raise ValueError("The value of sex must have no more than 50 characters.")

        return sex

    @validates("date_of_birth")
    def validate_date_of_birth(self, key, date_of_birth: str) -> datetime | None:
        """Validates the date of birth's format.

        Parameters
        ----------
        date_of_birth: str
            The character's date of birth in date form: yyy-mm-dd

        Returns
        -------
        str
            The validated date of birth
        """

        if date_of_birth and bool(datetime.strptime(date_of_birth, date_format)) is False:
            raise ValueError("The date of birth must be in the format 'YYYY-MM-DD'.")

        if date_of_birth:
            return datetime.strptime(date_of_birth, date_format)

        else:
            return None

    @validates("date_of_death")
    def validate_date_of_death(self, key, date_of_death: str) -> datetime | None:
        """Validates the date of death's format.

        Parameters
        ----------
        date_of_death: str
            The character's date of death in date form: yyy-mm-dd

        Returns
        -------
        str
            The validated date of death
        """

        if date_of_death and bool(datetime.strptime(date_of_death, date_format)) is False:
            raise ValueError("The date of death must be in the format 'YYYY-MM-DD'.")

        if date_of_death:
            return datetime.strptime(date_of_death, date_format)

        else:
            return None

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length.

        Parameters
        ----------
        description: str
            The character's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("The character description must have no more than 65535 characters.")

        return description


class CharacterEvent(Base):
    """The CharacterEvent class represents the relationship between a character and an event.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        event_id: int
            The event's id
        created: str
            The creation datetime of the link between the Character and the Event
        user: User
            The user who owns this entry
        character: Character
            The character that the event belongs to
        event: Event
            The event that the character has

    Methods
    -------
        __repr__()
            Returns a string representation of the relationship
        __str__()
            Returns a string representation of the relationship
        serialize():
            Returns a dictionary representation of the relationship
        unserialize(data: dict)
            Updates the relationship's attributes with the values from the dictionary
    """

    __tablename__ = 'characters_events'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'), primary_key=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship("Character", back_populates="events")
    event: Mapped["Event"] = relationship("Event", back_populates="characters")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<CharacterEvent {self.character.first_name!r} {self.character.last_name!r} - {self.event.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.character.first_name} {self.character.last_name} - {self.event.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'character_id': self.character_id,
            'event_id': self.event_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "CharacterEvent":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        CharacterEvent
            The updated relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.event_id = data.get('event_id', self.event_id)
        self.created = data.get('created', self.created)

        return self


class CharacterImage(Base):
    """The CharacterImage class represents the relationship between a character and an image.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        image_id: int
            The image's id
        position: int
            The position of the image in the character's gallery
        is_default: bool
            Whether the image is the default image for the character
        created: str
            The creation datetime of the link between the Character and the Image
        modified: str
            The last modification datetime of the link between the Character and the Image
        user: User
            The user who owns this entry
        character: Character
            The character that the image belongs to
        image: Image
            The image that the character has

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
    __tablename__ = 'characters_images'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'), primary_key=True)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey('images.id'), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship("Character", back_populates="images")
    image: Mapped["Image"] = relationship("Image", back_populates="character")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<CharacterImage {self.character.first_name!r} {self.character.last_name!r} - {self.image.caption!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.character.first_name} {self.character.last_name} - {self.image.caption}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'character_id': self.character_id,
            'image_id': self.image_id,
            'position': self.position,
            'is_default': self.is_default,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "CharacterImage":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        CharacterImage
            The updated relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.image_id = data.get('image_id', self.image_id)
        self.position = data.get('position', self.position)
        self.is_default = data.get('is_default', self.is_default)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self


class CharacterLink(Base):
    """The CharacterLink class represents the relationship between a character and a link.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        link_id: int
            The link's id
        created: str
            The creation datetime of the link between the Character and the Link
        user: User
            The user who owns this entry
        character: Character
            The character that the link belongs to
        link: Link
            The link that the character has

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

    __tablename__ = 'characters_links'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'), primary_key=True)
    link_id: Mapped[int] = mapped_column(Integer, ForeignKey('links.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship("Character", back_populates="links")
    link: Mapped["Link"] = relationship("Link", back_populates="characters")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<CharacterLink {self.character.first_name!r} {self.character.last_name!r} - {self.link.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.character.first_name} {self.character.last_name} - {self.link.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'character_id': self.character_id,
            'link_id': self.link_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "CharacterLink":
        """Updates the relationship's attributes with the values from the dictionary.

        Returns
        -------
        CharacterLink
            The updated relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.link_id = data.get('link_id', self.link_id)
        self.created = data.get('created', self.created)

        return self


class CharacterNote(Base):
    """The CharacterNote class represents the relationship between a character and a note.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        note_id: int
            The note's id
        created: str
            The creation datetime of the link between the Character and the Note
        user: User
            The user who owns this entry
        character: Character
            The character that the note belongs to
        note: Note
            The note that the character has

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

    __tablename__ = 'characters_notes'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'), primary_key=True)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey('notes.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship("Character", back_populates="notes")
    note: Mapped["Note"] = relationship("Note", back_populates="characters")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<CharacterNote {self.character.first_name!r} {self.character.last_name!r} - {self.note.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.character.first_name} {self.character.last_name} - {self.note.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'character_id': self.character_id,
            'note_id': self.note_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "CharacterNote":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        CharacterNote
            The updated relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.note_id = data.get('note_id', self.note_id)
        self.created = data.get('created', self.created)

        return self


class CharacterRelationshipTypes(Enum):
    """The CharacterRelationshipTypes class represents the types of relationships between characters.

    Attributes
    ----------
        FAMILY: str
            The relationship is familial
        PERSONAL: str
            The relationship is personal
        ROMANTIC: str
            The relationship is romantic
        PROFESSIONAL: str
            The relationship is professional
        OTHER: str
            The relationship is other
    """

    FAMILY = 'Family'
    PERSONAL = 'Personal'
    ROMANTIC = 'Romantic'
    PROFESSIONAL = 'Professional'
    OTHER = 'Other'


class CharacterRelationship(Base):
    """The CharacterRelationship class represents the relationship between two characters.

    Attributes
    ----------
        id: int
            The character relationship's id
        user_id: int
            The id of the owner of this entry
        parent_id: int
            The parent character's id
        position: int
            The position of the related character in the parent character's life
        related_id: int
            The related character's id
        relationship_type: str
            The type of relationship between the characters
        description: str
            A description of the relationship
        start_date: str
            The starting date of the relationship
        end_date: str
            The ending date of the relationship
        created: str
            The creation datetime of the relationship
        modified: str
            The last modification datetime of the relationship
        user: User
            The user who owns this entry
        parent_character: Character
            The parent character in the relationship
        related_character: Character
            The related character in the relationship

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
        validate_relationship_type(relationship_type: str)
            Validates the relationship type
        validate_description(description: str)
            Validates the description
        validate_start_date(start_date: str)
            Validates the start date
        validate_end_date(end_date: str)
            Validates the end date
    """

    __tablename__ = 'character_relationships'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'))
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    related_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'), )
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    start_date: Mapped[str] = mapped_column(Date, nullable=True)
    end_date: Mapped[str] = mapped_column(Date, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    parent_character: Mapped["Character"] = relationship("Character", foreign_keys="CharacterRelationship.parent_id", lazy="joined")
    related_character: Mapped["Character"] = relationship(
        "Character", back_populates="character_relationships", lazy="joined",
        foreign_keys="[CharacterRelationship.related_id]"
    )

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return (f'<CharacterRelationship {self.parent_character.first_name!r} {self.parent_character.last_name!r} - '
                f'{self.description!r} - {self.related_character.first_name!r} {self.related_character.last_name!r}>')

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return (f'{self.parent_character.first_name} {self.parent_character.last_name} - '
                f'{self.description!r} - {self.related_character.first_name} {self.related_character.last_name}')

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'position': self.position,
            'related_id': self.related_id,
            'relationship_type': self.relationship_type,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "CharacterRelationship":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        CharacterRelationship
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.parent_id = data.get('parent_id', self.parent_id)
        self.position = data.get('position', self.position)
        self.related_id = data.get('related_id', self.related_id)
        self.relationship_type = data.get('relationship_type', self.relationship_type)
        self.description = data.get('description', self.description)
        self.start_date = data.get('start_date', self.start_date)
        self.end_date = data.get('end_date', self.end_date)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("relationship_type")
    def validate_relationship_type(self, key, relationship_type: str) -> str:
        """Validates the relationship type.

        Parameters
        ----------
        relationship_type: str
            The character relationship type

        Returns
        -------
        str
            The validated relationship type
        """

        if not relationship_type:
            raise ValueError("A character relationship type is required.")

        rtypes = [str(rt.value) for rt in CharacterRelationshipTypes]

        if relationship_type not in rtypes:
            raise ValueError("The character relationship type is invalid.")

        return relationship_type

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description.

        Parameters
        ----------
        description: str
            The character relationship description

        Returns
        -------
        str
            The validated description
        """

        if not description:
            raise ValueError("A character relationship description is required.")

        if len(description) > 250:
            raise ValueError("The character relationship description must have no more than 250 characters.")

        return description


class CharacterStory(Base):
    """The CharacterStory class represents the relationship between a character and a story.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        story_id: int
            The story's id
        created: str
            The creation datetime of the link between the Character and the Story
        user: User
            The user who owns this entry
        character: Character
            The character that the story belongs to
        story: Story
            The story that the character has

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

    __tablename__ = 'characters_stories'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'), primary_key=True)
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship("Character", back_populates="stories", lazy="joined")
    story: Mapped["Story"] = relationship("Story", back_populates="characters", lazy="joined")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<CharacterStory {self.character.__str__()!r} - {self.story.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.character.__str__()} - {self.story.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'character_id': self.character_id,
            'story_id': self.story_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "CharacterStory":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        CharacterStory
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.story_id = data.get('story_id', self.story_id)
        self.created = data.get('created', self.created)

        return self


class CharacterTrait(Base):
    """The CharacterTrait class represents a trait of a character.

    Attributes
    ----------
        id: int
            The trait's id
        user_id: int
            The id of the owner of this entry
        character_id: int
            The character's id
        position: int
            The position of the trait in the character's traits
        name: str
            The name of the trait
        magnitude: int
            The magnitude of the trait expressed as an integer between 0 and 100
        created: str
            The trait's creation date in datetime form: yyy-mm-dd hh:mm:ss
        modified: str
            The trait's last modification date in datetime form: yyy-mm-dd hh:mm:ss

    Methods
    -------
        __repr__()
            Returns a string representation of the trait
        __str__()
            Returns a string representation of the trait
        serialize()
            Returns a dictionary representation of the trait
        unserialize(data: dict)
            Updates the trait's attributes with the values from the dictionary
        validate_name(name: str)
            Validates the name's length
        validate_magnitude(magnitude: int)
            Validates the magnitude's value
    """

    __tablename__ = 'characters_traits'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'))
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    magnitude: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    character: Mapped["Character"] = relationship("Character", back_populates="traits", lazy="joined")

    def __repr__(self):
        """Returns a string representation of the trait.

        Returns
        -------
        str
            A string representation of the trait
        """

        return f'{self.character.first_name!r} {self.character.last_name!r} - {self.name!r}'

    def __str__(self):
        """Returns a string representation of the trait.

        Returns
        -------
        str
            A string representation of the trait
        """

        return f'{self.character.first_name} {self.character.last_name} - {self.name}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the trait.

        Returns
        -------
        dict
            A dictionary representation of the trait
        """

        return {
            'user_id': self.user_id,
            'character_id': self.character_id,
            'position': self.position,
            'name': self.name,
            'magnitude': self.magnitude,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "CharacterTrait":
        """Updates the trait's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the trait

        Returns
        -------
        CharacterTrait
            The unserialized trait
        """

        self.user_id = data.get('user_id', self.user_id)
        self.character_id = data.get('character_id', self.character_id)
        self.position = data.get('position', self.position)
        self.name = data.get('name', self.name)
        self.magnitude = data.get('magnitude', self.magnitude)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("name")
    def validate_name(self, key, name: str) -> str:
        """Validates the name's length.

        Parameters
        ----------
        name: str
            The trait's name

        Returns
        -------
        str
            The validated name
        """

        if not name:
            raise ValueError("The trait name cannot be empty.")

        return name

    @validates("magnitude")
    def validate_magnitude(self, key, magnitude: int) -> int:
        """Validates the magnitude's value.

        Parameters
        ----------
        magnitude: int
            The trait's magnitude

        Returns
        -------
        str
            The validated magnitude
        """

        if magnitude < 0:
            raise ValueError("The trait magnitude cannot be negative.")

        if magnitude > 100:
            raise ValueError("The trait magnitude cannot be greater than 100.")

        return magnitude


class Event(Base):
    """The Event class represents an event in a story.

    Attributes
    ----------
        id: int
            The event's id
        user_id: int
            The id of the owner of this entry
        title: str
            The event's title
        description: str
            A description of the event
        start_datetime: str
            The starting datetime of the event
        end_datetime: str
            The ending datetime of the event
        created: str
            The creation datetime of the event
        modified: str
            The last modification datetime of the event
        user: User
            The user who owns this entry
        links: List[EventLink]
            The links that the event has
        characters: List[CharacterEvent]
            The characters that the event has
        notes: List[EventNote]
            The notes that the event has

    Methods
    -------
        __repr__()
            Returns a string representation of the event
        __str__()
            Returns a string representation of the event
        serialize()
            Returns a dictionary representation of the event
        unserialize(data: dict)
            Updates the event's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_description(description: str)
            Validates the description's length
        validate_start_datetime(start_datetime: str)
            Validates the start datetime's format
        validate_end_datetime(end_datetime: str)
            Validates the end datetime's format
    """

    __tablename__ = 'events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    start_datetime: Mapped[str] = mapped_column(DateTime, nullable=True)
    end_datetime: Mapped[str] = mapped_column(DateTime, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User", back_populates="events")
    links: Mapped[Optional[List["EventLink"]]] = relationship("EventLink", back_populates="event", lazy="joined")
    characters: Mapped[Optional[List["CharacterEvent"]]] = relationship("CharacterEvent", back_populates="event", lazy="joined")
    notes: Mapped[Optional[List["EventNote"]]] = relationship("EventNote", back_populates="event", lazy="joined")
    locations: Mapped[Optional[List["EventLocation"]]] = relationship("EventLocation", back_populates="event", lazy="joined")

    def __repr__(self):
        """Returns a string representation of the event.

        Returns
        -------
        str
            A string representation of the event
        """

        return f'<Event {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the event.

        Returns
        -------
        str
            A string representation of the event
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the event.

        Returns
        -------
        dict
            A dictionary representation of the event
        """

        return {
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Event":
        """Updates the event's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the event

        Returns
        -------
        Event
            The unserialized event
        """

        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
        self.description = data.get('description', self.description)
        self.start_datetime = data.get('start_datetime', self.start_datetime)
        self.end_datetime = data.get('end_datetime', self.end_datetime)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length.

        Parameters
        ----------
        title: str
            The event's title

        Returns
        -------
        str
            The validated title
        """

        if not title:
            raise ValueError("Title cannot be empty")

        return title

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length.

        Parameters
        ----------
        description: str
            The event's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("Description cannot have more than 65,535 characters.")

        return description


class EventLink(Base):
    """The EventLink class represents the relationship between an event and a link.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        event_id: int
            The event's id
        link_id: int
            The link's id
        created: str
            The creation datetime of the link between the Event and the Link
        user: User
            The user who owns this entry
        event: Event
            The event that the link belongs to
        link: Link
            The link that the event has

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

    __tablename__ = 'events_links'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events.id'), primary_key=True)
    link_id: Mapped[int] = mapped_column(Integer, ForeignKey('links.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    event: Mapped["Event"] = relationship("Event", back_populates="links")
    link: Mapped["Link"] = relationship("Link", back_populates="events")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<EventLink {self.event.title!r} - {self.link.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.event.title} - {self.link.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'event_id': self.event_id,
            'link_id': self.link_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "EventLink":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        EventLink
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.event_id = data.get('event_id', self.event_id)
        self.link_id = data.get('link_id', self.link_id)
        self.created = data.get('created', self.created)

        return self


class EventLocation(Base):
    """The EventLocation class represents the relationship between an event and a location.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        event_id: int
            The event's id
        location_id: int
            The location's id
        created: str
            The creation datetime of the link between the Event and the Location
        user: User
            The user who owns this entry
        event: Event
            The event that the location belongs to
        location: Location
            The location that the event has

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

    __tablename__ = 'events_locations'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events.id'), primary_key=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey('locations.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    event: Mapped["Event"] = relationship("Event", back_populates="locations")
    location: Mapped["Location"] = relationship("Location", back_populates="events")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<EventLocation {self.event.title!r} - {self.location.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.event.title} - {self.location.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'event_id': self.event_id,
            'location_id': self.location_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "EventLocation":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        EventLocation
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.event_id = data.get('event_id', self.event_id)
        self.location_id = data.get('location_id', self.location_id)
        self.created = data.get('created', self.created)

        return self


class EventNote(Base):
    """The EventNote class represents the relationship between an event and a note.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        event_id: int
            The event's id
        note_id: int
            The note's id
        created: str
            The creation datetime of the link between the Event and the Note
        user: User
            The user who owns this entry
        event: Event
            The event that the note belongs to
        note: Note
            The note that the event has

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

    __tablename__ = 'events_notes'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events.id'), primary_key=True)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey('notes.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    event: Mapped["Event"] = relationship("Event", back_populates="notes")
    note: Mapped["Note"] = relationship("Note", back_populates="events")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<EventNote {self.event.title!r} - {self.note.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.event.title} - {self.note.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'event_id': self.event_id,
            'note_id': self.note_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "EventNote":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        EventNote
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.event_id = data.get('event_id', self.event_id)
        self.note_id = data.get('note_id', self.note_id)
        self.created = data.get('created', self.created)

        return self


class ImageMimeTypes(Enum):
    """The ImageMimeTypes class represents the types of image mime types.

    Attributes
    ----------
        JPEG: str
            The image is in JPEG format
        PNG: str
            The image is in PNG format
        GIF: str
            The image is in GIF format
    """
    JPEG = 'image/jpeg'
    PNG = 'image/png'
    GIF = 'image/gif'


class Image(Base):
    """The Image class represents an image in the system.

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
    size_in_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mime_type: Mapped[ImageMimeTypes] = mapped_column(String(50), nullable=False)
    caption: Mapped[str] = mapped_column(String(250), nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User", back_populates="images")
    character: Mapped[Optional[List["CharacterImage"]]] = relationship("CharacterImage", back_populates="image")
    location: Mapped[Optional[List["ImageLocation"]]] = relationship("ImageLocation", back_populates="image")

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


class Link(Base):
    """The Link class represents a link in the system.

    Attributes
    ----------
        id: int
            The link's id
        user_id: int
            The id of the owner of this entry
        title: str
            The link's title
        url: str
            The link's URL
        created: str
            The creation datetime of the link
        modified: str
            The last modification datetime of the link
        user: User
            The user who owns this entry
        stories: List[LinkStory]
            The stories that the link has
        chapters: List[ChapterLink]
            The chapters that the link has
        scenes: List[LinkScene]
            The scenes that the link has
        characters: List[CharacterLink]
            The characters that the link has
        events: List[EventLink]
            The events that the link has
        locations: List[LinkLocation]
            The locations that the link has

    Methods
    -------
        __repr__()
            Returns a string representation of the link
        __str__()
            Returns a string representation of the link
        serialize()
            Returns a dictionary representation of the link
        unserialize(data: dict)
            Updates the link's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_url(url: str)
            Validates the URL's length and format
    """

    __tablename__ = 'links'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    url: Mapped[str] = mapped_column(String(200), nullable=False)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User", back_populates="links")
    stories: Mapped[Optional[List["LinkStory"]]] = relationship("LinkStory", back_populates="link")
    chapters: Mapped[Optional[List["ChapterLink"]]] = relationship("ChapterLink", back_populates="link")
    scenes: Mapped[Optional[List["LinkScene"]]] = relationship(
        "LinkScene", back_populates="link",
        cascade="all, delete, delete-orphan")
    characters: Mapped[Optional[List["CharacterLink"]]] = relationship("CharacterLink", back_populates="link")
    events: Mapped[Optional[List["EventLink"]]] = relationship("EventLink", back_populates="link")
    locations: Mapped[Optional[List["LinkLocation"]]] = relationship("LinkLocation", back_populates="link")

    def __repr__(self):
        """Returns a string representation of the link.

        Returns
        -------
        str
            A string representation of the link
        """

        return f'<Link {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the link.

        Returns
        -------
        str
            A string representation of the link
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the link.

        Returns
        -------
        dict
            A dictionary representation of the link
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'url': self.url,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Link":
        """Updates the link's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the link

        Returns
        -------
        Link
            The unserialized link
        """

        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
        self.url = data.get('url', self.url)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length.

        Parameters
        ----------
        title: str
            The link's title

        Returns
        -------
        str
            The validated title
        """

        if not title:
            raise ValueError("A link title is required.")

        if len(title) > 250:
            raise ValueError("The link title can have no more than 250 characters.")

        return title

    @validates("url")
    def validate_url(self, key, url: str) -> str:
        """Validates the URL's length and format.

        Parameters
        ----------
        url: str
            The link's URL

        Returns
        -------
        str
            The validated URL
        """

        if not url:
            raise ValueError("A link URL is required.")

        if len(url) > 200:
            raise ValueError("The link URL can have no more than 200 characters.")

        if not url_validator(url):
            raise ValueError("The link URL is not valid.")

        return url


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
    link: Mapped["Link"] = relationship("Link", back_populates="scenes")
    scene: Mapped["Scene"] = relationship("Scene", back_populates="links")

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


class LinkStory(Base):
    """The LinkStory class represents the relationship between a link and a story.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        link_id: int
            The link's id
        story_id: int
            The story's id
        created: str
            The creation datetime of the link between the Link and the Story
        user: User
            The user who owns this entry
        link: Link
            The link that the story belongs to
        story: Story
            The story that the link has

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

    __tablename__ = 'links_stories'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    link_id: Mapped[int] = mapped_column(Integer, ForeignKey('links.id'), primary_key=True)
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    link: Mapped["Link"] = relationship("Link", back_populates="stories")
    story: Mapped["Story"] = relationship("Story", back_populates="links")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<LinkStory {self.link.title!r} - {self.story.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.link.title} - {self.story.title}'

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
            'story_id': self.story_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "LinkStory":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship

        Returns
        -------
        LinkStory
            The unserialized relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.link_id = data.get('link_id', self.link_id)
        self.story_id = data.get('story_id', self.story_id)
        self.created = data.get('created', self.created)

        return self


class Location(Base):
    """The Location class represents a location in the system.

    Attributes
    ----------
        id: int
            The location's id
        user_id: int
            The id of the owner of this entry
        title: str
            The location's title
        description: str
            The location's description
        address: str
            The location's address
        city: str
            The location's city
        state: str
            The location's state
        country: str
            The location's country
        zip_code: str
            The location's zip code
        latitude: float
            The location's latitude
        longitude: float
            The location's longitude
        created: str
            The creation datetime of the location
        modified: str
            The last modification datetime of the location
        user: User
            The user who owns this entry
        images: List[ImageLocation]
            The images that the location has
        links: List[LinkLocation]
            The links that the location has
        notes: List[LocationNote]
            The notes that the location has

    Methods
    -------
        __repr__()
            Returns a string representation of the location
        __str__()
            Returns a string representation of the location
        serialize()
            Returns a dictionary representation of the location
        unserialize(data: dict)
            Updates the location's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_description(description: str)
            Validates the description's length
        validate_address(address: str)
            Validates the address's length
        validate_city(city: str)
            Validates the city's length
        validate_state(state: str)
            Validates the state's length
        validate_country(country: str)
            Validates the country's length
        validate_zip_code(zip_code: str)
            Validates the zip code's length
        validate_latitude(latitude: float)
            Validates the latitude's range
        validate_longitude(longitude: float)
            Validates the longitude's range
    """

    __tablename__ = 'locations'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(250), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(250), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    zip_code: Mapped[str] = mapped_column(String(20), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User", back_populates="locations")
    images: Mapped[Optional[List["ImageLocation"]]] = relationship("ImageLocation", back_populates="location")
    links: Mapped[Optional[List["LinkLocation"]]] = relationship("LinkLocation", back_populates="location",
                                                                 lazy="joined")
    events: Mapped[Optional[List["EventLocation"]]] = relationship("EventLocation", back_populates="location",
                                                                   lazy="joined")
    notes: Mapped[Optional[List["LocationNote"]]] = relationship("LocationNote", back_populates="location",
                                                                 lazy="joined")

    def __repr__(self):
        """Returns a string representation of the location.

        Returns
        -------
        str
            A string representation of the location
        """

        return f'<Location {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the location.

        Returns
        -------
        str
            A string representation of the location
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the location.

        Returns
        -------
        dict
            A dictionary representation of the location
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Location":
        """Updates the location's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the location

        Returns
        -------
        Location
            The unserialized location
        """

        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
        self.description = data.get('description', self.description)
        self.address = data.get('address', self.address)
        self.city = data.get('city', self.city)
        self.state = data.get('state', self.state)
        self.country = data.get('country', self.country)
        self.zip_code = data.get('zip_code', self.zip_code)
        self.latitude = data.get('latitude', self.latitude)
        self.longitude = data.get('longitude', self.longitude)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length

        Parameters
        ----------
        title: str
            The location's title

        Returns
        -------
        str
            The validated title
        """

        if title and len(title) > 250:
            raise ValueError("The location title can have no more than 250 characters.")

        return title

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length

        Parameters
        ----------
        description: str
            The location's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("The location description can have no more than 65,535 characters.")

        return description

    @validates("address")
    def validate_address(self, key, address: str) -> str:
        """Validates the address's length

        Parameters
        ----------
        address: str
            The location's address

        Returns
        -------
        str
            The validated address
        """

        if address and len(address) > 250:
            raise ValueError("The location address can have no more than 250 characters.")

        return address

    @validates("city")
    def validate_city(self, key, city: str) -> str:
        """Validates the city's length

        Parameters
        ----------
        city: str
            The location's city

        Returns
        -------
        str
            The validated city
        """

        if city and len(city) > 100:
            raise ValueError("The location city can have no more than 100 characters.")

        return city

    @validates("state")
    def validate_state(self, key, state: str) -> str:
        """Validates the state's length

        Parameters
        ----------
        state: str
            The location's state

        Returns
        -------
        str
            The validated state
        """

        if state and len(state) > 100:
            raise ValueError("The location state can have no more than 100 characters.")

        return state

    @validates("country")
    def validate_country(self, key, country: str) -> str:
        """Validates the country's length

        Parameters
        ----------
        country: str
            The location's country

        Returns
        -------
        str
            The validated country
        """

        if country and len(country) > 100:
            raise ValueError("The location country can have no more than 100 characters.")

        return country

    @validates("zip_code")
    def validate_zip_code(self, key, zip_code: str) -> str:
        """Validates the zip code's length

        Parameters
        ----------
        zip_code: str
            The location's zip code

        Returns
        -------
        str
            The validated zip code
        """

        if zip_code and len(zip_code) > 20:
            raise ValueError("The location zip code can have no more than 20 characters.")

        return zip_code

    @validates("latitude")
    def validate_latitude(self, key, latitude: float) -> float:
        """Validates the latitude's range

        Parameters
        ----------
        latitude: float
            The location's latitude

        Returns
        -------
        float
            The validated latitude
        """

        if type(latitude) is float:
            if latitude < -90.0 or latitude > 90.0:
                raise ValueError("The location latitude must be between -90 and 90.")

        return latitude

    @validates("longitude")
    def validate_longitude(self, key, longitude: float) -> float:
        """Validates the longitude's range

        Parameters
        ----------
        longitude: float
            The location's longitude

        Returns
        -------
        float
            The validated longitude
        """

        if type(longitude) is float:
            if longitude < -180.0 or longitude > 180.0:
                raise ValueError("The location longitude must be between -180 and 180.")

        return longitude


class LocationNote(Base):
    """The LocationNote class represents the relationship between a location and a note.

    Attributes
    ----------
        user_id: int
            The id of the owner of this entry
        location_id: int
            The location's id
        note_id: int
            The note's id
        created: str
            The creation datetime of the link between the Location and the Note
        user: User
            The user who owns this entry
        location: Location
            The location that the note belongs to
        note: Note
            The note that the location has

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

    __tablename__ = 'locations_notes'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey('locations.id'), primary_key=True)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey('notes.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    location: Mapped["Location"] = relationship("Location", back_populates="notes")
    note: Mapped["Note"] = relationship("Note", back_populates="locations")

    def __repr__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'<LocationNote {self.location.title!r} - {self.note.title!r}>'

    def __str__(self):
        """Returns a string representation of the relationship.

        Returns
        -------
        str
            A string representation of the relationship
        """

        return f'{self.location.title} - {self.note.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the relationship.

        Returns
        -------
        dict
            A dictionary representation of the relationship
        """

        return {
            'user_id': self.user_id,
            'location_id': self.location_id,
            'note_id': self.note_id,
            'created': str(self.created),
        }

    def unserialize(self, data: dict) -> "LocationNote":
        """Updates the relationship's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the relationship
        """

        self.user_id = data.get('user_id', self.user_id)
        self.location_id = data.get('location_id', self.location_id)
        self.note_id = data.get('note_id', self.note_id)
        self.created = data.get('created', self.created)

        return self


class Note(Base):
    """The Note class represents a note in the system.

    Attributes
    ----------
        id: int
            The note's id
        user_id: int
            The id of the owner of this entry
        title: str
            The note's title
        content: str
            The note's content
        created: str
            The creation datetime of the note
        modified: str
            The last modification datetime of the note
        user: User
            The user who owns this entry
        stories: List[NoteStory]
            The stories that the note has
        chapters: List[ChapterNote]
            The chapters that the note has
        scenes: List[NoteScene]
            The scenes that the note has
        characters: List[CharacterNote]
            The characters that the note has
        events: List[EventNote]
            The events that the note has
        locations: List[LocationNote]
            The locations that the note has

    Methods
    -------
        __repr__()
            Returns a string representation of the note
        __str__()
            Returns a string representation of the note
        serialize()
            Returns a dictionary representation of the note
        unserialize(data: dict)
            Updates the note's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_content(content: str)
            Validates the content's length
    """

    __tablename__ = 'notes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User", back_populates="notes")
    stories: Mapped[Optional[List["NoteStory"]]] = relationship("NoteStory", back_populates="note")
    chapters: Mapped[Optional[List["ChapterNote"]]] = relationship("ChapterNote", back_populates="note")
    scenes: Mapped[Optional[List["NoteScene"]]] = relationship(
        "NoteScene", back_populates="note",
        cascade="all, delete, delete-orphan")
    characters: Mapped[Optional[List["CharacterNote"]]] = relationship("CharacterNote", back_populates="note")
    events: Mapped[Optional[List["EventNote"]]] = relationship("EventNote", back_populates="note")
    locations: Mapped[Optional[List["LocationNote"]]] = relationship("LocationNote", back_populates="note")

    def __repr__(self):
        """Returns a string representation of the note.

        Returns
        -------
        str
            A string representation of the note
        """

        return f'<Note {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the note.

        Returns
        -------
        str
            A string representation of the note
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the note.

        Returns
        -------
        dict
            A dictionary representation of the note
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Note":
        """Updates the note's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the note

        Returns
        -------
        Note
            The unserialized note
        """

        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
        self.content = data.get('content', self.content)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length

        Parameters
        ----------
        title: str
            The note's title

        Returns
        -------
        str
            The validated title
        """

        if not title:
            raise ValueError("A note title is required.")

        if len(title) > 250:
            raise ValueError("The note title can have no more than 250 characters.")

        return title

    @validates("content")
    def validate_content(self, key, content: str) -> str:
        """Validates the content's length

        Parameters
        ----------
        content: str
            The note's content

        Returns
        -------
        str
            The validated content
        """

        if content and len(content) > 65535:
            raise ValueError("The note content can have no more than 65,535 characters.")

        return content


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
    note: Mapped["Note"] = relationship("Note", back_populates="scenes")
    scene: Mapped["Scene"] = relationship("Scene", back_populates="notes")

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
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey('notes.id'), primary_key=True)
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'), primary_key=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship("User")
    note: Mapped["Note"] = relationship("Note", back_populates="stories")
    story: Mapped["Story"] = relationship("Story", back_populates="notes")

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


class Scene(Base):
    """The Scene class represents a scene in the system.

    Attributes
    ----------
        id: int
            The scene's id
        user_id: int
            The id of the owner of this entry
        story_id: int
            The story's id
        chapter_id: int
            The chapter's id
        position: int
            The scene's position in the chapter
        title: str
            The scene's title
        description: str
            The scene's description
        content: str
            The scene's content
        created: str
            The creation datetime of the scene
        modified: str
            The last modification datetime of the scene
        user: User
            The user who owns this entry
        links: List[LinkScene]
            The links that the scene has
        notes: List[NoteScene]
            The notes that the scene has

    Methods
    -------
        __repr__()
            Returns a string representation of the scene
        __str__()
            Returns a string representation of the scene
        serialize()
            Returns a dictionary representation of the scene
        unserialize(data: dict)
            Updates the scene's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_description(description: str)
            Validates the description's length
        validate_content(content: str)
            Validates the content's length
    """

    __tablename__ = 'scenes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'))
    chapter_id: Mapped[int] = mapped_column(Integer, ForeignKey('chapters.id'))
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(String(250), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="scenes")
    user: Mapped["User"] = relationship("User")
    links: Mapped[Optional[List["LinkScene"]]] = relationship("LinkScene", back_populates="scene",
                    lazy="joined", cascade="all, delete, delete-orphan")
    notes: Mapped[Optional[List["NoteScene"]]] = relationship("NoteScene", back_populates="scene",
                    lazy="joined", cascade="all, delete, delete-orphan")

    def __repr__(self):
        """Returns a string representation of the scene.

        Returns
        -------
        str
            A string representation of the scene
        """

        return f'<Scene {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the scene.

        Returns
        -------
        str
            A string representation of the scene
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the scene.

        Returns
        -------
        dict
            A dictionary representation of the scene
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'story_id': self.story_id,
            'chapter_id': self.chapter_id,
            'position': self.position,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Scene":
        """Updates the scene's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the scene

        Returns
        -------
        Scene
            The unserialized scene
        """

        self.user_id = data.get('user_id', self.user_id)
        self.story_id = data.get('story_id', self.story_id)
        self.chapter_id = data.get('chapter_id', self.chapter_id)
        self.position = data.get('position', self.position)
        self.title = data.get('title', self.title)
        self.description = data.get('description', self.description)
        self.content = data.get('content', self.content)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length

        Parameters
        ----------
        title: str
            The scene's title

        Returns
        -------
        str
            The validated title
        """

        if title and len(title) > 250:
            raise ValueError("The scene title can have no more than 250 characters.")

        return title

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length

        Parameters
        ----------
        description: str
            The scene's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("The scene description can have no more than 65,535 characters.")

        return description

    @validates("content")
    def validate_content(self, key, content: str) -> str:
        """Validates the content's length

        Parameters
        ----------
        content: str
            The scene's content

        Returns
        -------
        str
            The validated content
        """

        if content and len(content) > 65535:
            raise ValueError("The scene content can have no more than 65,535 characters.")

        return content


class Story(Base):
    """The Story class represents a story in the system.

    Attributes
    ----------
        id: int
            The story's id
        user_id: int
            The id of the owner of this entry
        title: str
            The story's title
        description: str
            The story's description
        created: str
            The creation datetime of the story
        modified: str
            The last modification datetime of the story
        user: User
            The user who owns this entry
        chapters: List[Chapter]
            The chapters that the story has
        authors: List[AuthorStory]
            The authors that the story has
        references: List[Bibliography]
            The references that the story has
        submissions: List[Submission]
            The submissions that the story has
        links: List[LinkStory]
            The links that the story has
        notes: List[NoteStory]
            The notes that the story has

    Methods
    -------
        __repr__()
            Returns a string representation of the story
        __str__()
            Returns a string representation of the story
        serialize()
            Returns a dictionary representation of the story
        unserialize(data: dict)
            Updates the story's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_description(description: str)
            Validates the description's length
    """

    __tablename__ = 'stories'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User", back_populates="stories")
    chapters: Mapped[Optional[List["Chapter"]]] = relationship("Chapter", back_populates="story")
    authors: Mapped[Optional[List["AuthorStory"]]] = relationship("AuthorStory", back_populates="story", lazy="joined")
    references: Mapped[Optional[List["Bibliography"]]] = relationship("Bibliography", back_populates="story")
    submissions: Mapped[Optional[List["Submission"]]] = relationship("Submission", back_populates="story")
    links: Mapped[Optional[List["LinkStory"]]] = relationship("LinkStory", back_populates="story")
    notes: Mapped[Optional[List["NoteStory"]]] = relationship("NoteStory", back_populates="story")
    characters: Mapped[Optional[List["CharacterStory"]]] = relationship(
        "CharacterStory", back_populates="story", lazy="joined"
    )

    def __repr__(self):
        """Returns a string representation of the story.

        Returns
        -------
        str
            A string representation of the story
        """

        return f'<Story {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the story.

        Returns
        -------
        str
            A string representation of the story
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the story.

        Returns
        -------
        dict
            A dictionary representation of the story
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Story":
        """Updates the story's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the story

        Returns
        -------
        Story
            The unserialized story
        """

        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
        self.description = data.get('description', self.description)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length.

        Parameters
        ----------
        title: str
            The story's title

        Returns
        -------
        str
            The validated title
            :param key:
        """

        if not title:
            raise ValueError("A story title is required.")

        if len(title) > 250:
            raise ValueError("The story title can have no more than 250 characters.")

        return title

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length.

        Parameters
        ----------
        description: str
            The story's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("The story description can have no more than 65,535 characters.")

        return description


class SubmissionResultType(Enum):
    """The SubmissionResultType class represents the possible results of a submission.

    Attributes
    ----------
        ACCEPTED: str
            The submission was accepted
        REJECTED: str
            The submission was rejected
        REWRITE_REQUESTED: str
            The submission was requested to be rewritten
        PENDING: str
            The submission is pending
        WITHDRAWN: str
            The submission was withdrawn
        IGNORED: str
            The submission was ignored
    """

    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    REWRITE_REQUESTED = 'Rewrite Requested'
    PENDING = 'Pending'
    WITHDRAWN = 'Withdrawn'
    IGNORED = 'Ignored'


class Submission(Base):
    """The Submission class represents a submission in the system.

    Attributes
    ----------
        id: int
            The submission's id
        user_id: int
            The id of the owner of this entry
        story_id: int
            The story's id
        submitted_to: str
            The submission's recipient
        date_sent: str
            The submission's sent date
        date_reply_received: str
            The submission's reply received date
        date_published: str
            The submission's published date
        date_paid: str
            The submission's paid date
        result (SubmissionResultType):
            The submission's result
        amount: float
            The submission's amount
        created: str
            The creation datetime of the submission
        modified: str
            The last modification datetime of the submission
        user : User
            The user who owns this entry
        story: Story
            The story that the submission has

    Methods
    -------
        __repr__()
            Returns a string representation of the submission
        __str__()
            Returns a string representation of the submission
        serialize()
            Returns a dictionary representation of the submission
        unserialize(data: dict):
            Updates the submission's attributes with the values from the dictionary
        validate_submitted_to(submitted_to: str)
            Validates the submitted_to's length
        validate_date_sent(date_sent: str)
            Validates the date_sent's format
        validate_date_reply_received(date_reply_received: str)
            Validates the date_reply_received's format
        validate_date_published(date_published: str)
            Validates the date_published's format
        validate_date_paid(date_paid: str)
            Validates the date_paid's format
        validate_result(result: str)
            Validates the result's value
    """

    __tablename__ = 'submissions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey('stories.id'))
    submitted_to: Mapped[str] = mapped_column(Text, nullable=False)
    date_sent: Mapped[str] = mapped_column(Date, nullable=True)
    date_reply_received: Mapped[str] = mapped_column(Date, nullable=True)
    date_published: Mapped[str] = mapped_column(Date, nullable=True)
    date_paid: Mapped[str] = mapped_column(Date, nullable=True)
    result: Mapped[SubmissionResultType] = mapped_column(String(50), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    user: Mapped["User"] = relationship("User", back_populates="submissions")
    story: Mapped["Story"] = relationship("Story", back_populates="submissions")

    def __repr__(self):
        """Returns a string representation of the submission.

        Returns
        -------
        str
            A string representation of the submission
        """

        return f'<Submission {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the submission.

        Returns
        -------
        str
            A string representation of the submission
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the submission.

        Returns
        -------
        dict
            A dictionary representation of the submission
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'story_id': self.story_id,
            'submitted_to': self.submitted_to,
            'date_sent': str(self.date_sent),
            'date_reply_received': str(self.date_reply_received),
            'date_published': str(self.date_published),
            'date_paid': str(self.date_paid),
            'result': self.result,
            'amount': self.amount,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Submission":
        """Updates the submission's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the submission

        Returns
        -------
        Submission
            The unserialized submission
        """

        self.user_id = data.get('user_id', self.user_id)
        self.story_id = data.get('story_id', self.story_id)
        self.submitted_to = data.get('submitted_to', self.submitted_to)
        self.date_sent = data.get('date_sent', self.date_sent)
        self.date_reply_received = data.get('date_reply_received', self.date_reply_received)
        self.date_published = data.get('date_published', self.date_published)
        self.date_paid = data.get('date_paid', self.date_paid)
        self.result = data.get('result', self.result)
        self.amount = data.get('amount', self.amount)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("submitted_to")
    def validate_submitted_to(self, key, submitted_to: str) -> str:
        """Validates the submitted_to's length.

        Parameters
        ----------
        submitted_to: str
            The submission's recipient

        Returns
        -------
        str
            The validated submitted_to
        """

        if not submitted_to:
            raise ValueError("A submission recipient is required.")

        if len(submitted_to) > 65535:
            raise ValueError("The submission recipient can have no more than 65,535 characters.")

        return submitted_to

    @validates("date_sent")
    def validate_date_sent(self, key, date_sent: str) -> str | None:
        """Validates the date_sent's format.

        Parameters
        ----------
        date_sent: str
            The submission's sent date

        Returns
        -------
        str
            The validated date_sent
        """

        if type(date_sent) is str and bool(datetime.strptime(date_sent, date_format)) is False:
            raise ValueError("The submission sent date must be in the format 'YYYY-MM-DD'.")

        return date_sent

    @validates("date_reply_received")
    def validate_date_reply_received(self, key, date_reply_received: str) -> str | None:
        """Validates the date_reply_received's format.

        Parameters
        ----------
        date_reply_received: str
            The submission's reply received date

        Returns
        -------
        str
            The validated date_reply_received
        """

        if date_reply_received is not None and bool(datetime.strptime(date_reply_received, date_format)) is False:
            raise ValueError("The submission reply received date must be in the format 'YYYY-MM-DD'.")

        return date_reply_received

    @validates("date_published")
    def validate_date_published(self, key, date_published: str) -> str | None:
        """Validates the date_published's format.

        Parameters
        ----------
        date_published: str
            The submission's published date

        Returns
        -------
        str
            The validated date_published
        """

        if date_published is not None and bool(datetime.strptime(date_published, date_format)) is False:
            raise ValueError("The submission published date must be in the format 'YYYY-MM-DD'.")

        return date_published

    @validates("date_paid")
    def validate_date_paid(self, key, date_paid: str) -> str | None:
        """Validates the date_paid's format.

        Parameters
        ----------
        date_paid: str
            The submission's paid date

        Returns
        -------
        str
            The validated date_paid
        """

        if date_paid is not None and bool(datetime.strptime(date_paid, date_format)) is False:
            raise ValueError("The submission paid date must be in the format 'YYYY-MM-DD'.")

        return date_paid

    @validates("result")
    def validate_result(self, key, result: str) -> str:
        """Validates the result's value.

        Parameters
        ----------
        result: str
            The submission's result

        Returns
        -------
        str
            The validated result
        """

        if result is not None:
            if result not in SubmissionResultType.__members__.values():
                raise ValueError("Invalid submission result type.")

        return result


class User(Base):
    """The User class represents a user in the system.

    Attributes
    ----------
        id: int
            The user's id
        uuid: str
            The user's UUID
        username: str
            The user's username
        email: str
            The user's email address
        password: str
            The user's password hash
        is_active: bool
            The user's active status
        is_banned: bool
            The user's banned status
        created: str
            The creation datetime of the user
        modified: str
            The last modification datetime of the user
        activities: List[Activity]
            The activities that the user has
        authors: List[Author]
            The authors that the user has
        characters: List[Character]
            The characters that the user has
        events: List[Event]
            The events that the user has
        images: List[Image]
            The images that the user has
        links: List[Link]
            The links that the user has
        locations: List[Location]
            The locations that the user has
        notes: List[Note]
            The notes that the user has
        stories: List[Story]
            The stories that the user has
        submissions: List[Submission]
            The submissions that the user has

    Methods
    -------
        __repr__()
            Returns a string representation of the user
        __str__()
            Returns a string representation of the user
        serialize()
            Returns a dictionary representation of the user
        unserialize(data: dict)
            Updates the user's attributes with the values from the dictionary
        validate_uuid(uuid: str)
            Validates the UUID's length and format
        validate_username(username: str)
            Validates the username's length
        validate_email(email: str)
            Validates the email's length
        validate_password(password: str)
            Validates the password's length
    """

    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()), onupdate=str(datetime.now()))
    activities: Mapped[Optional[List["Activity"]]] = relationship("Activity", back_populates="user")
    authors: Mapped[Optional[List["Author"]]] = relationship("Author", back_populates="user", lazy="joined")
    characters: Mapped[Optional[List["Character"]]] = relationship("Character", back_populates="user")
    events: Mapped[Optional[List["Event"]]] = relationship("Event", back_populates="user")
    images: Mapped[Optional[List["Image"]]] = relationship("Image", back_populates="user")
    links: Mapped[Optional[List["Link"]]] = relationship("Link", back_populates="user")
    locations: Mapped[Optional[List["Location"]]] = relationship("Location", back_populates="user")
    notes: Mapped[Optional[List["Note"]]] = relationship("Note", back_populates="user")
    stories: Mapped[Optional[List["Story"]]] = relationship("Story", back_populates="user")
    submissions: Mapped[Optional[List["Submission"]]] = relationship("Submission", back_populates="user")

    def __repr__(self):
        """Returns a string representation of the user.

        Returns
        -------
        str
            A string representation of the user
        """

        return f'<User {self.id!r} - {self.username!r}>'

    def __str__(self):
        """Returns a string representation of the user.

        Returns
        -------
        str
            A string representation of the user
        """

        return f'{self.id!r} - {self.username}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the user.

        Returns
        -------
        dict
            A dictionary representation of the user
        """

        return {
            'id': self.id,
            'uuid': self.uuid,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'is_active': self.is_active,
            'is_banned': self.is_banned,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "User":
        """Updates the user's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the user

        Returns
        -------
        User
            The unserialized user
        """

        self.uuid = data.get('uuid', self.uuid)
        self.username = data.get('username', self.username)
        self.email = data.get('email', self.email)
        self.is_active = data.get('is_active', self.is_active)
        self.is_banned = data.get('is_banned', self.is_banned)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("uuid")
    def validate_uuid(self, key, uuid: str) -> str:
        """Validates the UUID's length and format.

        Parameters
        ----------
        uuid: str
            The user's UUID

        Returns
        -------
        str
            The validated UUID
        """

        if not uuid:
            raise ValueError("A user UUID is required.")

        if len(uuid) != 36:
            raise ValueError("The user UUID must have 36 characters.")

        if not uuid_validator(uuid):
            raise ValueError("The user UUID is not valid.")

        return uuid

    @validates("username")
    def validate_username(self, key, username: str) -> str:
        """Validates the username's length.

        Parameters
        ----------
        username: str
            The user's username

        Returns
        -------
        str
            The validated username
        """

        if not username:
            raise ValueError("A username is required.")

        if len(username) > 50:
            raise ValueError("The username can have no more than 50 characters.")

        return username

    @validates("email")
    def validate_email(self, key, email: str) -> str:
        """Validates the email's length.

        Parameters
        ----------
        email: str
            The user's email address

        Returns
        -------
        str
            The validated email
        """

        if not email:
            raise ValueError("An email address is required.")

        if len(email) > 100:
            raise ValueError("The email address can have no more than 100 characters.")

        if not validators.email(email):
            raise ValueError("The email address is not valid.")

        return email

    @validates("password")
    def validate_password(self, key, password: str) -> str:
        """Validates the password's length.

        Parameters
        ----------
        password: str
            The user's password hash

        Returns
        -------
        str
            The validated password
        """

        if not password:
            raise ValueError("A password is required.")

        if len(password) > 250:
            raise ValueError("The password can have no more than 250 characters.")

        return password
