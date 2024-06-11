from configparser import ConfigParser
from datetime import datetime, date
from typing import Type, List
from sqlalchemy.orm import Session
from gnatwriter.controllers.BaseController import BaseController
from gnatwriter.models import User, Submission, Activity


class SubmissionController(BaseController):
    """Submission controller encapsulates submission management functionality

    Attributes
    ----------
    _instance : SubmissionController
        The instance of the submission controller
    _config: ConfigParser
        The configuration parser
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
    delete_submission_by_id(submission_id: int)
        Delete a submission
    get_all_submissions()
        Get all submissions associated with an owner
    get_all_submissions_page(page: int, per_page: int)
        Get a single page of submissions associated with an owner from the database
    get_submissions_by_story_id(story_id: int)
        Get all submissions associated with a story
    get_submissions_page_by_story_id(story_id: int, page
        Get a single page of submissions associated with a story from the database
    """

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_submission(
        self, story_id: int, submitted_to: str, date_sent: str = None,
        date_reply_received: str = None, date_published: str = None,
        date_paid: str = None, result: str = None, amount: float = None
    ) -> Submission:
        """Create a new submission

        Parameters
        ----------
        story_id : int
            The id of the story
        submitted_to : str
            The entity the story was submitted to
        date_sent : str
            The date the story was submitted, optional
        date_reply_received : str
            The date the reply was received
        date_published : str
            The date the story was published
        date_paid : str
            The date on which the story was paid
        result : str
            The result of the submission
        amount : float
            The amount paid for the submission

        Returns
        -------
        Submission
            The new submission object
        """

        with (self._session as session):

            try:

                created = datetime.now()
                modified = created

                submission = Submission(
                    user_id=self._owner.id, story_id=story_id,
                    submitted_to=submitted_to, date_sent=date_sent,
                    date_reply_received=date_reply_received,
                    date_published=date_published, date_paid=date_paid,
                    result=result, amount=amount, created=created,
                    modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Submission \
                    {submission.id} created by {self._owner.username}',
                    created=datetime.now()
                )

                session.add(submission)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return submission

    def update_submission(
        self, submission_id: int, submitted_to: str, date_sent: str = None,
        date_reply_received: str = None, date_published: str = None,
        date_paid: str = None, result: str = None, amount: float = None
    ) -> Type[Submission]:
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
            The date on which the story was paid
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
                submission = session.query(Submission).filter(
                    Submission.id == submission_id,
                    Submission.user_id == self._owner.id
                ).first()

                if not submission:
                    raise ValueError('Submission not found.')

                submission.submitted_to = submitted_to
                submission.date_sent = date_sent
                submission.date_reply_received = date_reply_received
                submission.date_published = date_published
                submission.date_paid = date_paid
                submission.result = result
                submission.amount = amount

                activity = Activity(
                    user_id=self._owner.id, summary=f'Submission \
                    {submission.id} updated by {self._owner.username}',
                    created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return submission

    def delete_submission_by_id(self, submission_id: int) -> bool:
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
                submission = session.query(Submission).filter(
                    Submission.id == submission_id,
                    Submission.user_id == self._owner.id
                ).first()

                if not submission:
                    raise ValueError('Submission not found.')

                activity = Activity(
                    user_id=self._owner.id, summary=f'Submission \
                    {submission.id} deleted by {self._owner.username}',
                    created=datetime.now()
                )

                session.delete(submission)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_submission_by_id(self, submission_id: int) -> Type[Submission]:
        """Get a submission by id

        Parameters
        ----------
        submission_id : int
            The id of the submission

        Returns
        -------
        Submission
            The submission object
        """

        with self._session as session:
            return session.query(Submission).filter(
                Submission.id == submission_id,
                Submission.user_id == self._owner.id
            ).first()

    def get_all_submissions(self) -> List[Type[Submission]]:
        """Get all submissions associated with an owner

        Returns
        -------
        list
            A list of submission objects
        """

        with self._session as session:

            return session.query(Submission).filter(
                Submission.user_id == self._owner.id
            ).all()

    def get_all_submissions_page(
        self, page: int, per_page: int
    ) -> List[Type[Submission]]:
        """Get a single page of submissions associated with an owner from the database

        Parameters
        ----------
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
                Submission.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def get_submissions_by_story_id(
        self, story_id: int
    ) -> List[Type[Submission]]:
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
            return session.query(Submission).filter(
                Submission.story_id == story_id,
                Submission.user_id == self._owner.id
            ).all()

    def get_submissions_page_by_story_id(
        self, story_id: int, page: int, per_page: int
    ) -> List[Type[Submission]]:
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
                Submission.story_id == story_id,
                Submission.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()
