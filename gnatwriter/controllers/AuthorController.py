from configparser import ConfigParser
from datetime import datetime
from typing import Type, List
from sqlalchemy import func
from sqlalchemy.orm import Session
from gnatwriter.controllers.BaseController import BaseController
from gnatwriter.models import User, Author, Activity, Story


class AuthorController(BaseController):
    """Author controller encapsulates author management functionality

    Attributes
    ----------
    _instance : AuthorController
        The instance of the author controller
    _config : ConfigParser
        The configuration parser
    _session : Session
        The database session object
    _owner : User
        The current user of the controller

    Methods
    -------
    create_author(name: str, initials: str, is_pseudonym: bool)
        Create a new author
    update_author(author_id: int, name: str, initials: str)
        Update an author
    delete_author_by_id(author_id: int)
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

    def __init__(
            self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_author(
        self, name: str, initials: str = None, is_pseudonym: bool = False
    ) -> Author:
        """Create a new author

        Parameters
        ----------
        name : str
            The name of the new author
        initials : str
            The initials of the new author, optional
        is_pseudonym : bool
            Whether the author is a pseudonym, optional, default is False, suggesting it is the user's actual name

        Returns
        -------
        Author
            The new author object
        """

        with self._session as session:

            try:

                name_exists = session.query(Author).filter(
                    Author.name == name,
                    Author.user_id == self._owner.id
                ).first()

                if name_exists:
                    raise Exception('That author already exists.')

                created = datetime.now()
                modified = created

                author = Author(
                    user_id=self._owner.id, name=name, initials=initials,
                    is_pseudonym=is_pseudonym, created=created,
                    modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Author {author.name} \
                    created by {self._owner.username}', created=datetime.now()
                )

                session.add(author)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return author

    def update_author(
        self, author_id: int, name: str, initials: str = None,
        is_pseudonym: bool = False
    ) -> Type[Author]:
        """Update an author

        Parameters
        ----------
        author_id : int
            The id of the author to update
        name : str
            The name of the author
        initials : str
            The initials of the author, optional
        is_pseudonym : bool
            Whether the author is a pseudonym, optional, default is False

        Returns
        -------
        Author
            The updated author object
        """

        with self._session as session:

            try:

                author = session.query(Author).filter(
                    Author.id == author_id,
                    Author.user_id == self._owner.id
                ).first()

                if not author:
                    raise ValueError('Author not found.')

                author.name = name
                author.initials = initials
                author.is_pseudonym = is_pseudonym
                author.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Author {author.name} \
                    updated by {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return author

    def delete_author_by_id(self, author_id: int) -> bool:
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
                    Author.id == author_id,
                    Author.user_id == self._owner.id
                ).first()

                if not author:
                    raise ValueError('Author not found.')

                activity = Activity(
                    user_id=self._owner.id, summary=f'Author {author.name} \
                    deleted by {self._owner.username}', created=datetime.now()
                )

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
                Author.id == author_id,
                Author.user_id == self._owner.id
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
                Author.name == name,
                Author.user_id == self._owner.id
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

            return session.query(func.count(Author.id)).filter(
                Author.user_id == self._owner.id
            ).scalar()

    def get_all_authors(self) -> List[Type[Author]]:
        """Get all authors associated with a user

        Returns
        -------
        list
            A list of author objects
        """

        with self._session as session:

            return session.query(Author).filter(
                Author.user_id == self._owner.id
            ).all()

    def get_authors_page(self, page: int, per_page: int) -> list:
        """Get a single page of authors from the database associated with a user

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of author objects
        """

        with self._session as session:

            offset = (page - 1) * per_page

            return session.query(Author).filter(
                Author.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def get_authors_by_story_id(
        self, story_id: int
    ) -> List[Type[Author]] | None:
        """Get all authors associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list | None
            A list of author objects or None if not found
        """

        with self._session as session:

            story = session.query(Story).filter(
                Story.id == story_id,
                Story.user_id == self._owner.id
            ).first()

            authors = []

            if story:
                for author_story in story.authors:
                    authors.append(author_story.author)

            return authors if authors else None

    def search_authors(self, search: str) -> List[Type[Author]]:
        """Search for authors by name

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of author objects
        """

        with self._session as session:

            return session.query(Author).filter(
                Author.name.like(f'%{search}%'),
                Author.user_id == self._owner.id
            ).all()
