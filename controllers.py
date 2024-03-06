import binascii
import os
from datetime import date
from typing import Type
import bcrypt
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
import uuid
from models import *


def hash_password(password):
    """Hash a password, return hashed password"""

    if password == '':
        raise ValueError('The password cannot be empty.')

    if len(password) < 8:
        raise ValueError('The password must be at least 8 characters.')

    if len(password) > 24:
        raise ValueError('The password cannot be more than 24 characters.')

    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(rounds=12)).decode('utf8')


def verify_password(password, hashed_password):
    """Verify a password, return true if verified, false if not"""

    return bcrypt.checkpw(password.encode('utf8'), hashed_password.encode('utf8'))


class BaseController:
    """Base controller encapsulates common functionality for all controllers

    Attributes
    ----------
    _self : BaseController
        The instance of the base controller
    _owner : User
        The current user of the base controller
    _session : Session
        The database session
    """
    _self = None
    _owner = None
    _session = None

    def __new__(cls, session: Session, owner: Type[User]):
        """Enforce Singleton pattern"""

        if cls._self is None:
            cls._self = super().__new__(cls)

        return cls._self

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        self._session = session
        self._owner = owner


class ActivityController(BaseController):
    """Activity controller encapsulates activity management functionality

    Attributes
    ----------
    _self : ActivityController
        The instance of the activity controller
    _owner : User
        The current user of the activity controller
    _session : Session
        The database session

    Methods
    -------
    get_activity_by_id(activity_id: int)
        Get an activity by id
    get_activities()
        Get all activities associated with a user, sorted by created date with most recent first
    get_activities_page(user_id: int, page: int, per_page: int)
        Get a single page of activities associated with a user, sorted by created date with most recent first
    get_activity_count()
        Get activity count associated with a user
    search_activities(search: str)
        Search for activities by summary
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def get_activity_by_id(self, activity_id: int) -> Type[Activity] | None:
        """Get an activity by id

        Parameters
        ----------
        activity_id : int
            The id of the activity to get

        Returns
        -------
        Activity | None
            The activity object or None if not found
        """

        with self._session as session:
            activity = session.query(Activity).filter(
                Activity.id == activity_id, Activity.user_id == self._owner.id
            ).first()
            return activity if activity else None

    def get_activities(self) -> list:
        """Get all activities associated with a user, sorted by created date with most recent first

        Returns
        -------
        list
            A list of activity objects
        """

        with self._session as session:
            return session.query(Activity).filter(
                Activity.user_id == self._owner.id
            ).order_by(Activity.created.desc()).all()

    def get_activities_page(self, user_id: int, page: int, per_page: int) -> list:
        """Get a single page of activities associated with a user, sorted by created date with most recent first

        Parameters
        ----------
        user_id : int
            The id of the user
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of activity objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Activity).filter(
                Activity.user_id == user_id
            ).order_by(Activity.created.desc()).offset(offset).limit(per_page).all()

    def get_activity_count(self, user_id: int) -> int:
        """Get activity count associated with a user

        Parameters
        ----------
        user_id : int
            The id of the user

        Returns
        -------
        int
            The number of activities
        """

        with self._session as session:
            return session.query(func.count(Activity.id)).filter(Activity.user_id == user_id).scalar()

    def search_activities(self, search: str) -> list:
        """Search for activities by summary

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of activity objects
        """

        with self._session as session:
            return session.query(Activity).filter(
                Activity.summary.like(f'%{search}%'), Activity.user_id == self._owner.id
            ).all()


class AuthorController(BaseController):
    """Author controller encapsulates author management functionality

    Attributes
    ----------
    _self : AuthorController
        The instance of the author controller
    _owner : User
        The current user of the author controller
    _session : Session
        The database session

    Methods
    -------
    create_author(is_pseudonym: bool, name: str, initials: str)
        Create a new author
    update_author(is_pseudonym: bool, name: str, initials: str)
        Update an author
    change_pseudonym_status(author_id: int, is_pseudonym: bool)
        Change the pseudonym status of an author
    delete_author(author_id: int)
        Delete an author
    get_author_by_id(author_id: int)
        Get an author by id
    get_author_by_name(name: str)
        Get an author by name
    get_author_count()
        Get author count associated with a user
    get_all_authors()
        Get all authors associated with a user
    get_authors_page(page: int, per_page: int)
        Get a single page of authors from the database associated with a user
    get_authors_by_story_id(story_id: int)
        Get all authors associated with a story
    search_authors(search: str)
        Search for authors by name
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_author(self, is_pseudonym: bool, name: str, initials: str = None) -> Author:
        """Create a new author

        Parameters
        ----------
        is_pseudonym : bool
            Whether the author is a pseudonym
        name : str
            The name of the new author
        initials : str
            The initials of the new author, optional

        Returns
        -------
        Author
            The new author object
        """

        with self._session as session:

            try:
                name_exists = session.query(Author).filter(
                    Author.name == name, Author.user_id == self._owner.id
                ).first()

                if name_exists:
                    raise Exception('That author already exists.')

                created = datetime.now()
                modified = created

                author = Author(user_id=self._owner.id, name=name, initials=initials, is_pseudonym=is_pseudonym,
                                created=created, modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Author {author.name} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(author)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return author

    def update_author(self, author_id: int, is_pseudonym: bool, name: str, initials: str = None) -> Type[Author]:
        """Update an author

        Parameters
        ----------
        author_id : int
            The id of the author to update
        is_pseudonym : bool
            Whether the author is a pseudonym
        name : str
            The name of the author
        initials : str
            The initials of the author, optional

        Returns
        -------
        Author
            The updated author object
        """

        with self._session as session:

            try:
                author = session.query(Author).filter(
                    Author.id == author_id, Author.user_id == self._owner.id
                ).first()

                if not author:
                    raise ValueError('Author not found.')

                name_exists = session.query(Author).filter(
                    Author.name == name, Author.user_id == self._owner.id
                ).first()

                if name_exists:
                    raise Exception('That author already exists.')

                author.is_pseudonym = is_pseudonym
                author.name = name
                author.initials = initials
                author.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Author {author.name} updated by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return author

    def change_pseudonym_status(self, author_id: int, is_pseudonym: bool) -> Type[Author]:
        """Change the pseudonym status of an author

        Parameters
        ----------
        author_id : int
            The id of the author to update
        is_pseudonym : bool
            Whether the author is a pseudonym

        Returns
        -------
        Author
            The updated author object
        """

        with self._session as session:

            try:
                author = session.query(Author).filter(
                    Author.id == author_id, Author.user_id == self._owner.id
                ).first()

                if not author:
                    raise ValueError('Author not found.')

                author.is_pseudonym = is_pseudonym
                author.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Author {author.name} pseudonym status changed by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return author

    def delete_author(self, author_id: int) -> bool:
        """Delete an author

        Parameters
        ----------
        author_id : int
            The id of the author to delete

        Returns
        -------
        bool
            True if the author was deleted, False if not
        """

        with self._session as session:

            try:
                author = session.query(Author).filter(
                    Author.id == author_id, Author.user_id == self._owner.id
                ).first()

                if not author:
                    raise ValueError('Author not found.')

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Author {author.name} deleted by {self._owner.username}',
                                    created=datetime.now())

                session.delete(author)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_author_by_id(self, author_id: int) -> Type[Author] | None:
        """Get an author by id

        Parameters
        ----------
        author_id : int
            The id of the author to get

        Returns
        -------
        Author | None
            The author object or None if not found
        """

        with self._session as session:
            author = session.query(Author).filter(
                Author.id == author_id, Author.user_id == self._owner.id
            ).first()
            return author if author else None

    def get_author_by_name(self, name: str) -> Type[Author] | None:
        """Get an author by name

        Parameters
        ----------
        name : str
            The name of the author to get

        Returns
        -------
        Author | None
            The author object or None if not found
        """

        with self._session as session:
            author = session.query(Author).filter(
                Author.name == name, Author.user_id == self._owner.id
            ).first()
            return author if author else None

    def get_author_count(self) -> int:
        """Get author count associated with a user

        Returns
        -------
        int
            The number of authors
        """

        with self._session as session:
            return session.query(func.count(Author.id)).filter(Author.user_id == self._owner.id).scalar()

    def get_all_authors(self) -> list | None:
        """Get all authors associated with a user

        Parameters
        ----------
        user_id : int
            The id of the user

        Returns
        -------
        list | None
            A list of author objects or None if none are found
        """

        with self._session as session:
            return session.query(Author).filter(Author.user_id == self._owner.id).all()

    def get_authors_page(self, page: int, per_page: int) -> list | None:
        """Get a single page of authors from the database associated with a user

        Parameters
        ----------
        user_id : int
            The id of the user who owns the author names
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list | None
            A list of author objects or None if none are found
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Author).filter(Author.user_id == self._owner.id).offset(offset).limit(per_page).all()

    def get_authors_by_story_id(self, story_id: int) -> list | None:
        """Get all authors associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list | None
            A list of author objects or None if the story is not found
        """
        with self._session as session:
            story = session.query(Story).filter(
                Story.id == story_id, Story.user_id == self._owner.id
            ).first()
            return story.authors if story else None

    def search_authors(self, search: str) -> list | None:
        """Search for authors by name

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list | None
            A list of author objects or None if none are found
        """

        with self._session as session:
            return session.query(Author).filter(
                Author.name.like(f'%{search}%'), Author.user_id == self._owner.id
            ).all()


