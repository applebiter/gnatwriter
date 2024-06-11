from configparser import ConfigParser
from datetime import datetime
from typing import Type, List
from sqlalchemy.orm import Session
from gnatwriter.controllers.BaseController import BaseController
from gnatwriter.models import User, Link, Activity, LinkStory


class LinkController(BaseController):
    """Link controller encapsulates link management functionality

    Attributes
    ----------
    _instance : LinkController
        The instance of the link controller
    _config: ConfigParser
        The configuration parser
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
    get_all_links()
        Get all links associated with a user
    get_all_links_page(page: int, per_page: int)
        Get a single page of links associated with a user from the database
    search_links(search: str)
        Search for links by title
    """

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

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

                link = Link(
                    user_id=self._owner.id, url=url, title=title,
                    created=created, modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Link {link.title[:50]} \
                    created by {self._owner.username}', created=datetime.now()
                )

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
                link = session.query(Link).filter(
                    Link.id == link_id,
                    Link.user_id == self._owner.id
                ).first()

                if not link:
                    raise ValueError('Link not found.')

                link.url = url
                link.title = title
                link.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Link {link.id} updated \
                    by {self._owner.username}', created=datetime.now()
                )

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
                link = session.query(Link).filter(
                    Link.id == link_id,
                    Link.user_id == self._owner.id
                ).first()

                if not link:
                    raise ValueError('Link not found.')

                activity = Activity(
                    user_id=self._owner.id, summary=f'Link {link.id} deleted \
                    by {self._owner.username}', created=datetime.now()
                )

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
            return session.query(Link).filter(
                Link.id == link_id,
                Link.user_id == self._owner.id
            ).first()

    def get_links_by_story_id(self, story_id: int) -> List[Type[Link]]:
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
            return session.query(Link).join(LinkStory).filter(
                LinkStory.story_id == story_id,
                LinkStory.user_id == self._owner.id
            ).all()

    def get_all_links(self) -> List[Type[Link]]:
        """Get all links associated with an owner

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            return session.query(Link).filter(
                Link.user_id == self._owner.id
            ).all()

    def get_all_links_page(self, page: int, per_page: int) -> List[Type[Link]]:
        """Get a single page of links associated with an owner from the database

        Parameters
        ----------
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
                Link.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def search_links(self, search: str) -> List[Type[Link]]:
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
            return session.query(Link).filter(
                Link.title.like(f'%{search}%'),
                Link.user_id == self._owner.id
            ).all()
