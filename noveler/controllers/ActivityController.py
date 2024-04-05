from typing import Type
from sqlalchemy import func
from sqlalchemy.orm import Session
from noveler.controllers import BaseController
from noveler.models import User, Activity


class ActivityController(BaseController):
    """Activity controller encapsulates activity management functionality

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

    def __init__(
            self, path_to_config: str, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(path_to_config, session, owner)

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

    def get_activities_page(self, page: int, per_page: int) -> list:
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
            ).order_by(Activity.created.desc()).offset(offset).limit(per_page).all()

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
                Activity.summary.like(f'%{search}%'),
                Activity.user_id == self._owner.id
            ).all()