class BibliographyController(BaseController):
    """Bibliography controller encapsulates bibliography management functionality

    Attributes
    ----------
    _self : BibliographyController
        The instance of the bibliography controller
    _owner : User
        The current user of the bibliography controller
    _session : Session
        The database session

    Methods
    -------
    create_bibliography(story_id: int, title: str, pages: str, publication_date: str, other_text: str)
        Create a new bibliography
    update_bibliography(bibliography_id: int, story_id: int, title: str, pages: str, publication_date: str, \
                        other_text: str)
        Update a bibliography
    delete_bibliography(bibliography_id: int)
        Delete a bibliography
    get_bibliography_by_id(bibliography_id: int)
        Get a bibliography by id
    get_bibliography_by_title(title: str)
        Get a bibliography by title
    get_bibliography_count()
        Get bibliography count associated with a user
    get_all_bibliographies()
        Get all bibliographies associated with a user
    get_bibliographies_page(page: int, per_page: int)
        Get a single page of bibliographies from the database associated with a user
    get_bibliographies_by_story_id(story_id: int)
        Get all bibliographies associated with a story
    get_bibliographies_page_by_story_id(story_id: int, page: int, per_page: int)
        Get a single page of bibliographies associated with a story from the database
    search_bibliographies(search: str)
        Search for bibliographies by title associated with a user
    search_bibliographies_by_story_id(story_id: int, search: str)
        Search for bibliographies by title associated with a story
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_bibliography(self, story_id: int, title: str, pages: str = None, publication_date: str = None,
                            other_text: str = None) -> Bibliography:
        """Create a new bibliography

        Parameters
        ----------
        story_id : int
            The id of the story
        title : str
            The title of the referenced work
        pages : str
            The pages of the referenced work, optional
        publication_date : str
            The publication date of the referenced work, optional
        other_text : str
            Other text, optional

        Returns
        -------
        Bibliography
            The new bibliography object
        """

        with self._session as session:
            try:
                title_exists = session.query(Bibliography).filter(
                    Bibliography.title == title, Bibliography.story_id == story_id,
                    Bibliography.user_id == self._owner.id
                ).first()

                if title_exists:
                    raise Exception('A reference with the same title is already associated with that story.')

                created = datetime.now()
                modified = created

                bibliography = Bibliography(user_id=self._owner.id, story_id=story_id, title=title, pages=pages,
                                            publication_date=publication_date, other_text=other_text, created=created,
                                            modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Bibliography {bibliography.title[:50]} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(bibliography)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return bibliography

    def update_bibliography(self, bibliography_id: int, story_id: int, title: str, pages: str = None,
                            publication_date: str = None, other_text: str = None) -> Type[Bibliography]:
        """Update a bibliography

        Parameters
        ----------
        bibliography_id : int
            The id of the bibliography to update
        story_id : int
            The id of the story
        title : str
            The title of the referenced work
        pages : str
            The pages of the referenced work, optional
        publication_date : str
            The publication date of the referenced work, optional
        other_text : str
            Other text, optional

        Returns
        -------
        Bibliography
            The updated bibliography object
        """

        with self._session as session:
            try:
                bibliography = session.query(Bibliography).filter(
                    Bibliography.id == bibliography_id, Bibliography.user_id == self._owner.id
                ).first()

                if not bibliography:
                    raise ValueError('Bibliography not found.')

                title_exists = session.query(Bibliography).filter(
                    Bibliography.title == title, Bibliography.story_id == story_id
                ).first()

                if title_exists:
                    raise Exception('A reference with the same title is already associated with that story.')

                bibliography.story_id = story_id
                bibliography.title = title
                bibliography.pages = pages
                bibliography.publication_date = publication_date
                bibliography.other_text = other_text
                bibliography.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Bibliography {bibliography.title} updated by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return bibliography

    def delete_bibliography(self, bibliography_id: int) -> bool:
        """Delete a bibliography

        Before deleting the Bibliography, first delete any BibliographyAuthor objects associated with the Bibliography.

        Parameters
        ----------
        bibliography_id : int
            The id of the bibliography to delete

        Returns
        -------
        bool
            True if the bibliography was deleted, False if not
        """

        with self._session as session:

            try:
                bibliography = session.query(Bibliography).filter(
                    Bibliography.id == bibliography_id, Bibliography.user_id == self._owner.id
                ).first()

                if not bibliography:
                    raise ValueError('Bibliography not found.')

                session.query(BibliographyAuthor).filter(BibliographyAuthor.bibliography_id == bibliography_id).delete()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Bibliography {bibliography.title} deleted by {self._owner.username}',
                                    created=datetime.now())

                session.delete(bibliography)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_bibliography_by_id(self, bibliography_id: int) -> Type[Bibliography] | None:
        """Get a bibliography by id

        Parameters
        ----------
        bibliography_id : int
            The id of the bibliography to get

        Returns
        -------
        Bibliography | None
            The bibliography object or None if not found
        """

        with self._session as session:
            bibliography = session.query(Bibliography).filter(
                Bibliography.id == bibliography_id, Bibliography.user_id == self._owner.id
            ).first()
            return bibliography if bibliography else None

    def get_bibliography_by_title(self, title: str) -> Type[Bibliography] | None:
        """Get a bibliography by title

        Parameters
        ----------
        title : str
            The title of the referenced work

        Returns
        -------
        Bibliography | None
            The bibliography object or None if not found
        """

        with self._session as session:
            bibliography = session.query(Bibliography).filter(
                Bibliography.title == title, Bibliography.user_id == self._owner.id
            ).first()
            return bibliography if bibliography else None

    def get_bibliography_count(self) -> int:
        """Get bibliography count associated with a user

        Returns
        -------
        int
            The number of bibliographies
        """

        with self._session as session:
            return session.query(func.count(Bibliography.id)).filter(Bibliography.user_id == self._owner.id).scalar()

    def get_all_bibliographies(self) -> list:
        """Get all bibliographies associated with a user

        Returns
        -------
        list
            A list of bibliography objects
        """

        with self._session as session:
            return session.query(Bibliography).filter(Bibliography.user_id == self._owner.id).all()

    def get_bibliographies_page(self, page: int, per_page: int) -> list:
        """Get a single page of bibliographies from the database associated with a user

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of bibliography objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Bibliography).filter(
                Bibliography.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def get_bibliographies_by_story_id(self, story_id: int) -> list | None:
        """Get all bibliographies associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list | None
            A list of bibliography objects or None if the story is not found
        """

        with self._session as session:
            bibliographies = session.query(Bibliography).filter(
                Bibliography.story_id == story_id, Bibliography.user_id == self._owner.id
            ).all()
            return bibliographies if bibliographies else None

    def get_bibliographies_page_by_story_id(self, story_id: int, page: int, per_page: int) -> list | None:
        """Get a single page of bibliographies associated with a story from the database

        Parameters
        ----------
        story_id : int
            The id of the story
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list | None
            A list of bibliography objects or None if the story is not found
        """

        with self._session as session:
            offset = (page - 1) * per_page
            bibliographies = session.query(Bibliography).filter(
                Bibliography.story_id == story_id, Bibliography.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()
            return bibliographies if bibliographies else None

    def search_bibliographies(self, search: str) -> list:
        """Search for bibliographies by title associated with a user

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of bibliography objects
        """

        with self._session as session:
            return session.query(Bibliography).filter(
                Bibliography.title.like(f'%{search}%'), Bibliography.user_id == self._owner.id
            ).all()

    def search_bibliographies_by_story_id(self, story_id: int, search: str) -> list | None:
        """Search for bibliographies by title associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story
        search : str
            The search string

        Returns
        -------
        list | None
            A list of bibliography objects or None if none found
        """

        with self._session as session:
            return session.query(Bibliography).filter(
                Bibliography.story_id == story_id, Bibliography.title.like(f'%{search}%'),
                Bibliography.user_id == self._owner.id
            ).all()


class ChapterController(BaseController):
    """Chapter controller encapsulates chapter management functionality

    Attributes
    ----------
    _self : ChapterController
        The instance of the chapter controller
    _owner : User
        The current user of the chapter controller

    Methods
    -------
    create_chapter(story_id: int, title: str, description: str)
        Create a new chapter
    update_chapter(chapter_id: int, title: str, description: str)
        Update a chapter
    delete_chapter(chapter_id: int)
        Delete a chapter
    change_chapter_position(chapter_id: int, position: int)
        Set the position of a chapter
    get_chapter_by_id(chapter_id: int)
        Get a chapter by id
    get_all_chapters()
        Get all chapters associated with a user
    get_chapters_page(page: int, per_page: int)
        Get a single page of chapters from the database associated with a user
    get_chapter_count()
        Get chapter count associated with a user
    get_all_chapters_by_story_id(story_id: int)
        Get all chapters associated with a story
    get_chapters_page_by_story_id(story_id: int, page: int, per_page: int)
        Get a single page of chapters associated with a story from the database
    get_chapter_count_by_story_id(story_id: int)
        Get chapter count associated with a story
    search_chapters(search: str)
        Search for chapters by title and description belonging to a specific user
    search_chapters_by_story_id(story_id: int, search: str)
        Search for chapters by title and description belonging to a specific story
    append_links_to_chapter(chapter_id: int, links: list)
        Append links to a chapter
    get_links_by_chapter_id(chapter_id: int)
        Get all links associated with a chapter
    append_notes_to_chapter(chapter_id: int, notes: list)
        Append notes to a chapter
    get_notes_by_chapter_id(chapter_id: int)
        Get all notes associated with a chapter
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_chapter(self, story_id: int, title: str, description: str = None) -> Chapter:
        """Create a new chapter

        Parameters
        ----------
        story_id : int
            The id of the story
        title : str
            The title of the chapter
        description : str
            The description of the chapter, optional

        Returns
        -------
        Chapter
            The new chapter object
        """

        with self._session as session:
            try:
                title_exists = session.query(Chapter).filter(
                    Chapter.title == title, Chapter.story_id == story_id, Chapter.user_id == self._owner.id
                ).first()

                if title_exists:
                    raise Exception('This story already has a chapter with the same title.')

                position = session.query(func.max(Chapter.position)).filter(
                    Chapter.story_id == story_id, Chapter.user_id == self._owner.id
                ).scalar()
                position = int(position) + 1 if position else 1
                created = datetime.now()
                modified = created

                chapter = Chapter(user_id=self._owner.id, story_id=story_id, position=position, title=title,
                                  description=description, created=created, modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Chapter {chapter.title[:50]} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(chapter)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return chapter

    def update_chapter(self, chapter_id: int, title: str, description: str = None) -> Type[Chapter]:
        """Update a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter to update
        title : str
            The title of the chapter
        description : str
            The description of the chapter, optional

        Returns
        -------
        Chapter
            The updated chapter object
        """

        with self._session as session:
            try:
                chapter = session.query(Chapter).filter(
                    Chapter.id == chapter_id, Chapter.user_id == self._owner.id
                ).first()

                if not chapter:
                    raise ValueError('Chapter not found.')

                title_exists = session.query(Chapter).filter(
                    Chapter.title == title, Chapter.story_id == chapter.story_id,
                    Chapter.user_id == self._owner.id
                ).first()

                if title_exists:
                    raise Exception('This story already has a chapter with the same title.')

                chapter.title = title
                chapter.description = description
                chapter.modified = str(datetime.now())

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Chapter {chapter.title} updated by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return chapter

    def delete_chapter(self, chapter_id: int) -> bool:
        """Delete a chapter

        Each Chapter contains an arbitrary number of Scene objects, but before those Scenes can be deleted, the links
        and notes associated with them through the LinkScene and LinkNote objects must be deleted before deleting those
        associations. Next, the scenes are deleted. Before the Chapter can be deleted, the links, notes, and joining
        associations among the ChapterLink and NoteLink objects must be deleted. The last task to perform before the
        Chapter can be deleted is to fix the hole in the position scheme its deletion is going to leave. To do that,
        we'll decrement by 1 the position for each sibling chapter sharing the same story id and having a position that
        is greater than that of the Chapter being deleted. Finally, the Chapter is deleted.

        Parameters
        ----------
        chapter_id : int
            The id of the chapter to delete

        Returns
        -------
        bool
            True if the chapter was deleted, False if not
        """

        with self._session as session:
            try:
                chapter = session.query(Chapter).filter(
                    Chapter.id == chapter_id, Chapter.user_id == self._owner.id
                ).first()

                if not chapter:
                    raise ValueError('Chapter not found.')

                for scene in chapter.scenes:
                    for link_scene in scene.links:
                        session.query(LinkNote).filter(
                            LinkNote.link_id == link_scene.link_id, LinkNote.user_id == self._owner.id
                        ).delete()
                        session.query(Link).filter(
                            Link.id == link_scene.link_id, Link.user_id == self._owner.id
                        ).delete()
                        session.delete(link_scene)
                    for note_scene in scene.notes:
                        session.query(LinkNote).filter(
                            LinkNote.note_id == note_scene.note_id, LinkNote.user_id == self._owner.id
                        ).delete()
                        session.query(Note).filter(
                            Note.id == note_scene.note_id, Note.user_id == self._owner.id
                        ).delete()
                        session.delete(note_scene)
                    session.delete(scene)

                for link in chapter.links:
                    session.query(LinkNote).filter(
                        LinkNote.link_id == link.link_id, LinkNote.user_id == self._owner.id
                    ).delete()
                    session.query(Link).filter(Link.id == link.link_id).delete()
                    session.delete(link)

                for note in chapter.notes:
                    session.query(LinkNote).filter(
                        LinkNote.note_id == note.note_id, LinkNote.user_id == self._owner.id
                    ).delete()
                    session.query(Note).filter(
                        Note.id == note.note_id, Note.user_id == self._owner.id
                    ).delete()
                    session.delete(note)

                siblings = session.query(Chapter).filter(
                    Chapter.story_id == chapter.story_id, Chapter.user_id == self._owner.id,
                    Chapter.position > chapter.position
                ).all()

                for sibling in siblings:
                    sibling.position -= 1
                    sibling.created = datetime.strptime(str(sibling.created), datetime_format)
                    sibling.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Chapter {chapter.title} deleted by {self._owner.username}',
                                    created=datetime.now())

                session.delete(chapter)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def change_chapter_position(self, chapter_id: int, position: int) -> Type[Chapter]:
        """Set the position of a chapter

        First, determine whether the new position is closer to 1 or further from 1. If closer to one, get all sibling
        chapters with positions greater than or equal to the new position but less than the current position, and
        increment those position values by 1. If the target position is further away from 1 than the current position,
        get all sibling chapters with positions greater than the current position but less than or equal to the new
        position, and decrement those position values by 1. Finally, set the position of the target chapter to the new
        position. Return the new position.

        Parameters
        ----------
        chapter_id : int
            The id of the chapter to update
        position : int
            The position of the chapter

        Returns
        -------
        Chapter
            The updated chapter object
        """

        with self._session as session:
            try:
                chapter = session.query(Chapter).filter(
                    Chapter.id == chapter_id, Chapter.user_id == self._owner.id
                ).first()

                if not chapter:
                    raise ValueError('Chapter not found.')

                if position < 1:
                    raise ValueError('Position must be greater than 0.')

                highest_position = session.query(func.max(Chapter.position)).filter(
                    Chapter.story_id == chapter.story_id, Chapter.user_id == self._owner.id
                ).scalar()

                if position > highest_position:
                    raise ValueError(f'Position must be less than or equal to {highest_position}.')

                if position == chapter.position:
                    return chapter.position

                if position < chapter.position:
                    siblings = session.query(Chapter).filter(
                        Chapter.story_id == chapter.story_id, Chapter.user_id == self._owner.id,
                        Chapter.position >= position, Chapter.position < chapter.position
                    ).all()

                    for sibling in siblings:
                        sibling.position += 1
                        sibling.created = datetime.strptime(str(sibling.created), datetime_format)
                        sibling.modified = datetime.now()

                else:
                    siblings = session.query(Chapter).filter(
                        Chapter.story_id == chapter.story_id, Chapter.user_id == self._owner.id,
                        Chapter.position > chapter.position, Chapter.position <= position
                    ).all()

                    for sibling in siblings:
                        sibling.position -= 1
                        sibling.created = datetime.strptime(str(sibling.created), datetime_format)
                        sibling.modified = datetime.now()

                chapter.position = position
                chapter.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Chapter {chapter.title[:50]} position changed by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return chapter

    def get_chapter_by_id(self, chapter_id: int) -> Type[Chapter] | None:
        """Get a chapter by id

        Parameters
        ----------
        chapter_id : int
            The id of the chapter to get

        Returns
        -------
        Chapter | None
            The chapter object or None if not found
        """

        with self._session as session:
            chapter = session.query(Chapter).filter(
                Chapter.id == chapter_id, Chapter.user_id == self._owner.id
            ).first()
            return chapter if chapter else None

    def get_chapters(self) -> list | None:
        """Get all chapters associated with a user

        Chapters are sorted by story id and position.

        Returns
        -------
        list | None
            A list of chapter objects or None if none are found
        """

        with self._session as session:
            return session.query(Chapter).filter(
                Chapter.user_id == self._owner.id
            ).order_by(Chapter.story_id, Chapter.position).all()

    def get_chapters_page(self, page: int, per_page: int) -> list | None:
        """Get a single page of chapters from the database associated with a user

        Chapters are sorted by story id and position.

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list | None
            A list of chapter objects or None if none are found
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Chapter).filter(
                Chapter.user_id == self._owner.id
            ).order_by(Chapter.story_id, Chapter.position).offset(offset).limit(per_page).all()

    def get_chapter_count(self) -> int:
        """Get chapter count associated with a user

        Returns
        -------
        int
            The number of chapters
        """

        with self._session as session:
            return session.query(func.count(Chapter.id)).filter(Chapter.user_id == self._owner.id).scalar()

    def get_chapters_by_story_id(self, story_id: int) -> list | None:
        """Get all chapters associated with a story

        The returned list will be sorted by the position.

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list } None
            A list of chapter objects or None if none are found
        """

        with self._session as session:
            return session.query(Chapter).filter(
                Chapter.story_id == story_id, Chapter.user_id == self._owner.id
            ).order_by(Chapter.position).all()

    def get_chapters_page_by_story_id(self, story_id: int, page: int, per_page: int) -> list | None:
        """Get a single page of chapters associated with a story from the database

        The returned list will be sorted by the position.

        Parameters
        ----------
        story_id : int
            The id of the story
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list | None
            A list of chapter objects or None if none are found
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Chapter).filter(
                Chapter.story_id == story_id, Chapter.user_id == self._owner.id
            ).order_by(Chapter.position).offset(offset).limit(per_page).all()

    def get_chapter_count_by_story_id(self, story_id: int) -> int:
        """Get chapter count associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        int
            The number of chapters
        """

        with self._session as session:
            return session.query(func.count(Chapter.id)).filter(
                Chapter.story_id == story_id, Chapter.user_id == self._owner.id
            ).scalar()

    def search_chapters(self, search: str) -> list:
        """Search for chapters by title and description belonging to a specific user

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of chapter objects
        """

        with self._session as session:
            return session.query(Chapter).filter(
                or_(Chapter.title.like(f'%{search}%'), Chapter.description.like(f'%{search}%')),
                Chapter.user_id == self._owner.id
            ).all()

    def search_chapters_by_story_id(self, story_id: int, search: str) -> list:
        """Search for chapters by title and description belonging to a specific story

        Parameters
        ----------
        story_id : int
            The id of the story
        search : str
            The search string

        Returns
        -------
        list
            A list of chapter objects
        """

        with self._session as session:
            return session.query(Chapter).filter(
                or_(Chapter.title.like(f'%{search}%'), Chapter.description.like(f'%{search}%')),
                Chapter.story_id == story_id, Chapter.user_id == self._owner.id
            ).all()

    def append_links_to_chapter(self, chapter_id: int, links: list) -> Type[Chapter]:
        """Append links to a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter
        links : list
            A list of link ids

        Returns
        -------
        Chapter
            The updated chapter object
        """

        with self._session as session:
            try:
                chapter = session.query(Chapter).filter(
                    Chapter.id == chapter_id, Chapter.user_id == self._owner.id
                ).first()

                if not chapter:
                    raise ValueError('Chapter not found.')

                for link_id in links:
                    link = session.query(Link).filter(Link.id == link_id).first()

                    if not link:
                        raise ValueError('Link not found.')

                    chapter_link = ChapterLink(user_id=self._owner.id, story_id=chapter.story_id,
                                               chapter_id=chapter_id, link_id=link_id, created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Link {link.title[:50]} associated with \
                                        chapter {chapter.title[:50]} by {self._owner.username}', created=datetime.now())

                    session.add(chapter_link)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return chapter

    def get_links_by_chapter_id(self, chapter_id: int) -> list[Type[Link]]:
        """Get all links associated with a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            return session.query(Link).join(ChapterLink, Link.id == ChapterLink.link_id).filter(
                ChapterLink.chapter_id == chapter_id, ChapterLink.user_id == self._owner.id
            ).all()

    def append_notes_to_chapter(self, chapter_id: int, notes: list) -> Type[Chapter]:
        """Append notes to a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter
        notes : list
            A list of note ids

        Returns
        -------
        Chapter
            The updated chapter object
        """

        with self._session as session:
            try:
                chapter = session.query(Chapter).filter(
                    Chapter.id == chapter_id, Chapter.user_id == self._owner.id
                ).first()

                if not chapter:
                    raise ValueError('Chapter not found.')

                for note_id in notes:
                    note = session.query(Note).filter(
                        Note.id == note_id, Note.user_id == self._owner.id
                    ).first()

                    if not note:
                        raise ValueError('Note not found.')

                    chapter_note = ChapterNote(user_id=self._owner.id, story_id=chapter.story_id, chapter_id=chapter_id,
                                               note_id=note_id, created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Note {note.title[:50]} associated with \
                                        chapter {chapter.title[:50]} by {self._owner.username}', created=datetime.now())

                    session.add(chapter_note)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return chapter

    def get_notes_by_chapter_id(self, chapter_id: int) -> list[Type[Note]]:
        """Get all notes associated with a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            return session.query(Note).join(ChapterNote, Note.id == ChapterNote.note_id).filter(
                ChapterNote.chapter_id == chapter_id, ChapterNote.user_id == self._owner.id
            ).all()


class CharacterController(BaseController):
    """Character controller encapsulates characters management functionality

    Attributes
    ----------
    _self : CharacterController
        The instance of the characters controller
    _owner : User
        The current user of the characters controller
    _session : Session
        The database session

    Methods
    -------
    create_character(title: str, first_name: str, middle_name: str, last_name: str, nickname: str, gender: str, \
                     sex: str, description: str, date_of_birth: str, date_of_death: str)
        Create a new character
    update_character(character_id: int, title: str, first_name: str, middle_name: str, last_name: str, nickname: str, \
                     gender: str, sex: str, description: str, date_of_birth: str, date_of_death: str)
        Update a character
    delete_character(character_id: int)
        Delete a character
    get_character_by_id(character_id: int)
        Get a character by id
    get_character_count()
        Get character count associated with a user
    get_all_characters()
        Get all characters associated with a user
    get_characters_page(page: int, per_page: int)
        Get a single page of characters from the database associated with a user
    get_character_count_by_story_id(story_id: int)
        Get character count associated with a story
    get_characters_by_story_id(story_id: int)
        Get a list of characters by story id
    get_characters_page_by_story_id(story_id: int, page: int, per_page: int)
        Get a single page of characters by story id
    search_characters(search: str)
        Search for characters by title, first name, middle name, last name, nickname, and description belonging to a \
        specific user
    search_characters_by_story_id(story_id: int, search: str)
        Search for characters by title, first name, middle name, last name, nickname, and description belonging to a \
        specific story
    create_relationship(parent_id: int, related_id: int, relationship_type: str, description: str,
                        start_date: str, end_date: str)
        Create a new character relationship
    update_relationship(relationship_id: int, parent_id: int, related_id: int, relationship_type: str,
                        description: str, start_date: str, end_date: str)
        Update a character relationship
    change_relationship_position(relationship_id: int, position: int)
        Set the position of a character relationship
    delete_relationship(relationship_id: int)
        Delete a character relationship
    get_relationship_by_id(relationship_id: int)
        Get a character relationship by id
    get_relationships_by_character_id(parent_id: int)
        Get character relationships by character id, from that character's perspective
    get_relationships_page_by_character_id(parent_id: int, page: int, per_page: int)
        Get a single page of character relationships by character id, from that character's perspective
    create_trait(character_id: int, name: str, magnitude: int)
        Create a new character trait
    update_trait(trait_id: int, name: str, magnitude: int)
        Update a character trait
    change_trait_position(trait_id: int, position: int)
        Set the position of a character trait
    delete_trait(trait_id: int)
        Delete a character trait
    get_trait_by_id(trait_id: int)
        Get a character trait by id
    get_traits_by_character_id(character_id: int)
        Get character traits by character id
    get_traits_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of character traits by character id
    append_events_to_character(character_id: int, events: list)
        Append events to a character
    get_events_by_character_id(character_id: int)
        Get all events associated with a character
    get_events_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of events associated with a character from the database
    append_links_to_character(character_id: int, links: list)
        Append links to a character
    get_links_by_character_id(character_id: int)
        Get all links associated with a character
    get_links_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of links associated with a character from the database
    append_notes_to_character(character_id: int, notes: list)
        Append notes to a character
    get_notes_by_character_id(character_id: int)
        Get all notes associated with a character
    get_notes_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of notes associated with a character from the database
    append_images_to_character(character_id: int, images: list)
        Append images to a character
    change_image_position(image_id: int, position: int)
        Set the position of an image related to a character
    change_image_default_status(image_id: int, is_default: bool)
        Set the default status of an image related to a character
    delete_image(image_id: int)
        Delete an image related to a character
    get_image_count_by_character_id(character_id: int)
        Get image count associated with a character
    get_images_by_character_id(character_id: int)
        Get all images associated with a character
    get_images_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of images associated with a character from the database
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_character(self, title: str = None, first_name: str = None, middle_name: str = None,
                         last_name: str = None, nickname: str = None, gender: str = None, sex: str = None,
                         date_of_birth: str = None, date_of_death: str = None, description: str = None) -> Character:
        """Create a new character

        Although all the attributes are technically optional, at least one of the following fields must be provided:
        title, first name, middle name, last name, or nickname.

        Parameters
        ----------
        title : str
            The title of the character, optional
        first_name : str
            The first name of the character, optional
        middle_name : str
            The middle name of the character, optional
        last_name : str
            The last name of the character, optional
        nickname : str
            The nickname of the character, optional
        gender: str
            The gender of the character, optional
        sex: str
            The sex of the character, optional
        date_of_birth: str
            The date of birth of the character, optional
        date_of_death: str
            The date of death of the character, optional
        description
            The description of the character, optional

        Returns
        -------
        Character
            The new character object
        """

        with self._session as session:
            try:
                if not title and not first_name and not last_name and not middle_name and not nickname:
                    raise ValueError('At least one of the following fields must be provided: title, first name, \
                                      middle name, last name, nickname.')

                created = datetime.now()
                modified = created
                character = Character(user_id=self._owner.id, title=title, first_name=first_name,
                                      middle_name=middle_name, last_name=last_name, nickname=nickname, gender=gender,
                                      sex=sex, date_of_birth=date_of_birth, date_of_death=date_of_death,
                                      description=description, created=created, modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'{character.__str__} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(character)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def update_character(self, character_id: int = None, title: str = None, first_name: str = None,
                         middle_name: str = None, last_name: str = None, nickname: str = None, gender: str = None,
                         sex: str = None, date_of_birth: str = None, date_of_death: str = None,
                         description: str = None) -> Type[Character]:
        """Update a character

        Parameters
        ----------
        character_id : int
            The id of the character to update
        title : str
            The title of the character
        first_name : str
            The first name of the character
        middle_name : str
            The middle name of the character
        last_name : str
            The last name of the character
        nickname : str
            The nickname of the character
        gender : str
            The gender of the character
        sex : str
            The sex of the character
        date_of_birth : str
            The date of birth of the character
        date_of_death : str
            The date of death of the character
        description : str
            The description of the character

        Returns
        -------
        Character
            The updated character object
        """

        with self._session as session:
            try:
                character = session.query(Character).filter(
                    Character.id == character_id, Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                character.title = title
                character.first_name = first_name
                character.middle_name = middle_name
                character.last_name = last_name
                character.nickname = nickname
                character.gender = gender
                character.sex = sex
                character.date_of_birth = date_of_birth
                character.date_of_death = date_of_death
                character.description = description
                character.modified = datetime.now()

                activity = Activity(user_id=self._owner.id, summary=f'{character.__str__} updated by \
                    {self._owner.username}', created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def delete_character(self, character_id: int) -> bool:
        """Delete a character

        Character objects are even more complex than Chapter objects. Each Character can have an arbitrary number of
        Link, Note, and Image objects associated with it. Additionally, each Character has an arbitrary number of
        character relationships, an arbitrary number of character traits, and an arbitrary number of events associated
        with it. Before the Character can be deleted, the links, notes, images, relationships, traits, and events
        associated with it must be deleted. The Characters do not possess a position scheme, so there is no need to
        adjust the position of sibling characters. Finally, the Character is deleted.

        Parameters
        ----------
        character_id : int
            The id of the character to delete

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                character = session.query(Character).filter(
                    Character.id == character_id, Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                for link in character.links:
                    session.query(LinkNote).filter(
                        LinkNote.link_id == link.link_id, LinkNote.user_id == self._owner.id
                    ).delete()
                    session.query(Link).filter(
                        Link.id == link.link_id, Link.user_id == self._owner.id
                    ).delete()
                    session.delete(link)

                for note in character.notes:
                    session.query(LinkNote).filter(
                        LinkNote.note_id == note.note_id, LinkNote.user_id == self._owner.id
                    ).delete()
                    session.query(Note).filter(
                        Note.id == note.note_id, Note.user_id == self._owner.id
                    ).delete()
                    session.delete(note)

                for image in character.images:
                    session.query(Image).filter(
                        Image.id == image.id, Image.user_id == self._owner.id
                    ).delete()
                    session.delete(image)

                for character_relationship in character.character_relationships:
                    session.delete(character_relationship)

                for trait in character.traits:
                    session.delete(trait)

                for event in character.events:
                    session.query(CharacterEvent).filter(
                        CharacterEvent.event_id == event.id, CharacterEvent.user_id == self._owner.id
                    ).delete()

                activity = Activity(user_id=self._owner.id, summary=f'Character {character.__str__} deleted by \
                    {self._owner.username}', created=datetime.now())

                session.delete(character)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_character_by_id(self, character_id: int) -> Type[Character] | None:
        """Get a character by id

        Parameters
        ----------
        character_id : int
            The id of the character to get

        Returns
        -------
        Type[Character] | None
            The character if found, otherwise None
        """

        with self._session as session:
            character = session.query(Character).filter(
                Character.id == character_id, Character.user_id == self._owner.id
            ).first()
            return character if character else None

    def get_character_count(self) -> int:
        """Get character count associated with a user

        Returns
        -------
        int
            The count of characters associated with the user
        """

        with self._session as session:
            return session.query(func.count(Character.id)).filter(
                Character.user_id == self._owner.id
            ).scalar()

    def get_all_characters(self) -> list:
        """Get all characters associated with a user

        Returns
        -------
        list
            The list of characters associated with the user
        """

        with self._session as session:
            return session.query(Character).filter(
                Character.user_id == self._owner.id
            ).all()

    def get_characters_page(self, page: int, per_page: int) -> list:
        """Get a single page of characters from the database associated with a user

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of characters associated with the user
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Character).filter(
                Character.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def get_character_count_by_story_id(self, story_id: int) -> int:
        """Get character count associated with a story

        The characters and stories are associated in the CharacterStory table.

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        int
            The count of characters associated with the story
        """

        with self._session as session:
            return session.query(func.count(CharacterStory.character_id)).filter(
                CharacterStory.story_id == story_id, CharacterStory.user_id == self._owner.id
            ).scalar()

    def get_characters_by_story_id(self, story_id: int) -> list:
        """Get characters by story id

        The characters and stories are associated in the CharacterStory table.

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            The list of characters associated with the story
        """

        with self._session as session:
            for character_story in session.query(CharacterStory).filter(
                    CharacterStory.story_id == story_id, CharacterStory.user_id == self._owner.id
            ).all():
                yield session.query(Character).filter(
                    Character.id == character_story.character_id, Character.user_id == self._owner.id
                ).first()

    def get_characters_page_by_story_id(self, story_id: int, page: int, per_page: int) -> list:
        """Get a single page of characters by story id

        The characters and stories are associated in the CharacterStory table.

        Parameters
        ----------
        story_id : int
            The id of the story
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of characters associated with the story
        """

        with self._session as session:
            offset = (page - 1) * per_page
            for character_story in session.query(CharacterStory).filter(
                    CharacterStory.story_id == story_id, CharacterStory.user_id == self._owner.id
            ).offset(offset).limit(per_page).all():
                yield session.query(Character).filter(
                    Character.id == character_story.character_id, Character.user_id == self._owner.id
                ).first()

    def search_characters(self, search: str) -> list:
        """Search for characters by title, first name, middle name, last name, nickname, and description belonging to \
        a specific user

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            The list of characters associated with the user
        """

        with self._session as session:
            return session.query(Character).filter(
                or_(Character.title.like(f'%{search}%'), Character.first_name.like(f'%{search}%'),
                    Character.middle_name.like(f'%{search}%'), Character.last_name.like(f'%{search}%'),
                    Character.nickname.like(f'%{search}%'), Character.description.like(f'%{search}%')),
                Character.user_id == self._owner.id
            ).all()

    def search_characters_by_story_id(self, story_id: int, search: str) -> list | None:
        """Search for characters by title, first name, middle name, last name, nickname, and description belonging to \
        a specific story

        Parameters
        ----------
        story_id : int
            The id of the story
        search : str
            The search string

        Returns
        -------
        list | None
            The list of characters associated with the story or None if none are found
        """

        with self._session as session:
            return session.query(Character).join(CharacterStory, Character.id == CharacterStory.character_id).filter(
                or_(Character.title.like(f'%{search}%'), Character.first_name.like(f'%{search}%'),
                    Character.middle_name.like(f'%{search}%'), Character.last_name.like(f'%{search}%'),
                    Character.nickname.like(f'%{search}%'), Character.description.like(f'%{search}%')),
                CharacterStory.story_id == story_id, CharacterStory.user_id == self._owner.id
            ).all()

    def create_relationship(self, parent_id: int, related_id: int, relationship_type: str, description: str = None,
                            start_date: str = None, end_date: str = None) -> CharacterRelationship:
        """Create a new character relationship

        There are many relationships for each character, and the linking class, CharacterRelationship, is used to
        define the relationship between two characters. The relationship type is defined in the
        CharacterRelationshipTypes and elaborated upon in the description. Before insertion, in order to determine
        the correct position, the highest position among sibling CharacterRelationship objects is first determined.
        The new position is set to the highest position plus one. The created and modified fields are set to the
        current date and time. Finally, insert the new CharacterRelationship object into the database.

        Parameters
        ----------
        parent_id : int
            The id of the parent character
        related_id : int
            The id of the related character
        relationship_type : str
            The type of relationship
        description : str
            The description of the relationship, optional
        start_date : str
            The start date of the relationship, optional
        end_date : str
            The end date of the relationship, optional

        Returns
        -------
        CharacterRelationship
            The new character relationship object
        """

        with self._session as session:
            try:
                if not parent_id or not related_id:
                    raise ValueError('Both parent and related character ids must be provided.')

                if parent_id == related_id:
                    raise ValueError('Parent and related character ids must be different.')

                parent = session.query(Character).filter(
                    Character.id == parent_id, Character.user_id == self._owner.id
                ).first()

                if not parent:
                    raise ValueError('Parent character not found.')

                related = session.query(Character).filter(
                    Character.id == related_id, Character.user_id == self._owner.id
                ).first()

                if not related:
                    raise ValueError('Related character not found.')

                position = session.query(func.max(CharacterRelationship.position)).filter(
                    CharacterRelationship.parent_id == parent_id,
                    CharacterRelationship.user_id == self._owner.id
                ).scalar()

                position = 1 if not position else position + 1
                created = datetime.now()
                modified = created
                character_relationship = CharacterRelationship(user_id=self._owner.id, parent_id=parent.id,
                                                               related_id=related.id, position=position,
                                                               relationship_type=relationship_type,
                                                               description=description, start_date=start_date,
                                                               end_date=end_date, created=created,
                                                               modified=modified)

                activity = Activity(user_id=self._owner.id, summary=f'Character relationship created by \
                                        {self._owner.username}', created=datetime.now())

                session.add(character_relationship)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_relationship

    def update_relationship(self, relationship_id: int, parent_id: int, related_id: int, relationship_type: str,
                            description: str = None, start_date: str = None, end_date: str = None) \
            -> Type[CharacterRelationship]:
        """Update a character relationship

        Parameters
        ----------
        relationship_id : int
            The id of the relationship to update
        parent_id : int
            The id of the parent character
        related_id : int
            The id of the related character
        relationship_type : str
            The type of relationship
        description : str
            The description of the relationship, optional
        start_date : str
            The start date of the relationship, optional
        end_date : str
            The end date of the relationship, optional

        Returns
        -------
        CharacterRelationship
            The updated character relationship object
        """

        with self._session as session:
            try:
                character_relationship = session.query(CharacterRelationship).filter(
                    CharacterRelationship.id == relationship_id, CharacterRelationship.user_id == self._owner.id
                ).first()

                if not character_relationship:
                    raise ValueError('Character relationship not found.')

                character_relationship.parent_id = parent_id
                character_relationship.related_id = related_id
                character_relationship.relationship_type = relationship_type
                character_relationship.description = description
                character_relationship.start_date = start_date
                character_relationship.end_date = end_date
                character_relationship.modified = datetime.now()

                activity = Activity(user_id=self._owner.id, summary=f'Character relationship updated by \
                                    {self._owner.username}', created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_relationship

    def change_relationship_position(self, relationship_id: int, position: int) -> Type[CharacterRelationship]:
        """Set the position of a character relationship

        First, determine whether the new position is closer to 1 or further from 1. If closer to one, get all sibling
        CharacterRelationship objects with positions greater than or equal to the new position but less than the current
        position, and increment those position values by 1. If the target position is further away from 1 than the
        current position, get all sibling CharacterRelationship objects with positions greater than the current position
        but less than or equal to the new position, and decrement those position values by 1. Finally, set the position
        of the target CharacterRelationship object to the new position. Return the new position.

        Parameters
        ----------
        relationship_id : int
            The id of the relationship to update
        position : int
            The new position of the relationship

        Returns
        -------
        CharacterRelationship
            The updated character relationship object
        """

        with self._session as session:
            try:
                character_relationship = session.query(CharacterRelationship).filter(
                    CharacterRelationship.id == relationship_id, CharacterRelationship.user_id == self._owner.id
                ).first()

                if not character_relationship:
                    raise ValueError('Character relationship not found.')

                if position < 1:
                    raise ValueError('Position must be greater than 0.')

                if position == character_relationship.position:
                    return character_relationship

                if position < character_relationship.position:
                    for sibling in session.query(CharacterRelationship).filter(
                        CharacterRelationship.parent_id == character_relationship.parent_id,
                        CharacterRelationship.position >= position,
                        CharacterRelationship.position < character_relationship.position,
                        CharacterRelationship.user_id == self._owner.id
                    ).all():
                        sibling.position += 1

                else:
                    for sibling in session.query(CharacterRelationship).filter(
                        CharacterRelationship.parent_id == character_relationship.parent_id,
                        CharacterRelationship.position > character_relationship.position,
                        CharacterRelationship.position <= position, CharacterRelationship.user_id == self._owner.id
                    ).all():
                        sibling.position -= 1

                character_relationship.position = position
                character_relationship.modified = datetime.now()

                activity = Activity(user_id=self._owner.id, summary=f'Character relationship position updated by \
                                    {self._owner.username}', created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_relationship

    def delete_relationship(self, relationship_id: int) -> bool:
        """Delete a character relationship

        Before deleting the CharacterRelationship object, all sibling objects with positions higher than the current
        position are decremented by one. The activity is then logged and the CharacterRelationship object is deleted.

        Parameters
        ----------
        relationship_id : int
            The id of the relationship to delete

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                character_relationship = session.query(CharacterRelationship).filter(
                    CharacterRelationship.id == relationship_id, CharacterRelationship.user_id == self._owner.id
                ).first()

                if not character_relationship:
                    raise ValueError('Character relationship not found.')

                for sibling in session.query(CharacterRelationship).filter(
                    CharacterRelationship.parent_id == character_relationship.parent_id,
                    CharacterRelationship.position > character_relationship.position,
                    CharacterRelationship.user_id == self._owner.id
                ).all():
                    sibling.position -= 1

                activity = Activity(user_id=self._owner.id, summary=f'Character relationship deleted by \
                                    {self._owner.username}', created=datetime.now())

                session.delete(character_relationship)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_relationship_by_id(self, relationship_id: int) -> Type[CharacterRelationship] | None:
        """Get a character relationship by id

        Parameters
        ----------
        relationship_id : int
            The id of the relationship to get

        Returns
        -------
        Type[CharacterRelationship] | None
            The character relationship if found, otherwise None
        """

        with self._session as session:
            character_relationship = session.query(CharacterRelationship).filter(
                CharacterRelationship.id == relationship_id, CharacterRelationship.user_id == self._owner.id
            ).first()
            return character_relationship if character_relationship else None

    def get_relationships_by_character_id(self, parent_id: int) -> list:
        """Get character relationships by character id, from that character's perspective

        Parameters
        ----------
        parent_id : int
            The id of the character

        Returns
        -------
        list
            The list of character relationships
        """

        with self._session as session:
            return session.query(CharacterRelationship).filter(
                CharacterRelationship.parent_id == parent_id, CharacterRelationship.user_id == self._owner.id
            ).all()

    def get_relationships_page_by_character_id(self, parent_id: int, page: int, per_page: int) -> list:
        """Get a single page of character relationships by character id, from that character's perspective

        Parameters
        ----------
        parent_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of character relationships
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(CharacterRelationship).filter(
                CharacterRelationship.parent_id == parent_id, CharacterRelationship.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def create_trait(self, character_id: int, name: str, magnitude: int) -> CharacterTrait:
        """Create a new character trait

        The position of the new trait must be determined by first finding the highest existing position among siblings,
        if any. Any other CharacterTrait objects associated with the same character are those siblings.

        Parameters
        ----------
        character_id : int
            The id of the character
        name : str
            The name of the trait
        magnitude : int
            The magnitude of the trait

        Returns
        -------
        CharacterTrait
            The new character trait object
        """

        with self._session as session:
            try:
                if not character_id or not name or not magnitude:
                    raise ValueError('Character id, name, and magnitude must be provided.')

                character = session.query(Character).filter(
                    Character.id == character_id, Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                position = session.query(func.max(CharacterTrait.position)).filter(
                    CharacterTrait.character_id == character_id, CharacterTrait.user_id == self._owner.id
                ).scalar()

                position = 1 if not position else position + 1
                created = datetime.now()
                modified = created
                character_trait = CharacterTrait(user_id=self._owner.id, character_id=character_id, position=position,
                                                 name=name, magnitude=magnitude, created=created, modified=modified)

                activity = Activity(user_id=self._owner.id, summary=f'Character trait {name} \
                                    created by {self._owner.username} for "{character.__str__}"',
                                    created=datetime.now())

                session.add(character_trait)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_trait

    def update_trait(self, trait_id: int, name: str, magnitude: int) -> Type[CharacterTrait]:
        """Update a character trait

        Parameters
        ----------
        trait_id : int
            The id of the trait to update
        name : str
            The name of the trait
        magnitude : int
            The magnitude of the trait

        Returns
        -------
        CharacterTrait
            The updated character trait object
        """

        with self._session as session:
            try:
                character_trait = session.query(CharacterTrait).filter(
                    CharacterTrait.id == trait_id, CharacterTrait.user_id == self._owner.id
                ).first()

                if not character_trait:
                    raise ValueError('Character trait not found.')

                character_trait.name = name
                character_trait.magnitude = magnitude
                character_trait.modified = datetime.now()

                activity = Activity(user_id=self._owner.id, summary=f'Character trait {character_trait.__str__} \
                                    updated by {self._owner.username}', created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_trait

    def change_trait_position(self, trait_id: int, position: int) -> Type[CharacterTrait]:
        """Set the position of a character trait

        First, determine whether the new position is closer to 1 or further from 1. If closer to one, get all sibling
        CharacterTraits with positions greater than or equal to the new position but less than the current position, and
        increment those position values by 1. If the target position is further away from 1 than the current position,
        get all sibling CharacterTraits with positions greater than the current position but less than or equal to the
        new position, and decrement those position values by 1. Finally, set the position of the target chapter to the
        new position. Return the new position.

        Parameters
        ----------
        trait_id : int
            The id of the trait to update
        position : int
            The position of the trait

        Returns
        -------
        CharacterTrait
            The updated character trait object
        """

        with self._session as session:
            try:
                character_trait = session.query(CharacterTrait).filter(
                    CharacterTrait.id == trait_id, CharacterTrait.user_id == self._owner.id
                ).first()

                if not character_trait:
                    raise ValueError('Character trait not found.')

                if position < 1:
                    raise ValueError('Position must be greater than 0.')

                highest_position = session.query(func.max(CharacterTrait.position)).filter(
                    CharacterTrait.character_id == character_trait.character_id,
                    CharacterTrait.user_id == self._owner.id
                ).scalar()

                if position > highest_position:
                    raise ValueError(f'Position must be less than or equal to {highest_position}.')

                if position == character_trait.position:
                    return character_trait.position

                if position < character_trait.position:
                    siblings = session.query(CharacterTrait).filter(
                        CharacterTrait.character_id == character_trait.character_id,
                        CharacterTrait.position >= position, CharacterTrait.user_id == self._owner.id,
                        CharacterTrait.position < character_trait.position
                    ).all()

                    for sibling in siblings:
                        sibling.position += 1
                        sibling.created = datetime.strptime(str(sibling.created), datetime_format)
                        sibling.modified = datetime.now()

                else:
                    siblings = session.query(CharacterTrait).filter(
                        CharacterTrait.character_id == character_trait.character_id,
                        CharacterTrait.position > character_trait.position,
                        CharacterTrait.position <= position, CharacterTrait.user_id == self._owner.id
                    ).all()

                    for sibling in siblings:
                        sibling.position -= 1
                        sibling.created = datetime.strptime(str(sibling.created), datetime_format)
                        sibling.modified = datetime.now()

                character_trait.modified = datetime.now()

                activity = Activity(user_id=self._owner.id, summary=f'Character trait {character_trait.__str__} \
                                    position changed by {self._owner.username}', created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_trait

    def delete_trait(self, trait_id: int) -> bool:
        """Delete a character trait

        When a trait is deleted, all sibling traits having a higher position than the deleted trait must have their
        positions each decremented by 1. The activity is then logged and the CharacterTrait object is deleted.

        Parameters
        ----------
        trait_id : int
            The id of the trait to delete

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                character_trait = session.query(CharacterTrait).filter(
                    CharacterTrait.id == trait_id, CharacterTrait.user_id == self._owner.id
                ).first()

                if not character_trait:
                    raise ValueError('Character trait not found.')

                for sibling in session.query(CharacterTrait).filter(
                    CharacterTrait.character_id == character_trait.character_id,
                    CharacterTrait.position > character_trait.position, CharacterTrait.user_id == self._owner.id
                ).all():
                    sibling.position -= 1
                    sibling.created = datetime.strptime(str(sibling.created), datetime_format)
                    sibling.modified = datetime.now()

                activity = Activity(user_id=self._owner.id, summary=f'Character trait {character_trait.__str__} \
                                    deleted by {self._owner.username}', created=datetime.now())

                session.delete(character_trait)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_trait_by_id(self, trait_id: int) -> Type[CharacterTrait] | None:
        """Get a character trait by id

        Parameters
        ----------
        trait_id : int
            The id of the trait to get

        Returns
        -------
        Type[CharacterTrait] | None
            The character trait if found, otherwise None
        """

        with self._session as session:
            character_trait = session.query(CharacterTrait).filter(
                CharacterTrait.id == trait_id, CharacterTrait.user_id == self._owner.id
            ).first()
            return character_trait if character_trait else None

    def get_traits_by_character_id(self, character_id: int) -> list:
        """Get character traits by character id

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            The list of character traits
        """

        with self._session as session:
            return session.query(CharacterTrait).filter(
                CharacterTrait.character_id == character_id, CharacterTrait.user_id == self._owner.id
            ).all()

    def get_traits_page_by_character_id(self, character_id: int, page: int, per_page: int) -> list:
        """Get a single page of character traits by character id

        Parameters
        ----------
        character_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of character traits
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(CharacterTrait).filter(
                CharacterTrait.character_id == character_id, CharacterTrait.user_id == self._owner.id
            ).offset(
                offset).limit(per_page).all()

    def append_events_to_character(self, character_id: int, events: list) -> Type[Character]:
        """Append events to a character

        Parameters
        ----------
        character_id : int
            The id of the character
        events : list
            A list of event ids

        Returns
        -------
        Character
            The updated character object
        """

        with self._session as session:
            try:
                character = session.query(Character).filter(
                    Character.id == character_id, Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                for event_id in events:
                    event = session.query(Event).filter(
                        Event.id == event_id, Event.user_id == self._owner.id
                    ).first()

                    if not event:
                        raise ValueError('Event not found.')

                    character_event = CharacterEvent(user_id=self._owner.id, character_id=character_id,
                                                     event_id=event_id, created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Event {event.title[:50]} associated with \
                                        {character.__str__} by {self._owner.username}', created=datetime.now())

                    session.add(character_event)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def get_events_by_character_id(self, character_id: int) -> list:
        """Get all events associated with a character

        Using the association of the CharacterEvent table, get all events from teh Event table associated with a
        character.

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            The list of events
        """

        with self._session as session:
            for character_event in session.query(CharacterEvent).filter(
                CharacterEvent.character_id == character_id, CharacterEvent.user_id == self._owner.id
            ).all():
                yield session.query(Event).filter(
                    Event.id == character_event.event_id, Event.user_id == self._owner.id
                ).first()

    def get_events_page_by_character_id(self, character_id: int, page: int, per_page: int) -> list:
        """Get a single page of events associated with a character from the database

        Parameters
        ----------
        character_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of events
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(CharacterEvent).filter(
                CharacterEvent.character_id == character_id, CharacterEvent.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_links_to_character(self, character_id: int, links: list) -> Type[Character]:
        """Append links to a character

        Parameters
        ----------
        character_id : int
            The id of the character
        links : list
            A list of link ids

        Returns
        -------
        Character
            The updated character object
        """

        with self._session as session:
            try:
                character = session.query(Character).filter(
                    Character.id == character_id, Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                for link_id in links:
                    link = session.query(Link).filter(
                        Link.id == link_id, Link.user_id == self._owner.id
                    ).first()

                    if not link:
                        raise ValueError('Link not found.')

                    character_link = CharacterLink(user_id=self._owner.id, character_id=character_id, link_id=link_id,
                                                   created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Link {link.title[:50]} associated with \
                                        {character.__str__} by {self._owner.username}', created=datetime.now())

                    session.add(character_link)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def get_links_by_character_id(self, character_id: int) -> list:
        """Get all links associated with a character

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            The list of links
        """

        with self._session as session:
            for character_link in session.query(CharacterLink).filter(
                CharacterLink.character_id == character_id, CharacterLink.user_id == self._owner.id
            ).all():
                yield session.query(Link).filter(
                    Link.id == character_link.link_id, Link.user_id == self._owner.id
                ).first()

    def get_links_page_by_character_id(self, character_id: int, page: int, per_page: int) -> list:
        """Get a single page of links associated with a character from the database

        Parameters
        ----------
        character_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of links
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(CharacterLink).filter(
                CharacterLink.character_id == character_id, CharacterLink.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_notes_to_character(self, character_id: int, notes: list) -> Type[Character]:
        """Append notes to a character

        Parameters
        ----------
        character_id : int
            The id of the character
        notes : list
            A list of note ids

        Returns
        -------
        Character
            The updated character object
        """

        with self._session as session:
            try:
                character = session.query(Character).filter(
                    Character.id == character_id, Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                for note_id in notes:
                    note = session.query(Note).filter(
                        Note.id == note_id, Note.user_id == self._owner.id
                    ).first()

                    if not note:
                        raise ValueError('Note not found.')

                    character_note = CharacterNote(user_id=self._owner.id, character_id=character_id, note_id=note_id,
                                                   created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Note {note.title[:50]} associated with \
                                        {character.__str__} by {self._owner.username}', created=datetime.now())

                    session.add(character_note)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def get_notes_by_character_id(self, character_id: int) -> list:
        """Get all notes associated with a character

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            The list of notes
        """

        with self._session as session:
            for character_note in session.query(CharacterNote).filter(
                CharacterNote.character_id == character_id, CharacterNote.user_id == self._owner.id
            ).all():
                yield session.query(Note).filter(
                    Note.id == character_note.note_id, Note.user_id == self._owner.id
                ).first()

    def get_notes_page_by_character_id(self, character_id: int, page: int, per_page: int) -> list:
        """Get a single page of notes associated with a character from the database

        Parameters
        ----------
        character_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of notes
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(CharacterNote).filter(
                CharacterNote.character_id == character_id, CharacterNote.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_images_to_character(self, character_id: int, images: list) -> Type[Character]:
        """Append images to a character

        As images are appended to the character, before each image is appended, the highest position among other images
        associated with this object is found and the new image is appended with a position one higher than the highest
        position.

        Parameters
        ----------
        character_id : int
            The id of the character
        images : list
            A list of image ids

        Returns
        -------
        Character
            The updated character object
        """

        with self._session as session:
            try:
                character = session.query(Character).filter(
                    Character.id == character_id, Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                for image_id in images:
                    image = session.query(Image).filter(
                        Image.id == image_id, Image.user_id == self._owner.id
                    ).first()

                    if not image:
                        raise ValueError('Image not found.')

                    position = session.query(func.max(CharacterImage.position)).filter(
                        CharacterImage.character_id == character_id, CharacterImage.user_id == self._owner.id
                    ).scalar()

                    position = 1 if not position else position + 1
                    is_default = False
                    created = datetime.now()
                    modified = created
                    character_image = CharacterImage(user_id=self._owner.id, character_id=character_id,
                                                     image_id=image_id, position=position, is_default=is_default,
                                                     created=created, modified=modified)

                    activity = Activity(user_id=self._owner.id, summary=f'Image {image.filename[:50]} associated with \
                                        character {str(character)[:50]} by {self._owner.username}',
                                        created=datetime.now())

                    session.add(character_image)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def change_image_position(self, image_id: int, position: int) -> Type[CharacterImage]:
        """Set the position of a character image

        First, determine whether the new position is closer to 1 or further from 1. If closer to one, get all sibling
        CharacterImage objects with positions greater than or equal to the new position but less than the current
        position, and increment those position values by 1. If the target position is further away from 1 than the
        current position, get all sibling CharacterImage objects with positions greater than the current position but
        less than or equal to the new position, and decrement those position values by 1. Finally, set the position of
        the target CharacterImage object to the new position. Return the new position.

        Parameters
        ----------
        image_id : int
            The id of the image to update
        position : int
            The position of the image

        Returns
        -------
        CharacterImage
            The updated character image object
        """

        with self._session as session:
            try:
                character_image = session.query(CharacterImage).filter(
                    CharacterImage.id == image_id, CharacterImage.user_id == self._owner.id
                ).first()

                if not character_image:
                    raise ValueError('Character image not found.')

                if position < 1:
                    raise ValueError('Position must be greater than 0.')

                highest_position = session.query(func.max(CharacterImage.position)).filter(
                    CharacterImage.character_id == character_image.character_id,
                    CharacterImage.user_id == self._owner.id
                ).scalar()

                if position > highest_position:
                    raise ValueError(f'Position must be less than or equal to {highest_position}.')

                if position == character_image.position:
                    return character_image.position

                if position < character_image.position:
                    siblings = session.query(CharacterImage).filter(
                        CharacterImage.character_id == character_image.character_id,
                        CharacterImage.position >= position, CharacterImage.user_id == self._owner.id,
                        CharacterImage.position < character_image.position
                    ).all()

                    for sibling in siblings:
                        sibling.position += 1
                        sibling.created = datetime.strptime(str(sibling.created), datetime_format)
                        sibling.modified = datetime.now()

                else:
                    siblings = session.query(CharacterImage).filter(
                        CharacterImage.character_id == character_image.character_id,
                        CharacterImage.position > character_image.position,
                        CharacterImage.position <= position, CharacterImage.user_id == self._owner.id
                    ).all()

                    for sibling in siblings:
                        sibling.position -= 1
                        sibling.created = datetime.strptime(str(sibling.created), datetime_format)
                        sibling.modified = datetime.now()

                character_image.position = position
                character_image.modified = datetime.now()

                activity = Activity(user_id=self._owner.id, summary=f'Character image {character_image.__str__} \
                                    position changed by {self._owner.username}', created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_image

    def change_image_default_status(self, image_id: int, is_default: bool) -> Type[CharacterImage]:
        """Set the default status of a character image

        If changing the value from true to false, it is straightforward - make the value change and save the object.
        However, if the value is changed from false to true, then before saving that new value in the object, the same
        attribute must first be set to false in all sibling CharacterImage objects. This is because only one image can
        be the default image for a character. The activity is then logged and the CharacterImage object is saved.

        Parameters
        ----------
        image_id : int
            The id of the image to update
        is_default : bool
            The default status of the image

        Returns
        -------
        CharacterImage
            The updated character image object
        """

        with self._session as session:
            try:
                character_image = session.query(CharacterImage).filter(
                    CharacterImage.id == image_id, CharacterImage.user_id == self._owner.id
                ).first()

                if not character_image:
                    raise ValueError('Character image not found.')

                if is_default == character_image.is_default:
                    return character_image

                if is_default:
                    for sibling in session.query(CharacterImage).filter(
                        CharacterImage.character_id == character_image.character_id,
                        CharacterImage.user_id == self._owner.id
                    ).all():
                        sibling.is_default = False
                        sibling.modified = datetime.now()

                character_image.is_default = is_default
                character_image.modified = datetime.now()

                activity = Activity(user_id=self._owner.id, summary=f'Character image {character_image.__str__} \
                                    default status changed by {self._owner.username}', created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_image

    def delete_image(self, image_id: int) -> bool:
        """Delete a character image

        When an image is deleted, all sibling images having a higher position than the deleted image must have their
        positions each decremented by 1. The activity is then logged and the CharacterImage object is deleted. The
        Image object is also deleted.

        Parameters
        ----------
        image_id : int
            The id of the image to delete

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                character_image = session.query(CharacterImage).filter(
                    CharacterImage.id == image_id, CharacterImage.user_id == self._owner.id
                ).first()
                image = session.query(Image).filter(
                    Image.id == character_image.image_id, Image.user_id == self._owner.id
                ).first()

                if not character_image:
                    raise ValueError('Character image not found.')

                for sibling in session.query(CharacterImage).filter(
                    CharacterImage.character_id == character_image.character_id,
                    CharacterImage.position > character_image.position, CharacterImage.user_id == self._owner.id
                ).all():
                    sibling.position -= 1
                    sibling.created = datetime.strptime(str(sibling.created), datetime_format)
                    sibling.modified = datetime.now()

                activity = Activity(user_id=self._owner.id, summary=f'Character image {image.caption[:50]} \
                                    deleted by {self._owner.username}', created=datetime.now())

                session.delete(character_image)
                session.delete(image)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_image_count_by_character_id(self, character_id: int) -> int:
        """Get image count associated with a character

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        int
            The count of images
        """

        with self._session as session:
            return session.query(func.count(CharacterImage.id)).filter(
                CharacterImage.character_id == character_id, CharacterImage.user_id == self._owner.id
            ).scalar()

    def get_images_by_character_id(self, character_id: int) -> list:
        """Get all images associated with a character

        The images will be returned in the order of their position. A yield is used to return the images one at a time.

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            The list of images
        """

        with self._session as session:
            for character_image in session.query(CharacterImage).filter(
                CharacterImage.character_id == character_id, CharacterImage.user_id == self._owner.id
            ).order_by(CharacterImage.position).all():
                yield session.query(Image).filter(
                    Image.id == character_image.image_id, Image.user_id == self._owner.id
                ).first()

    def get_images_page_by_character_id(self, character_id: int, page: int, per_page: int) -> list:
        """Get a single page of images associated with a character from the database

        The images will be returned in the order of their position. A yield is used to return the images one at a time.

        Parameters
        ----------
        character_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of images
        """

        with self._session as session:
            offset = (page - 1) * per_page
            for character_image in session.query(CharacterImage).filter(
                CharacterImage.character_id == character_id, CharacterImage.user_id == self._owner.id
            ).order_by(CharacterImage.position).offset(offset).limit(per_page).all():
                yield session.query(Image).filter(
                    Image.id == character_image.image_id, Image.user_id == self._owner.id
                ).first()


class EventController(BaseController):
    """Event controller encapsulates event management functionality

    Attributes
    ----------
    _self : EventController
        The instance of the event controller
    _owner : User
        The current user of the event controller
    _session : Session
        The database session

    Methods
    -------
    create_event(title: str, description: str, start_datetime: str, end_datetime: str)
        Create a new event
    update_event(event_id: int, title: str, description: str, start_datetime: str, end_datetime: str)
        Update an event
    delete_event(event_id: int)
        Delete an event
    get_events_by_user_id(owner_id: int)
        Get all events associated with an owner
    get_events_page_by_user_id(owner_id: int, page: int, per_page: int)
        Get a single page of events associated with an owner from the database
    append_characters_to_event(event_id: int, characters: list)
        Append characters to an event
    get_characters_by_event_id(event_id: int)
        Get all characters associated with an event
    append_locations_to_event(event_id: int, locations: list)
        Append locations to an event
    get_locations_by_event_id(event_id: int)
        Get all locations associated with an event
    append_links_to_event(event_id: int, links: list)
        Append links to an event
    get_links_by_event_id(event_id: int)
        Get all links associated with an event
    get_links_page_by_event_id(event_id: int, page: int, per_page: int)
        Get a single page of links associated with an event from the database
    append_notes_to_event(event_id: int, notes: list)
        Append notes to an event
    get_notes_by_event_id(event_id: int)
        Get all notes associated with an event
    get_notes_page_by_event_id(event_id: int, page: int, per_page: int)
        Get a single page of notes associated with an event from the database
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_event(self, title: str, description: str = None, start_datetime: str = None,
                     end_datetime: str = None) -> Event:
        """Create a new event

        Parameters
        ----------
        title : str
            The title of the event
        description : str
            The description of the event
        start_datetime : str
            The start date and time of the event
        end_datetime : str
            The end date and time of the event

        Returns
        -------
        Event
            The new event object
        """

        with self._session as session:
            try:
                created = datetime.now()
                modified = created

                event = Event(user_id=self._owner.id, title=title, description=description,
                              start_datetime=start_datetime, end_datetime=end_datetime, created=created,
                              modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Event {event.title[:50]} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(event)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return event

    def update_event(self, event_id: int, title: str, description: str, start_datetime: str,
                     end_datetime: str) -> Type[Event]:
        """Update an event

        Parameters
        ----------
        event_id : int
            The id of the event
        title : str
            The title of the event
        description : str
            The description of the event
        start_datetime : str
            The start date and time of the event
        end_datetime : str
            The end date and time of the event

        Returns
        -------
        Event
            The updated event object
        """

        with self._session as session:
            try:
                event = session.query(Event).filter(Event.id == event_id).first()

                if not event:
                    raise ValueError('Event not found.')

                event.title = title
                event.description = description
                event.start_datetime = start_datetime
                event.end_datetime = end_datetime
                event.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Event {event.id} updated by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return event

    def delete_event(self, event_id: int) -> bool:
        """Delete an event

        Parameters
        ----------
        event_id : int
            The id of the event

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                event = session.query(Event).filter(
                    Event.id == event_id, Event.user_id == self._owner.id
                ).first()

                if not event:
                    raise ValueError('Event not found.')

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Event {event.id} deleted by {self._owner.username}',
                                    created=datetime.now())

                session.delete(event)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_events_by_user_id(self, owner_id: int) -> list:
        """Get all events associated with an owner

        Parameters
        ----------
        owner_id : int
            The id of the owner

        Returns
        -------
        list
            A list of event objects
        """

        with self._session as session:
            return session.query(Event).filter(
                Event.user_id == owner_id, Event.user_id == self._owner.id
            ).all()

    def get_events_page_by_user_id(self, owner_id: int, page: int, per_page: int) -> list:
        """Get a single page of events associated with an owner from the database

        Parameters
        ----------
        owner_id : int
            The id of the owner
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of event objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Event).filter(
                Event.owner_id == owner_id, Event.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_characters_to_event(self, event_id: int, characters: list) -> Type[Event]:
        """Append characters to an event

        Parameters
        ----------
        event_id : int
            The id of the event
        characters : list
            A list of character ids

        Returns
        -------
        Event
            The updated event object
        """

        with self._session as session:
            try:
                event = session.query(Event).filter(
                    Event.id == event_id, Event.user_id == self._owner.id
                ).first()

                if not event:
                    raise ValueError('Event not found.')

                for character_id in characters:
                    character = session.query(Character).filter(
                        Character.id == character_id, Character.user_id == self._owner.id
                    ).first()

                    if not character:
                        raise ValueError('Character not found.')

                    character_event = CharacterEvent(user_id=self._owner.id, event_id=event_id,
                                                     character_id=character_id, created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Character {character.__str__} associated with\
                                         event {event.title[:50]} by {self._owner.username}', created=datetime.now())

                    session.add(character_event)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return event

    def get_characters_by_event_id(self, event_id: int) -> list:
        """Get all characters associated with an event

        Parameters
        ----------
        event_id : int
            The id of the event

        Returns
        -------
        list
            A list of character objects
        """

        with self._session as session:
            for character_event in session.query(CharacterEvent).filter(
                CharacterEvent.event_id == event_id, CharacterEvent.user_id == self._owner.id
            ).all():
                yield session.query(Character).filter(Character.id == character_event.character_id).first()

    def get_characters_page_by_event_id(self, event_id: int, page: int, per_page: int) -> list:
        """Get a single page of characters associated with an event from the database

        Parameters
        ----------
        event_id : int
            The id of the event
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of character objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            for character_event in session.query(CharacterEvent).filter(
                CharacterEvent.event_id == event_id, CharacterEvent.user_id == self._owner.id
            ).offset(offset).limit(per_page).all():
                yield session.query(Character).filter(
                    Character.id == character_event.character_id, Character.user_id == self._owner.id
                ).first()

    def append_locations_to_event(self, event_id: int, locations: list) -> Type[Event]:
        """Append locations to an event

        Parameters
        ----------
        event_id : int
            The id of the event
        locations : list
            A list of location ids

        Returns
        -------
        Event
            The updated event object
        """

        with self._session as session:
            try:
                event = session.query(Event).filter(
                    Event.id == event_id, Event.user_id == self._owner.id
                ).first()

                if not event:
                    raise ValueError('Event not found.')

                for location_id in locations:
                    location = session.query(Location).filter(
                        Location.id == location_id, Location.user_id == self._owner.id
                    ).first()

                    if not location:
                        raise ValueError('Location not found.')

                    event_location = EventLocation(user_id=self._owner.id, event_id=event_id, location_id=location_id,
                                                   created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Location {location.name[:50]} associated with\
                                         event {event.title[:50]} by {self._owner.username}', created=datetime.now())

                    session.add(event_location)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return event

    def get_locations_by_event_id(self, event_id: int) -> list:
        """Get all locations associated with an event

        Parameters
        ----------
        event_id : int
            The id of the event

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            for event_location in session.query(EventLocation).filter(
                EventLocation.event_id == event_id, EventLocation.user_id == self._owner.id
            ).all():
                yield session.query(Location).filter(
                    Location.id == event_location.location_id, Location.user_id == self._owner.id
                ).first()

    def append_links_to_event(self, event_id: int, links: list) -> Type[Event]:
        """Append links to an event

        Parameters
        ----------
        event_id : int
            The id of the event
        links : list
            A list of link ids

        Returns
        -------
        Event
            The updated event object
        """

        with self._session as session:
            try:
                event = session.query(Event).filter(
                    Event.id == event_id, Event.user_id == self._owner.id
                ).first()

                if not event:
                    raise ValueError('Event not found.')

                for link_id in links:
                    link = session.query(Link).filter(
                        Link.id == link_id, Link.user_id == self._owner.id
                    ).first()

                    if not link:
                        raise ValueError('Link not found.')

                    event_link = EventLink(user_id=self._owner.id, event_id=event_id, link_id=link_id,
                                           created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Link {link.title[:50]} associated with \
                                        event {event.title[:50]} by {self._owner.username}', created=datetime.now())

                    session.add(event_link)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return event

    def get_links_by_event_id(self, event_id: int) -> list:
        """Get all links associated with an event

        Parameters
        ----------
        event_id : int
            The id of the event

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            for event_link in session.query(EventLink).filter(
                EventLink.event_id == event_id, EventLink.user_id == self._owner.id
            ).all():
                yield session.query(Link).filter(
                    Link.id == event_link.link_id, Link.user_id == self._owner.id
                ).first()

    def get_links_page_by_event_id(self, event_id: int, page: int, per_page: int) -> list:
        """Get a single page of links associated with an event from the database

        Parameters
        ----------
        event_id : int
            The id of the event
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(EventLink).filter(
                EventLink.event_id == event_id, EventLink.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_notes_to_event(self, event_id: int, notes: list) -> Type[Event]:
        """Append notes to an event

        Parameters
        ----------
        event_id : int
            The id of the event
        notes : list
            A list of note ids

        Returns
        -------
        Event
            The updated event object
        """

        with self._session as session:
            try:
                event = session.query(Event).filter(
                    Event.id == event_id, Event.user_id == self._owner.id
                ).first()

                if not event:
                    raise ValueError('Event not found.')

                for note_id in notes:
                    note = session.query(Note).filter(
                        Note.id == note_id, Note.user_id == self._owner.id
                    ).first()

                    if not note:
                        raise ValueError('Note not found.')

                    event_note = EventNote(user_id=self._owner.id, event_id=event_id, note_id=note_id,
                                           created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Note {note.title[:50]} associated with \
                                        event {event.title[:50]} by {self._owner.username}', created=datetime.now())

                    session.add(event_note)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return event

    def get_notes_by_event_id(self, event_id: int) -> list:
        """Get all notes associated with an event

        Parameters
        ----------
        event_id : int
            The id of the event

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            for event_note in session.query(EventNote).filter(
                EventNote.event_id == event_id, EventNote.user_id == self._owner.id
            ).all():
                yield session.query(Note).filter(
                    Note.id == event_note.note_id, Note.user_id == self._owner.id
                ).first()

    def get_notes_page_by_event_id(self, event_id: int, page: int, per_page: int) -> list:
        """Get a single page of notes associated with an event from the database

        Parameters
        ----------
        event_id : int
            The id of the event
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(EventNote).filter(
                EventNote.event_id == event_id, EventNote.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()


class ImageController(BaseController):
    """Image controller encapsulates image management functionality

    Attributes
    ----------
    _self : ImageController
        The instance of the image controller
    _owner : User
        The current user of the image controller
    _session : Session
        The database session

    Methods
    -------
    create_image(caption: str, filename: str, dirname: str, size_in_bytes: int, mime_type: str)
        Create a new image
    update_image(image_id: int, caption: str)
        Update an image
    delete_image(image_id: int)
        Delete an image
    get_images_by_user_id(owner_id: int)
        Get all images associated with a user
    get_images_page_by_user_id(owner_id: int, page: int, per_page: int)
        Get a single page of images associated with a user from the database
    search_images_by_caption(search: str)
        Search for images by caption
    get_images_by_character_id(character_id: int)
        Get all images associated with a character
    get_images_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of images associated with a character from the database
    get_images_by_location_id(location_id: int)
        Get all images associated with a location
    get_images_page_by_location_id(location_id: int, page: int, per_page: int)
        Get a single page of images associated with a location from the database
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_image(self, filename: str, dirname: str, size_in_bytes: int, mime_type: str, caption: str = None) -> Image:
        """Create a new image

        Parameters
        ----------
        filename : str
            The filename of the image
        dirname : str
            The directory name of the image
        size_in_bytes : int
            The size of the image in bytes
        mime_type : str
            The mime type of the image
        caption : str
            The caption of the image, optional

        Returns
        -------
        Image
            The new image object
        """

        with self._session as session:
            try:
                created = datetime.now()
                modified = created

                image = Image(user_id=self._owner.id, caption=caption, filename=filename, dirname=dirname,
                              size_in_bytes=size_in_bytes, mime_type=mime_type, created=created, modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Image {image.id} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(image)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return image

    def update_image(self, image_id: int, caption: str = None) -> Type[Image]:
        """Update an image

        Parameters
        ----------
        image_id : int
            The id of the image
        caption : str
            The caption of the image, optional

        Returns
        -------
        Image
            The updated image object
        """

        with self._session as session:
            try:
                image = session.query(Image).filter(
                    Image.id == image_id, Image.user_id == self._owner.id
                ).first()

                if not image:
                    raise ValueError('Image not found.')

                image.caption = caption
                image.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Image {image.id} updated by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return image

    def delete_image(self, image_id: int) -> bool:
        """Delete an image

        Parameters
        ----------
        image_id : int
            The id of the image

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                image = session.query(Image).filter(
                    Image.id == image_id, Image.user_id == self._owner.id
                ).first()

                if not image:
                    raise ValueError('Image not found.')

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Image {image.id} deleted by {self._owner.username}',
                                    created=datetime.now())

                session.delete(image)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_images_by_user_id(self) -> list:
        """Get all images associated with a user

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            return session.query(Image).filter(
                Image.user_id == self._owner.id
            ).all()

    def get_images_page_by_user_id(self, page: int, per_page: int) -> list:
        """Get a single page of images associated with a user from the database

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Image).filter(
                Image.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def search_images_by_caption(self, search: str) -> list:
        """Search for images by caption

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            return session.query(Image).filter(
                Image.caption.like(f'%{search}%'), Image.user_id == self._owner.id
            ).all()

    def get_images_by_character_id(self, character_id: int) -> list:
        """Get all images associated with a character

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            return session.query(Image).filter(
                Image.character_id == character_id, Image.user_id == self._owner.id
            ).all()

    def get_images_page_by_character_id(self, character_id: int, page: int, per_page: int) -> list:
        """Get a single page of images associated with a character from the database

        Parameters
        ----------
        character_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Image).filter(
                Image.character_id == character_id, Image.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def get_images_by_location_id(self, location_id: int) -> list:
        """Get all images associated with a location

        Images and Locations are associated through ImageLocation objects. This method will use yield to return the
        images one at a time.

        Parameters
        ----------
        location_id : int
            The id of the location

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            for image_location in session.query(ImageLocation).filter(
                ImageLocation.location_id == location_id, ImageLocation.user_id == self._owner.id
            ).all():
                yield session.query(Image).filter(
                    Image.id == image_location.image_id, Image.user_id == self._owner.id
                ).first()

    def get_images_page_by_location_id(self, location_id: int, page: int, per_page: int) -> list:
        """Get a single page of images associated with a location from the database

        Images and Locations are associated through ImageLocation objects. This method will use yield to return the
        images one at a time.

        Parameters
        ----------
        location_id : int
            The id of the location
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            for image_location in session.query(ImageLocation).filter(
                ImageLocation.location_id == location_id, ImageLocation.user_id == self._owner.id
            ).offset(offset).limit(per_page).all():
                yield session.query(Image).filter(
                    Image.id == image_location.image_id, Image.user_id == self._owner.id
                ).first()


class LinkController(BaseController):
    """Link controller encapsulates link management functionality

    Attributes
    ----------
    _self : LinkController
        The instance of the link controller
    _owner : User
        The current user of the link controller
    _session : Session
        The database session

    Methods
    -------
    create_link(url: str, title: str)
        Create a new link
    update_link(link_id: int, url: str, title: str)
        Update a link
    delete_link(link_id: int)
        Delete a link
    get_link_by_id(link_id: int)
        Get a link by id
    get_links_by_owner_id(owner_id: int)
        Get all links associated with an owner
    get_links_page_by_owner_id(owner_id: int, page: int, per_page: int)
        Get a single page of links associated with an owner from the database
    search_links_by_title(search: str)
        Search for links by title
    append_notes_to_link(link_id: int, notes: list)
        Append notes to a link
    get_notes_by_link_id(link_id: int)
        Get all notes associated with a link
    get_notes_page_by_link_id(link_id: int, page: int, per_page: int)
        Get a single page of notes associated with a link from the database
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_link(self, url: str, title: str) -> Link:
        """Create a new link

        Parameters
        ----------
        url : str
            The url of the link
        title : str
            The title of the link

        Returns
        -------
        Link
            The new link object
        """

        with self._session as session:
            try:
                created = datetime.now()
                modified = created

                link = Link(user_id=self._owner.id, url=url, title=title, created=created, modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Link {link.title[:50]} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(link)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return link

    def update_link(self, link_id: int, url: str, title: str) -> Type[Link]:
        """Update a link

        Parameters
        ----------
        link_id : int
            The id of the link
        url : str
            The url of the link
        title : str
            The title of the link

        Returns
        -------
        Link
            The updated link object
        """

        with self._session as session:
            try:
                link = session.query(Link).filter(Link.id == link_id).first()

                if not link:
                    raise ValueError('Link not found.')

                link.url = url
                link.title = title
                link.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Link {link.id} updated by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return link

    def delete_link(self, link_id: int) -> bool:
        """Delete a link

        Parameters
        ----------
        link_id : int
            The id of the link

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                link = session.query(Link).filter(Link.id == link_id).first()

                if not link:
                    raise ValueError('Link not found.')

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Link {link.id} deleted by {self._owner.username}',
                                    created=datetime.now())

                session.delete(link)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_link_by_id(self, link_id: int) -> Type[Link] | None:
        """Get a link by id

        Parameters
        ----------
        link_id : int
            The id of the link

        Returns
        -------
        Link
            The link object
        """

        with self._session as session:
            return session.query(Link).filter(Link.id == link_id).first()

    def get_links_by_story_id(self, story_id: int) -> list:
        """Get all links associated with a story

        The LinkStory objects are the associations between links and stories. This method returns a list of links
        associated with a story.

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            return session.query(Link).join(LinkStory).filter(LinkStory.story_id == story_id).all()

    def get_links_by_owner_id(self, owner_id: int) -> list:
        """Get all links associated with an owner

        Parameters
        ----------
        owner_id : int
            The id of the owner

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            return session.query(Link).filter(Link.owner_id == owner_id).all()

    def get_links_page_by_owner_id(self, owner_id: int, page: int, per_page: int) -> list:
        """Get a single page of links associated with an owner from the database

        Parameters
        ----------
        owner_id : int
            The id of the owner
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Link).filter(
                Link.owner_id == owner_id
            ).offset(offset).limit(per_page).all()

    def search_links_by_title(self, search: str) -> list:
        """Search for links by title

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            return session.query(Link).filter(Link.title.like(f'%{search}%')).all()

    def append_notes_to_link(self, link_id: int, notes: list) -> Type[Link]:
        """Append notes to a link

        Parameters
        ----------
        link_id : int
            The id of the link
        notes : list
            A list of note ids

        Returns
        -------
        Link
            The updated link object
        """

        with self._session as session:
            try:
                link = session.query(Link).filter(Link.id == link_id).first()

                if not link:
                    raise ValueError('Link not found.')

                for note_id in notes:
                    note = session.query(Note).filter(Note.id == note_id).first()

                    if not note:
                        raise ValueError('Note not found.')

                    link_note = LinkNote(user_id=self._owner.id, link_id=link_id, note_id=note_id, created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Note {note.title[:50]} associated with \
                                        link {link.title[:50]} by {self._owner.username}', created=datetime.now())

                    session.add(link_note)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return link

    def get_notes_by_link_id(self, link_id: int) -> list:
        """Get all notes associated with a link

        Parameters
        ----------
        link_id : int
            The id of the link

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            for link_note in session.query(LinkNote).filter(
                LinkNote.link_id == link_id
            ).all():
                yield session.query(Note).filter(Note.id == link_note.note_id).first()

    def get_notes_page_by_link_id(self, link_id: int, page: int, per_page: int) -> list:
        """Get a single page of notes associated with a link from the database

        Parameters
        ----------
        link_id : int
            The id of the link
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(LinkNote).filter(
                LinkNote.link_id == link_id
            ).offset(offset).limit(per_page).all()


class LocationController(BaseController):
    """Location controller encapsulates location management functionality

    Attributes
    ----------
    _self : LocationController
        The instance of the location controller
    _owner : User
        The current user of the location controller
    _session : Session
        The database session

    Methods
    -------
    create_location(title: str, description: str, address: str, city: str, state: str, country: str, zip_code: str, \
                    latitude: float, longitude: float)
        Create a new location
    update_location(location_id: int, title: str, description: str, address: str, city: str, state: str, country: str, \
                    zip_code: str, latitude: float, longitude: float)
        Update a location
    delete_location(location_id: int)
        Delete a location
    get_locations_by_user_id(owner_id: int)
        Get all locations associated with a user
    get_locations_page_by_user_id(owner_id: int, page: int, per_page: int)
        Get a single page of locations associated with a user from the database
    search_locations_by_title_and_description(search: str)
        Search for locations by title and description
    search_locations_by_address(search: str)
        Search for locations by address
    search_locations_by_city(search: str)
        Search for locations by city
    search_locations_by_state(search: str)
        Search for locations by state
    search_locations_by_country(search: str)
        Search for locations by country
    search_locations_by_zip_code(search: str)
        Search for locations by zip code
    append_images_to_location(location_id: int, images: list)
        Append images to a location
    get_images_by_location_id(location_id: int)
        Get all images associated with a location
    get_images_page_by_location_id(location_id: int, page: int, per_page: int)
        Get a single page of images associated with a location from the database
    append_links_to_location(location_id: int, links: list)
        Append links to a location
    get_links_by_location_id(location_id: int)
        Get all links associated with a location
    get_links_page_by_location_id(location_id: int, page: int, per_page: int)
        Get a single page of links associated with a location from the database
    append_notes_to_location(location_id: int, notes: list)
        Append notes to a location
    get_notes_by_location_id(location_id: int)
        Get all notes associated with a location
    get_notes_page_by_location_id(location_id: int, page: int, per_page: int)
        Get a single page of notes associated with a location from the database
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_location(self, title: str, description: str = None, address: str = None, city: str = None,
                        state: str = None, country: str = None, zip_code: str = None, latitude: float = None,
                        longitude: float = None) -> Location:
        """Create a new location

        Parameters
        ----------
        title : str
            The title of the location
        description : str
            The description of the location, optional
        address : str
            The address of the location, optional
        city : str
            The city of the location, optional
        state : str
            The state of the location, optional
        country : str
            The country of the location, optional
        zip_code : str
            The zip code of the location, optional
        latitude : float
            The latitude of the location, optional
        longitude : float
            The longitude of the location, optional

        Returns
        -------
        Location
            The new location object
        """

        with self._session as session:
            try:
                created = datetime.now()
                modified = created

                location = Location(user_id=self._owner.id, title=title, description=description, address=address,
                                    city=city, state=state, country=country, zip_code=zip_code, latitude=latitude,
                                    longitude=longitude, created=created, modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Location {location.id} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(location)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return location

    def update_location(self, location_id: int, title: str, description: str = None, address: str = None,
                        city: str = None, state: str = None, country: str = None, zip_code: str = None,
                        latitude: float = None, longitude: float = None) -> Type[Location]:
        """Update a location

        Parameters
        ----------
        location_id : int
            The id of the location
        title : str
            The title of the location
        description : str
            The description of the location
        address : str
            The address of the location
        city : str
            The city of the location
        state : str
            The state of the location
        country : str
            The country of the location
        zip_code : str
            The zip code of the location
        latitude : float
            The latitude of the location
        longitude : float
            The longitude of the location

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                location = session.query(Location).filter(Location.id == location_id).first()

                if not location:
                    raise ValueError('Location not found.')

                location.title = title
                location.description = description
                location.address = address
                location.city = city
                location.state = state
                location.country = country
                location.zip_code = zip_code
                location.latitude = latitude
                location.longitude = longitude
                location.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Location {location.id} updated by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return location

    def delete_location(self, location_id: int) -> bool:
        """Delete a location

        Parameters
        ----------
        location_id : int
            The id of the location

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                location = session.query(Location).filter(Location.id == location_id).first()

                if not location:
                    raise ValueError('Location not found.')

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Location {location.id} deleted by {self._owner.username}',
                                    created=datetime.now())

                session.delete(location)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_locations_by_user_id(self, user_id: int) -> list:
        """Get all locations associated with an owner

        Parameters
        ----------
        user_id : int
            The id of the user

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(Location.user_id == user_id).all()

    def get_locations_page_by_user_id(self, user_id: int, page: int, per_page: int) -> list:
        """Get a single page of locations associated with an owner from the database

        Parameters
        ----------
        user_id : int
            The id of the user
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Location).filter(
                Location.user_id == user_id
            ).offset(offset).limit(per_page).all()

    def search_locations_by_title_and_description(self, search: str) -> list:
        """Search for locations by title and description

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(
                or_(Location.title.like(f'%{search}%'), Location.description.like(f'%{search}%'))
            ).all()

    def search_locations_by_address(self, search: str) -> list:
        """Search for locations by address

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(Location.address.like(f'%{search}%')).all()

    def search_locations_by_city(self, search: str) -> list:
        """Search for locations by city

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(Location.city.like(f'%{search}%')).all()

    def search_locations_by_state(self, search: str) -> list:
        """Search for locations by state

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(Location.state.like(f'%{search}%')).all()

    def search_locations_by_country(self, search: str) -> list:
        """Search for locations by country

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(Location.country.like(f'%{search}%')).all()

    def search_locations_by_zip_code(self, search: str) -> list:
        """Search for locations by zip code

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(Location.zip_code.like(f'%{search}%')).all()

    def append_images_to_location(self, location_id: int, images: list) -> Type[Location]:
        """Append images to a location

        Parameters
        ----------
        location_id : int
            The id of the location
        images : list
            A list of image ids

        Returns
        -------
        Location
            The updated location object
        """

        with self._session as session:
            try:
                location = session.query(Location).filter(Location.id == location_id).first()

                if not location:
                    raise ValueError('Location not found.')

                for image_id in images:
                    image = session.query(Image).filter(Image.id == image_id).first()

                    if not image:
                        raise ValueError('Image not found.')

                    position = session.query(func.max(ImageLocation.position)).filter(
                        ImageLocation.location_id == location_id
                    ).scalar()
                    position = position + 1 if position else 1
                    is_default = False
                    created = datetime.now()
                    modified = created
                    image_location = ImageLocation(user_id=self._owner.id, location_id=location_id, image_id=image_id,
                                                   position=position, is_default=is_default, created=created,
                                                   modified=modified)

                    activity = Activity(user_id=self._owner.id, summary=f'Image {image.caption[:50]} associated with \
                                        location {location.title[:50]} by {self._owner.username}',
                                        created=datetime.now())

                    session.add(image_location)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return location

    def get_images_by_location_id(self, location_id: int) -> list:
        """Get all images associated with a location

        The images should be returned in the order determined by the position field in the ImageLocation table.

        Parameters
        ----------
        location_id : int
            The id of the location

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            for image_location in session.query(ImageLocation).filter(
                ImageLocation.location_id == location_id
            ).order_by(ImageLocation.position).all():
                yield session.query(Image).filter(Image.id == image_location.image_id).first()

    def get_images_page_by_location_id(self, location_id: int, page: int, per_page: int) -> list:
        """Get a single page of images associated with a location from the database

        Parameters
        ----------
        location_id : int
            The id of the location
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(ImageLocation).filter(
                ImageLocation.location_id == location_id
            ).offset(offset).limit(per_page).all()

    def append_links_to_location(self, location_id: int, links: list) -> Type[Location]:
        """Append links to a location

        Parameters
        ----------
        location_id : int
            The id of the location
        links : list
            A list of link ids

        Returns
        -------
        Location
            The updated location object
        """

        with self._session as session:
            try:
                location = session.query(Location).filter(Location.id == location_id).first()

                if not location:
                    raise ValueError('Location not found.')

                for link_id in links:
                    link = session.query(Link).filter(Link.id == link_id).first()

                    if not link:
                        raise ValueError('Link not found.')

                    link_location = LinkLocation(user_id=self._owner.id, location_id=location_id, link_id=link_id,
                                                 created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Link {link.title[:50]} associated with \
                                        location {location.title[:50]} by {self._owner.username}',
                                        created=datetime.now())

                    session.add(link_location)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return location

    def get_links_by_location_id(self, location_id: int) -> list:
        """Get all links associated with a location

        Parameters
        ----------
        location_id : int
            The id of the location

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            for link_location in session.query(LinkLocation).filter(
                LinkLocation.location_id == location_id
            ).all():
                yield session.query(Link).filter(Link.id == link_location.link_id).first()

    def get_links_page_by_location_id(self, location_id: int, page: int, per_page: int) -> list:
        """Get a single page of links associated with a location from the database

        Parameters
        ----------
        location_id : int
            The id of the location
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(LinkLocation).filter(
                LinkLocation.location_id == location_id
            ).offset(offset).limit(per_page).all()

    def append_notes_to_location(self, location_id: int, notes: list) -> Type[Location]:
        """Append notes to a location

        Parameters
        ----------
        location_id : int
            The id of the location
        notes : list
            A list of note ids

        Returns
        -------
        Location
            The updated location object
        """

        with self._session as session:
            try:
                location = session.query(Location).filter(Location.id == location_id).first()

                if not location:
                    raise ValueError('Location not found.')

                for note_id in notes:
                    note = session.query(Note).filter(Note.id == note_id).first()

                    if not note:
                        raise ValueError('Note not found.')

                    location_note = LocationNote(user_id=self._owner.id, location_id=location_id, note_id=note_id,
                                                 created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Note {note.title[:50]} associated with \
                                        location {location.title[:50]} by {self._owner.username}',
                                        created=datetime.now())

                    session.add(location_note)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return location

    def get_notes_by_location_id(self, location_id: int) -> list:
        """Get all notes associated with a location

        Parameters
        ----------
        location_id : int
            The id of the location

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            for location_note in session.query(LocationNote).filter(
                LocationNote.location_id == location_id
            ).all():
                yield session.query(Note).filter(Note.id == location_note.note_id).first()

    def get_notes_page_by_location_id(self, location_id: int, page: int, per_page: int) -> list:
        """Get a single page of notes associated with a location from the database

        Parameters
        ----------
        location_id : int
            The id of the location
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(LocationNote).filter(
                LocationNote.location_id == location_id
            ).offset(offset).limit(per_page).all()


class NoteController(BaseController):
    """Note controller encapsulates note management functionality

    Attributes
    ----------
    _self : NoteController
        The instance of the note controller
    _owner : User
        The current user of the note controller
    _session : Session
        The database session

    Methods
    -------
    create_note(title: str, content: str)
        Create a new note
    update_note(note_id: int, title: str, content: str)
        Update a note
    delete_note(note_id: int)
        Delete a note
    get_notes_by_owner_id(owner_id: int)
        Get all notes associated with an owner
    get_notes_page_by_owner_id(owner_id: int, page: int, per_page: int)
        Get a single page of notes associated with an owner from the database
    search_notes_by_title_and_content(search: str)
        Search for notes by title and content
    append_links_to_note(note_id: int, links: list)
        Append links to a note
    get_links_by_note_id(note_id: int)
        Get all links associated with a note
    get_links_page_by_note_id(note_id: int, page: int, per_page: int)
        Get a single page of links associated with a note from the database
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_note(self, title: str, content: str) -> Note:
        """Create a new note

        Parameters
        ----------
        title : str
            The title of the note
        content : str
            The content of the note

        Returns
        -------
        Note
            The new note object
        """

        with self._session as session:
            try:
                created = datetime.now()
                modified = created

                note = Note(user_id=self._owner.id, title=title, content=content, created=created, modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Note {note.title[:50]} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(note)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return note

    def update_note(self, note_id: int, title: str, content: str) -> Type[Note]:
        """Update a note

        Parameters
        ----------
        note_id : int
            The id of the note
        title : str
            The title of the note
        content : str
            The content of the note

        Returns
        -------
        Note
            The updated note object
        """

        with self._session as session:
            try:
                note = session.query(Note).filter(Note.id == note_id).first()

                if not note:
                    raise ValueError('Note not found.')

                note.title = title
                note.content = content
                note.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Note {note.id} updated by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return note

    def delete_note(self, note_id: int) -> bool:
        """Delete a note

        Parameters
        ----------
        note_id : int
            The id of the note

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                note = session.query(Note).filter(Note.id == note_id).first()

                if not note:
                    raise ValueError('Note not found.')

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Note {note.id} deleted by {self._owner.username}',
                                    created=datetime.now())

                session.delete(note)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_note_by_id(self, note_id: int) -> Type[Note] | None:
        """Get a note by id

        Parameters
        ----------
        note_id : int
            The id of the note

        Returns
        -------
        Note
            The note object
        """

        with self._session as session:
            return session.query(Note).filter(Note.id == note_id).first()

    def get_notes_by_owner_id(self, owner_id: int) -> list:
        """Get all notes associated with an owner

        Parameters
        ----------
        owner_id : int
            The id of the owner

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            return session.query(Note).filter(Note.owner_id == owner_id).all()

    def get_notes_page_by_owner_id(self, owner_id: int, page: int, per_page: int) -> list:
        """Get a single page of notes associated with an owner from the database

        Parameters
        ----------
        owner_id : int
            The id of the owner
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Note).filter(
                Note.owner_id == owner_id
            ).offset(offset).limit(per_page).all()

    def search_notes_by_title_and_content(self, search: str) -> list:
        """Search for notes by title and content

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            return session.query(Note).filter(
                or_(Note.title.like(f'%{search}%'), Note.content.like(f'%{search}%'))
            ).all()

    def append_links_to_note(self, note_id: int, links: list) -> Type[Note]:
        """Append links to a note

        Parameters
        ----------
        note_id : int
            The id of the note
        links : list
            A list of link ids

        Returns
        -------
        Note
            The updated note object
        """

        with self._session as session:
            try:
                note = session.query(Note).filter(Note.id == note_id).first()

                if not note:
                    raise ValueError('Note not found.')

                for link_id in links:
                    link = session.query(Link).filter(Link.id == link_id).first()

                    if not link:
                        raise ValueError('Link not found.')

                    link_note = LinkNote(user_id=self._owner.id, note_id=note_id, link_id=link_id,
                                         created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Link {link.title[:50]} associated with \
                                        note {note.title[:50]} by {self._owner.username}', created=datetime.now())

                    session.add(link_note)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return note

    def get_links_by_note_id(self, note_id: int) -> list:
        """Get all links associated with a note

        Parameters
        ----------
        note_id : int
            The id of the note

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            for link_note in session.query(LinkNote).filter(
                LinkNote.note_id == note_id
            ).all():
                yield session.query(Link).filter(Link.id == link_note.link_id).first()

    def get_links_page_by_note_id(self, note_id: int, page: int, per_page: int) -> list:
        """Get a single page of links associated with a note from the database

        Parameters
        ----------
        note_id : int
            The id of the note
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(LinkNote).filter(
                LinkNote.note_id == note_id
            ).offset(offset).limit(per_page).all()


class SceneController(BaseController):
    """Scene controller encapsulates scene management functionality

    Attributes
    ----------
    _self : SceneController
        The instance of the scene controller
    _owner : User
        The current user of the scene controller
    _session : Session
        The database session

    Methods
    -------
    create_scene(story_id: int, chapter_id: int, title: str, description: str, content: str)
        Create a new scene
    update_scene(scene_id: int, title: str, description: str, content: str)
        Update a scene
    change_scene_position(scene_id: int, position: int)
        Change the position of a scene within a chapter
    delete_scene(scene_id: int)
        Delete a scene
    get_scenes_by_owner_id(owner_id: int)
        Get all scenes associated with an owner
    get_scenes_page_by_owner_id(owner_id: int, page: int, per_page: int)
        Get a single page of scenes associated with an owner from the database
    get_scenes_by_story_id(story_id: int)
        Get all scenes associated with a story
    get_scenes_page_by_story_id(story_id: int, page: int, per_page: int)
        Get a single page of scenes associated with a story from the database
    get_scenes_by_chapter_id(chapter_id: int)
        Get all scenes associated with a chapter
    get_scenes_page_by_chapter_id(chapter_id: int, page: int, per_page: int)
        Get a single page of scenes associated with a chapter from the database
    search_scenes_by_title_and_description(search: str)
        Search for scenes by title and description
    search_scenes_by_content(search: str)
        Search for scenes by content
    append_links_to_scene(scene_id: int, link_ids: list)
        Append links to a scene
    get_links_by_scene_id(scene_id: int)
        Get all links associated with a scene
    append_notes_to_scene(scene_id: int, note_ids: list)
        Append notes to a scene
    get_notes_by_scene_id(scene_id: int)
        Get all notes associated with a scene
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_scene(self, story_id: int, chapter_id: int, title: str, description: str, content: str) -> Scene:
        """Create a new scene

        Parameters
        ----------
        story_id : int
            The id of the story
        chapter_id : int
            The id of the chapter
        title : str
            The title of the scene
        description : str
            The description of the scene
        content : str
            The content of the scene

        Returns
        -------
        Scene
            The new scene object
        """

        with self._session as session:
            try:
                title_exists = session.query(Scene).filter(
                    Scene.title == title, Scene.chapter_id == chapter_id
                ).first()

                if title_exists:
                    raise Exception('This chapter already has a scene with the same title.')

                position = session.query(func.max(Scene.position)).filter(Scene.chapter_id == chapter_id).scalar()
                position = int(position) + 1 if position else 1
                created = datetime.now()
                modified = created

                scene = Scene(user_id=self._owner.id, story_id=story_id, chapter_id=chapter_id, position=position,
                              title=title, description=description, content=content, created=created, modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Scene {scene.title[:50]} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(scene)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return scene

    def update_scene(self, scene_id: int, title: str, description: str, content: str) -> Type[Scene]:
        """Update a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene
        title : str
            The title of the scene
        description : str
            The description of the scene
        content : str
            The content of the scene

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                scene = session.query(Scene).filter(Scene.id == scene_id).first()

                if not scene:
                    raise ValueError('Scene not found.')

                scene.title = title
                scene.description = description
                scene.content = content
                scene.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Scene {scene.id} updated by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return scene

    def change_scene_position(self, scene_id: int, position: int) -> int:
        """Change the position of a scene within a chapter

        First, determine whether the new position is closer to 1 or further from 1. If closer to one, get all sibling
        scenes with positions greater than or equal to the new position but less than the current position, and
        increment those position values by 1. If the target position is further away from 1 than the current position,
        get all sibling scenes with positions greater than the current position but less than or equal to the new
        position, and decrement those position values by 1. Finally, set the position of the target scene to the new
        position. Return the new position.

        Parameters
        ----------
        scene_id : int
            The id of the scene
        position : int
            The position of the scene

        Returns
        -------
        int
            The new position value
        """

        with self._session as session:
            try:
                datetime_format = "%Y-%m-%d %H:%M:%S.%f"
                scene = session.query(Scene).filter(Scene.id == scene_id).first()

                if not scene:
                    raise ValueError('Scene not found.')

                if scene.position == position:
                    return position

                if scene.position > position:
                    scenes = session.query(Scene).filter(
                        Scene.chapter_id == scene.chapter_id, Scene.position >= position,
                        Scene.position < scene.position
                    ).all()
                    for sibling in scenes:
                        sibling.position += 1
                        sibling.created = datetime.strptime(str(sibling.created), datetime_format)
                        sibling.modified = datetime.now()
                else:
                    scenes = session.query(Scene).filter(
                        Scene.chapter_id == scene.chapter_id, Scene.position > scene.position,
                        Scene.position <= position
                    ).all()
                    for sibling in scenes:
                        sibling.position -= 1
                        sibling.created = datetime.strptime(str(sibling.created), datetime_format)
                        sibling.modified = datetime.now()

                scene.position = position
                scene.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Scene {scene.title[:50]} position changed by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return position

    def delete_scene(self, scene_id: int) -> bool:
        """Delete a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                scene = session.query(Scene).filter(Scene.id == scene_id).first()

                if not scene:
                    raise ValueError('Scene not found.')

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Scene {scene.id} deleted by {self._owner.username}',
                                    created=datetime.now())

                session.delete(scene)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_scenes_by_owner_id(self, owner_id: int) -> list:
        """Get all scenes associated with an owner

        Scenes are sorted by story id, chapter id, and position in ascending order.

        Parameters
        ----------
        owner_id : int
            The id of the owner

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            return session.query(Scene).filter(Scene.owner_id == owner_id).order_by(
                Scene.story_id, Scene.chapter_id, Scene.position
            ).all()

    def get_scenes_page_by_owner_id(self, owner_id: int, page: int, per_page: int) -> list:
        """Get a single page of scenes associated with an owner from the database

        Scenes are sorted by story id, chapter id, and position in ascending order

        Parameters
        ----------
        owner_id : int
            The id of the owner
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Scene).filter(
                Scene.owner_id == owner_id
            ).order_by(Scene.story_id, Scene.chapter_id, Scene.position).offset(offset).limit(per_page).all()

    def get_scenes_by_story_id(self, story_id: int) -> list:
        """Get all scenes associated with a story

        Scenes are sorted by chapter id and position in ascending order

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            return session.query(Scene).filter(Scene.story_id == story_id).all()

    def get_scenes_page_by_story_id(self, story_id: int, page: int, per_page: int) -> list:
        """Get a single page of scenes associated with a story from the database

        Parameters
        ----------
        story_id : int
            The id of the story
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Scene).filter(
                Scene.story_id == story_id
            ).offset(offset).limit(per_page).all()

    def get_scenes_by_chapter_id(self, chapter_id: int) -> list:
        """Get all scenes associated with a chapter

        Scenes are sorted by position in ascending order

        Parameters
        ----------
        chapter_id : int
            The id of the chapter

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            return session.query(Scene).filter(Scene.chapter_id == chapter_id).order_by(Scene.position).all()

    def get_scenes_page_by_chapter_id(self, chapter_id: int, page: int, per_page: int) -> list:
        """Get a single page of scenes associated with a chapter from the database

        Scenes are sorted by position in ascending order

        Parameters
        ----------
        chapter_id : int
            The id of the chapter
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Scene).filter(
                Scene.chapter_id == chapter_id
            ).order_by(Scene.position).offset(offset).limit(per_page).all()

    def search_scenes_by_title_and_description(self, search: str) -> list:
        """Search for scenes by title and description

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            return session.query(Scene).filter(
                or_(Scene.title.like(f'%{search}%'), Scene.description.like(f'%{search}%'))
            ).all()

    def search_scenes_by_content(self, search: str) -> list:
        """Search for scenes by content

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            return session.query(Scene).filter(Scene.content.like(f'%{search}%')).all()

    def append_links_to_scene(self, scene_id: int, link_ids: list) -> Type[Scene]:
        """Append links to a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene
        link_ids : list
            A list of link ids

        Returns
        -------
        Scene
            The updated scene object
        """

        with self._session as session:
            try:
                scene = session.query(Scene).filter(Scene.id == scene_id).first()

                if not scene:
                    raise ValueError('Scene not found.')

                for link_id in link_ids:
                    link = session.query(Link).filter(Link.id == link_id).first()

                    if not link:
                        raise ValueError('Link not found.')

                    link_scene = LinkScene(user_id=self._owner.id, link_id=link_id, scene_id=scene_id,
                                           created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Links appended to scene {scene.id} by \
                                        {self._owner.username}', created=datetime.now())

                    session.add(link_scene)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return scene

    def get_links_by_scene_id(self, scene_id: int) -> list:
        """Get all links associated with a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            return session.query(Link).join(LinkScene).filter(LinkScene.scene_id == scene_id).all()

    def append_notes_to_scene(self, scene_id: int, note_ids: list) -> Type[Scene]:
        """Append notes to a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene
        note_ids : list
            A list of note ids

        Returns
        -------
        Scene
            The updated scene object
        """

        with self._session as session:
            try:
                scene = session.query(Scene).filter(Scene.id == scene_id).first()

                if not scene:
                    raise ValueError('Scene not found.')

                for note_id in note_ids:
                    note = session.query(Note).filter(Note.id == note_id).first()

                    if not note:
                        raise ValueError('Note not found.')

                    note_scene = NoteScene(user_id=self._owner.id, note_id=note_id, scene_id=scene_id,
                                           created=datetime.now())

                    activity = Activity(user_id=self._owner.id, summary=f'Notes appended to scene {scene.id} by \
                                        {self._owner.username}', created=datetime.now())

                    session.add(note_scene)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return scene

    def get_notes_by_scene_id(self, scene_id: int) -> list:
        """Get all notes associated with a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            return session.query(Note).join(NoteScene).filter(NoteScene.scene_id == scene_id).all()


class StoryController(BaseController):
    """Story controller encapsulates story management functionality

    Attributes
    ----------
    _self : StoryController
        The instance of the story controller
    _owner : User
        The current user of the story controller
    _session : Session
        The database session

    Methods
    -------
    create_story(title: str, description: str)
        Create a new story
    update_story(story_id: int, title: str, description: str)
        Update a story
    delete_story(story_id: int)
        Delete a story
    get_story_by_id(story_id: int)
        Get a story by id
    get_stories_by_owner_id(owner_id: int)
        Get all stories associated with an owner
    get_stories_page_by_owner_id(owner_id: int, page: int, per_page: int)
        Get a single page of stories associated with an owner from the database
    search_stories_by_title_and_description(search: str)
        Search for stories by title and description
    append_authors_to_story(story_id: int, author_ids: list)
        Append authors to a story
    get_authors_by_story_id(story_id: int)
        Get all authors associated with a story
    append_links_to_story(story_id: int, link_ids: list)
        Append links to a story
    get_links_by_story_id(story_id: int)
        Get all links associated with a story
    append_notes_to_story(story_id: int, note_ids: list)
        Append notes to a story
    get_notes_by_story_id(story_id: int)
        Get all notes associated with a story
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_story(self, title: str, description: str) -> Story:
        """Create a new story

        Parameters
        ----------
        title : str
            The title of the story
        description : str
            The description of the story

        Returns
        -------
        Story
            The new story object
        """

        with self._session as session:
            try:
                created = datetime.now()
                modified = created

                story = Story(user_id=self._owner.id, title=title, description=description, created=created,
                              modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Story {story.title[:50]} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(story)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def update_story(self, story_id: int, title: str, description: str) -> Type[Story]:
        """Update a story

        Parameters
        ----------
        story_id : int
            The id of the story
        title : str
            The title of the story
        description : str
            The description of the story

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                story = session.query(Story).filter(Story.id == story_id).first()

                if not story:
                    raise ValueError('Story not found.')

                story.title = title
                story.description = description
                story.modified = datetime.now()

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Story {story.id} updated by {self._owner.username}',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def delete_story(self, story_id: int) -> bool:
        """Delete a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                story = session.query(Story).filter(Story.id == story_id).first()

                if not story:
                    raise ValueError('Story not found.')

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Story {story.id} deleted by {self._owner.username}',
                                    created=datetime.now())

                session.delete(story)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_story_by_id(self, story_id: int) -> Type[Story] | None:
        """Get a story by id

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        Story
            The story object
        """

        with self._session as session:
            story = session.query(Story).filter(Story.id == story_id).first()
            return story

    def get_stories_by_owner_id(self, owner_id: int) -> list:
        """Get all stories associated with an owner

        Parameters
        ----------
        owner_id : int
            The id of the owner

        Returns
        -------
        list
            A list of story objects
        """

        with self._session as session:
            return session.query(Story).filter(Story.user_id == owner_id).all()

    def get_stories_page_by_owner_id(self, owner_id: int, page: int, per_page: int) -> list:
        """Get a single page of stories associated with an owner from the database

        Parameters
        ----------
        owner_id : int
            The id of the owner
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of story objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Story).filter(
                Story.owner_id == owner_id
            ).offset(offset).limit(per_page).all()

    def search_stories_by_title_and_description(self, search: str) -> list:
        """Search for stories by title and description

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of story objects
        """

        with self._session as session:
            return session.query(Story).filter(
                or_(Story.title.like(f'%{search}%'), Story.description.like(f'%{search}%'))
            ).all()

    def append_authors_to_story(self, story_id: int, author_ids: list) -> Type[Story]:
        """Append authors to a story

        Parameters
        ----------
        story_id : int
            The id of the story
        author_ids : list
            The ids of the authors to append

        Returns
        -------
        Story
            The updated story object
        """

        with self._session as session:
            try:
                story = session.query(Story).filter(Story.id == story_id).first()

                if not story:
                    raise ValueError('Story not found.')

                for author_id in author_ids:
                    author = session.query(Author).filter(Author.id == author_id).first()

                    if not author:
                        raise ValueError('Author not found.')

                    author_story = AuthorStory(user_id=self._owner.id, author_id=author_id, story_id=story_id,
                                               created=datetime.now())
                    story.authors.append(author_story)

                activity = Activity(user_id=self._owner.id, summary=f'Authors appended to story {story.title[:50]} by \
                                    {self._owner.username}', created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def get_authors_by_story_id(self, story_id: int) -> list:
        """Get all authors associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of author objects
        """

        with self._session as session:
            return session.query(Author).join(AuthorStory).filter(AuthorStory.story_id == story_id).all()

    def append_links_to_story(self, story_id: int, link_ids: list) -> Type[Story]:
        """Append links to a story

        Parameters
        ----------
        story_id : int
            The id of the story
        link_ids : list
            The ids of the links to append

        Returns
        -------
        Story
            The updated story object
        """

        with self._session as session:
            try:
                story = session.query(Story).filter(Story.id == story_id).first()

                if not story:
                    raise ValueError('Story not found.')

                for link_id in link_ids:
                    link = session.query(Link).filter(Link.id == link_id).first()

                    if not link:
                        raise ValueError('Link not found.')

                    link_story = LinkStory(user_id=self._owner.id, story_id=story_id, link_id=link_id, created=datetime.now())

                    story.links.append(link_story)

                activity = Activity(user_id=self._owner.id, summary=f'Links appended to story {story.title[:50]} by \
                                    {self._owner.username}', created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def get_links_by_story_id(self, story_id: int) -> list:
        """Get all links associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            return session.query(Link).join(LinkStory).filter(LinkStory.story_id == story_id).all()

    def append_notes_to_story(self, story_id: int, note_ids: list) -> Type[Story]:
        """Append notes to a story

        Parameters
        ----------
        story_id : int
            The id of the story
        note_ids : list
            The ids of the notes to append

        Returns
        -------
        Story
            The updated story object
        """

        with self._session as session:
            try:
                story = session.query(Story).filter(Story.id == story_id).first()

                if not story:
                    raise ValueError('Story not found.')

                for note_id in note_ids:
                    note = session.query(Note).filter(Note.id == note_id).first()

                    if not note:
                        raise ValueError('Note not found.')

                    note_story = NoteStory(user_id=self._owner.id, story_id=story_id, note_id=note_id, created=datetime.now())

                    story.notes.append(note_story)

                activity = Activity(user_id=self._owner.id, summary=f'Notes appended to story {story.title[:50]} by \
                                    {self._owner.username}', created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def get_notes_by_story_id(self, story_id: int) -> list:
        """Get all notes associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            return session.query(Note).join(NoteStory).filter(NoteStory.story_id == story_id).all()


class SubmissionController(BaseController):
    """Submission controller encapsulates submission management functionality

    Attributes
    ----------
    _self : SubmissionController
        The instance of the submission controller
    _owner : User
        The current user of the submission controller
    _session : Session
        The database session

    Methods
    -------
    create_submission(story_id: int, submitted_to: str, date_sent: str)
        Create a new submission
    update_submission(submission_id: int, submitted_to: str, date_sent: str, date_reply_received: str, \
                      date_published: str, date_paid: str, result: str, amount: float)
        Update a submission
    delete_submission(submission_id: int)
        Delete a submission
    get_submissions_by_owner_id(owner_id: int)
        Get all submissions associated with an owner
    get_submissions_page_by_owner_id(owner_id: int, page: int, per_page: int)
        Get a single page of submissions associated with an owner from the database
    get_submissions_by_story_id(story_id: int)
        Get all submissions associated with a story
    get_submissions_page_by_story_id(story_id: int, page
        Get a single page of submissions associated with a story from the database
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_submission(self, story_id: int, submitted_to: str, date_sent: str = None) -> Submission:
        """Create a new submission

        Parameters
        ----------
        story_id : int
            The id of the story
        submitted_to : str
            The entity the story was submitted to
        date_sent : str
            The date the story was submitted, optional

        Returns
        -------
        Submission
            The new submission object
        """

        with (self._session as session):
            try:
                if date_sent is not None:
                    date_sent = datetime.strptime(date_sent, '%Y-%m-%d')
                else:
                    datetime.strptime(str(date.today()), '%Y-%m-%d')

                created = datetime.now()
                modified = created

                submission = Submission(user_id=self._owner.id, story_id=story_id, submitted_to=submitted_to,
                                        date_sent=date_sent, created=created, modified=modified)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'Submission {submission.id} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(submission)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return submission

    def update_submission(self, submission_id: int, submitted_to: str, date_sent: str, date_reply_received: str,
                          date_published: str, date_paid: str, result: str, amount: float) -> Type[Submission]:
        """Update a submission
        
        Parameters
        ----------
        submission_id : int
            The id of the submission
        submitted_to : str
            The entity the story was submitted to
        date_sent : str
            The date the story was submitted
        date_reply_received : str
            The date the reply was received
        date_published : str
            The date the story was published
        date_paid : str
            The date the story was paid
        result : str
            The result of the submission
        amount : float
            The amount paid for the submission
            
        Returns
        -------
        Submission
            The updated submission object
        """

        with self._session as session:
            try:
                submission = session.query(Submission).filter(Submission.id == submission_id).first()

                if not submission:
                    raise ValueError('Submission not found.')

                submission.submitted_to = submitted_to
                submission.date_sent = date_sent
                submission.date_reply_received = date_reply_received
                submission.date_published = date_published
                submission.date_paid = date_paid
                submission.result = result
                submission.amount = amount

                activity = Activity(user_id=self._owner.id, summary=f'Submission {submission.id} updated by \
                                    {self._owner.username}', created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return submission

    def delete_submission(self, submission_id: int) -> bool:
        """Delete a submission

        Parameters
        ----------
        submission_id : int
            The id of the submission

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                submission = session.query(Submission).filter(Submission.id == submission_id).first()

                if not submission:
                    raise ValueError('Submission not found.')

                activity = Activity(user_id=self._owner.id, summary=f'Submission {submission.id} deleted by \
                                    {self._owner.username}', created=datetime.now())

                session.delete(submission)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_submissions_by_owner_id(self, owner_id: int) -> list:
        """Get all submissions associated with an owner

        Parameters
        ----------
        owner_id : int
            The id of the owner

        Returns
        -------
        list
            A list of submission objects
        """

        with self._session as session:
            return session.query(Submission).filter(Submission.owner_id == owner_id).all()

    def get_submissions_page_by_owner_id(self, owner_id: int, page: int, per_page: int) -> list:
        """Get a single page of submissions associated with an owner from the database

        Parameters
        ----------
        owner_id : int
            The id of the owner
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of submission objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Submission).filter(
                Submission.owner_id == owner_id
            ).offset(offset).limit(per_page).all()

    def get_submissions_by_story_id(self, story_id: int) -> list:
        """Get all submissions associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of submission objects
        """

        with self._session as session:
            return session.query(Submission).filter(Submission.story_id == story_id).all()

    def get_submissions_page_by_story_id(self, story_id: int, page: int, per_page: int) -> list:
        """Get a single page of submissions associated with a story from the database

        Parameters
        ----------
        story_id : int
            The id of the story
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of submission objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Submission).filter(
                Submission.story_id == story_id
            ).offset(offset).limit(per_page).all()


class UserController(BaseController):
    """User controller encapsulates user management functionality

    Attributes
    ----------
    _self : UserController
        The instance of the user controller
    _owner : User
        The current user of the user controller
    _session : Session
        The database session

    Methods
    -------
    create_user(username: str, password: str, email: str)
        Create a new user
    register_user(username: str, password: str, repassword: str, email: str, reemail: str)
        Register a new user identity
    activate_user(user_id: int)
        Activate a user
    deactivate_user(user_id: int)
        Deactivate a user
    login(username: str, password: str)
        User login
    change_password(user_id: int, old_password: str, new_password, repassword: str)
        Change user password
    delete_user(user_id: int)
        Delete a user
    get_user_by_id(user_id: int)
        Get a user by id
    get_user_by_uuid(user_uuid: str)
        Get a user by uuid
    get_user_by_username(username: str)
        Get a user by username
    get_user_by_email(email: str)
        Get a user by email
    get_user_count()
        Get user count
    get_all_users()
        Get all users
    get_users_page(page: int, per_page: int)
        Get a single page of users from the database
    search_users(search: str)
        Search for users by username or email
    """

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

    def create_user(self, username: str, password: str, email: str) -> User:
        """Create a new user

        This method is available to the desktop application owner and the web application owner. It is not available to
        secondary users of the desktop application or the web application. The method first checks if the username or
        email already exists. If either exists, an exception is raised. If neither exists, the method creates a new user
        and logs the activity. The method returns the new user's id on success and nothing on failure.

        Parameters
        ----------
        username : str
            The username of the new user
        password : str
            The password of the new user
        email : str
            The email of the new user

        Returns
        -------
        User
            The new user object
        """

        with self._session as session:

            try:
                username_exists = session.query(User).filter(User.username == username).first()

                if username_exists:
                    raise Exception('That username already exists.')

                email_exists = session.query(User).filter(User.email == email).first()

                if email_exists:
                    raise Exception('That email already exists.')

                uuid4 = str(uuid.uuid4())
                uuid_exists = session.query(User).filter(User.uuid == uuid4).first()

                while uuid_exists:
                    uuid4 = str(uuid.uuid4())
                    uuid_exists = session.query(User).filter(User.uuid == uuid4).first()

                password = hash_password(password)
                created = datetime.now()
                modified = created

                user = User(uuid=uuid4, username=username, password=password, email=email, created=created,
                            modified=modified, is_active=True)

                activity = Activity(user_id=self._owner.id,
                                    summary=f'User {user.username} created by {self._owner.username}',
                                    created=datetime.now())

                session.add(user)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return user

    def register_user(self, username: str, password: str, repassword: str, email: str, reemail: str) -> User:
        """Register a new user identity

        This method is for self-registration of new users. It is available to secondary users of the website and the
        desktop application. The method first checks if the username or email already exists. If either exists, an
        exception is raised. If neither exists, the method creates a new user and logs the activity. The method returns
        the new user's id on success and nothing on failure.

        Parameters
        ----------
        username : str
            The username of the new user
        password : str
            The password of the new user
        repassword : str
            The password of the new user repeated
        email : str
            The email of the new user
        reemail : str
            The email of the new user repeated

        Returns
        -------
        int
            The id of the new user on success
        """

        with self._session as session:

            try:

                username_exists = session.query(User).filter(User.username == username).first()

                if username_exists:
                    raise Exception('That username already exists.')

                if email != reemail:
                    raise Exception('The email addresses do not match.')

                email_exists = session.query(User).filter(User.email == email).first()

                if email_exists:
                    raise Exception('That email address already exists.')

                if password != repassword:
                    raise Exception('The passwords do not match.')

                uuid4 = str(uuid.uuid4())
                uuid_exists = session.query(User).filter(User.uuid == uuid4).first()

                while uuid_exists:
                    uuid4 = str(uuid.uuid4())
                    uuid_exists = session.query(User).filter(User.uuid == uuid4).first()

                password = hash_password(password)
                created = datetime.now()
                modified = created
                user = User(uuid=uuid4, username=username, password=password, email=email, created=created,
                            modified=modified, is_active=False)

                session.add(user)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()

                activity = Activity(user_id=user.id,
                                    summary=f'User {user.username} registered by {user.username}',
                                    created=datetime.now())

                try:
                    session.add(activity)

                except Exception as e:
                    session.rollback()
                    raise e

                else:
                    session.commit()
                    return user

    def activate_user(self, user_id: int) -> User:
        """Activate a user

        Parameters
        ----------
        user_id: int
            The id of the user to activate

        Returns
        -------
        User
            The activated user object
        """

        with self._session as session:

            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                raise ValueError('User not found.')

            try:
                user.is_active = True
                user.modified = datetime.now()
                activity = Activity(user_id=self._owner.id,
                                    summary=f'User {user.username} activated by {self._owner.username}',
                                    created=datetime.now())

                session.add(user)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return user.id

    def deactivate_user(self, user_id: int) -> Type[User]:
        """Deactivate a user

        Parameters
        ----------
        user_id: int
            The id of the user to deactivate

        Returns
        -------
        User
            The deactivated user object
        """

        with self._session as session:

            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                raise ValueError('User not found.')

            try:
                user.is_active = False
                user.modified = datetime.now()
                activity = Activity(user_id=self._owner.id,
                                    summary=f'User {user.username} deactivated by {self._owner.username}',
                                    created=datetime.now())

                session.add(user)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return user

    def login(self, username: str, password: str) -> Type[User]:
        """User login

        Parameters
        ----------
        username : str
            The username of the user
        password : str
            The password of the user

        Returns
        -------
        User
            The user object on success
        """

        with self._session as session:

            try:
                candidate = session.query(User).filter(User.username == username).first()

                if not candidate:
                    raise Exception('User not found.')

                if not verify_password(password, candidate.password):
                    raise ValueError('Invalid password.')

                activity = Activity(user_id=candidate.id,
                                    summary=f'User {candidate.username} logged in',
                                    created=datetime.now())

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return candidate

    def change_password(self, user_id: int, old_password: str, new_password, repassword: str) -> Type[User]:
        """Change user password

        Parameters
        ----------
        user_id : int
            The id of the user
        old_password : str
            The old password of the user
        new_password : str
            The new password of the user
        repassword : str
            The new password of the user repeated

        Returns
        -------
        User
            The user object on success
        """

        user = self.get_user_by_id(user_id)

        if not user:
            raise ValueError('User not found.')

        if not verify_password(old_password, user.password):
            raise ValueError('Invalid password.')

        if new_password != repassword:
            raise ValueError('The new passwords do not match.')

        new_password = hash_password(new_password)
        user.password = new_password
        user.modified = str(datetime.now())

        with self._session as session:

            try:
                activity = Activity(user_id=user.id,
                                    summary=f'User {user.username} changed their password',
                                    created=datetime.now())

                session.add(user)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user

        Parameters
        ----------
        user_id : int
            The id of the user to delete

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:

            try:
                user = session.query(User).filter(User.id == user_id).first()

                if not user:
                    raise ValueError('User not found.')

                activity = Activity(user_id=self._owner.id,
                                    summary=f'User {user.username} deleted by {self._owner.username}',
                                    created=datetime.now())

                session.delete(user)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_user_by_id(self, user_id: int) -> Type[User] | None:
        """Get a user by id

        Parameters
        ----------
        user_id : int
            The id of the user to get

        Returns
        -------
        User
            The user
        """

        with self._session as session:
            user = session.query(User).filter(User.id == user_id).first()

            if user:
                return user

            return None

    def get_user_by_uuid(self, user_uuid: str) -> Type[User] | None:
        """Get a user by uuid

        Parameters
        ----------
        user_uuid : str
            The uuid of the user to get

        Returns
        -------
        User
            The user
        """

        with self._session as session:
            user = session.query(User).filter(User.uuid == user_uuid).first()

            if user:
                return user

            return None

    def get_user_by_username(self, username: str) -> Type[User] | None:
        """Get a user by username

        Parameters
        ----------
        username : str
            The username of the user to get

        Returns
        -------
        User
            The user
        """

        with self._session as session:
            user = session.query(User).filter(User.username == username).first()

            if user:
                return user

            return None

    def get_user_by_email(self, email: str) -> Type[User] | None:
        """Get a user by email

        Parameters
        ----------
        email : str
            The email of the user to get

        Returns
        -------
        User
            The user
        """

        with self._session as session:
            user = session.query(User).filter(User.email == email).first()

            if user:
                return user

            return None

    def get_user_count(self) -> int:
        """Get user count

        Returns
        -------
        int
            The number of users
        """

        with self._session as session:
            return session.query(func.count(User.id)).scalar()

    def get_all_users(self) -> list:
        """Get all users

        Returns
        -------
        list
            A list of users
        """

        with self._session as session:
            return session.query(User).all()

    def get_users_page(self, page: int, per_page: int) -> list:
        """Get a single page of users from the database

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of users
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(User).offset(offset).limit(per_page).all()

    def search_users(self, search: str) -> list:
        """Search for users by username or email

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of users
        """

        with self._session as session:
            return session.query(User).filter(
                User.username.like(f'%{search}%') | User.email.like(f'%{search}%')
            ).all()
