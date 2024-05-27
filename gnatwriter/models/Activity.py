from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import User, Base


class Activity(Base):
    """The Activity class documents any controller endpoint activities.

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
            The system user or user currently logged in

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
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    summary: Mapped[str] = mapped_column(String(250), nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    user: Mapped["User"] = relationship(
        "User", back_populates="activities"
    )

    def __repr__(self):
        """Returns a string representation of the activity.

        Returns
        -------
        str
            A string representation of the activity
        """

        return f'<Activity {self.summary!r}>'

    def __str__(self):
        """Returns a string representation of the activity.

        Returns
        -------
        str
            A string representation of the activity
        """

        return f'{self.summary}'

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
        """Validates the summary's length.
        """

        if len(summary) > 250:
            raise ValueError(
                """The activity summary must be no more than 250 characters in length.
                """
            )

        return summary
