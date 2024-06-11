from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Text, Date, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import SubmissionResultType, User, Story, Base


class Submission(Base):
    """The Submission class represents a submission of a story to some publisher or contest.

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
