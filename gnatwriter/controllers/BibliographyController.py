from configparser import ConfigParser
from datetime import datetime
from typing import Type, List
from sqlalchemy import func
from sqlalchemy.orm import Session
from gnatwriter.controllers.BaseController import BaseController
from gnatwriter.models import User, Bibliography, Activity


class BibliographyController(BaseController):
    """Bibliography controller encapsulates bibliography management functionality

    Attributes
    ----------
    _config : ConfigParser
        The configuration parser
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

    def __init__(
            self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_bibliography(
        self, story_id: int, title: str, pages: str = None,
        publication_date: str = None, other_text: str = None
    ) -> Bibliography:
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
                    Bibliography.title == title,
                    Bibliography.story_id == story_id,
                    Bibliography.user_id == self._owner.id
                ).first()

                if title_exists:
                    raise Exception('A reference with the same title is already \
                        associated with that story.')

                created = datetime.now()
                modified = created

                bibliography = Bibliography(
                    user_id=self._owner.id, story_id=story_id, title=title,
                    pages=pages, publication_date=publication_date,
                    other_text=other_text, created=created, modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Bibliography \
                    {bibliography.title[:50]} created by \
                    {self._owner.username}', created=datetime.now()
                )

                session.add(bibliography)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return bibliography

    def update_bibliography(
        self, bibliography_id: int, story_id: int, title: str,
        pages: str = None, publication_date: str = None, other_text: str = None
    ) -> Type[Bibliography]:
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
                    Bibliography.id == bibliography_id,
                    Bibliography.user_id == self._owner.id
                ).first()

                if not bibliography:
                    raise ValueError('Bibliography not found.')

                title_exists = session.query(Bibliography).filter(
                    Bibliography.title == title,
                    Bibliography.story_id == story_id
                ).first()

                if title_exists:
                    raise Exception('A reference with the same title is already\
                     associated with that story.')

                bibliography.story_id = story_id
                bibliography.title = title
                bibliography.pages = pages
                bibliography.publication_date = publication_date
                bibliography.other_text = other_text
                bibliography.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Bibliography \
                    {bibliography.title} updated by {self._owner.username}',
                    created=datetime.now()
                )

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
                    Bibliography.id == bibliography_id,
                    Bibliography.user_id == self._owner.id
                ).first()

                if not bibliography:
                    raise ValueError('Bibliography not found.')

                activity = Activity(
                    user_id=self._owner.id, summary=f'Bibliography \
                    {bibliography.title} deleted by {self._owner.username}',
                    created=datetime.now()
                )

                session.delete(bibliography)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_bibliography_by_id(
        self, bibliography_id: int
    ) -> Type[Bibliography] | None:
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
                Bibliography.id == bibliography_id,
                Bibliography.user_id == self._owner.id
            ).first()

            return bibliography if bibliography else None

    def get_bibliography_by_title(
        self, title: str
    ) -> Type[Bibliography] | None:
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
                Bibliography.title == title,
                Bibliography.user_id == self._owner.id
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

            return session.query(func.count(Bibliography.id)).filter(
                Bibliography.user_id == self._owner.id
            ).scalar()

    def get_all_bibliographies(self) -> List[Type[Bibliography]]:
        """Get all bibliographies associated with a user

        Returns
        -------
        list
            A list of bibliography objects
        """

        with self._session as session:

            return session.query(Bibliography).filter(
                Bibliography.user_id == self._owner.id
            ).all()

    def get_bibliographies_page(
        self, page: int, per_page: int
    ) -> List[Type[Bibliography]]:
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

    def get_bibliographies_by_story_id(
        self, story_id: int
    ) -> List[Type[Bibliography]]:
        """Get all bibliographies associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of bibliography objects
        """

        with self._session as session:

            bibliographies = session.query(Bibliography).filter(
                Bibliography.story_id == story_id,
                Bibliography.user_id == self._owner.id
            ).all()

            return bibliographies if bibliographies else None

    def get_bibliographies_page_by_story_id(
        self, story_id: int, page: int, per_page: int
    ) -> List[Type[Bibliography]]:
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
        list
            A list of bibliography objects
        """

        with self._session as session:

            offset = (page - 1) * per_page

            bibliographies = session.query(Bibliography).filter(
                Bibliography.story_id == story_id,
                Bibliography.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

            return bibliographies if bibliographies else None

    def search_bibliographies(self, search: str) -> List[Type[Bibliography]]:
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
                Bibliography.title.like(f'%{search}%'),
                Bibliography.user_id == self._owner.id
            ).all()

    def search_bibliographies_by_story_id(
        self, story_id: int, search: str
    ) -> List[Type[Bibliography]]:
        """Search for bibliographies by title associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story
        search : str
            The search string

        Returns
        -------
        list
            A list of bibliography objects
        """

        with self._session as session:

            return session.query(Bibliography).filter(
                Bibliography.story_id == story_id,
                Bibliography.title.like(f'%{search}%'),
                Bibliography.user_id == self._owner.id
            ).all()
