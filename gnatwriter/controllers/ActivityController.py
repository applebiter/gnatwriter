from configparser import ConfigParser
from typing import Type, List
from sqlalchemy import func
from sqlalchemy.orm import Session
from gnatwriter.controllers import BaseController
from gnatwriter.models import User, Activity


class ActivityController(BaseController):
    """Activity controller encapsulates activity management functionality

    Attributes
    ----------
    _instance : ActivityController
        The instance of the activity controller
    _config : configParser
        The path to the configuration file
    _session : Session
        The database session object
    _owner : Type[User]
        The current user of the controller

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
    search_activities_page(search: str, page: int, per_page: int)
        Search for activities by summary and get a single page of activities associated with a user, sorted by created
        date with most recent first
    """

    def __init__(
            self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

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
                Activity.id == activity_id,
                Activity.user_id == self._owner.id
            ).first()

            return activity if activity else None

    def get_activities(self) -> List[Type[Activity]]:
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

    def get_activities_page(
        self, page: int, per_page: int
    ) -> List[Type[Activity]]:
        """Get a single page of activities associated with a user, sorted by created date with most recent first

        Parameters
        ----------
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
                Activity.user_id == self._owner.id
            ).order_by(
                Activity.created.desc()
            ).offset(offset).limit(per_page).all()

    def get_activity_count(self) -> int:
        """Get activity count associated with a user

        Returns
        -------
        int
            The number of activities
        """

        with self._session as session:

            return session.query(func.count(Activity.id)).filter(
                Activity.user_id == self._owner.id
            ).scalar()

    def search_activities(self, search: str) -> List[Type[Activity]]:
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
                Activity.summary.like(f'%{search}%'),
                Activity.user_id == self._owner.id
            ).all()

    def search_activities_page(
        self, search: str, page: int, per_page: int
    ) -> List[Type[Activity]]:
        """Search for activities by summary and get a single page of activities associated with a user

        Parameters
        ----------
        search : str
            The search string
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
                Activity.summary.like(f'%{search}%'),
                Activity.user_id == self._owner.id
            ).order_by(
                Activity.created.desc()
            ).offset(offset).limit(per_page).all()
