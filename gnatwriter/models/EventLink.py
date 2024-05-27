from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from gnatwriter.models import User, Event, Link, Base


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
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('events.id'), primary_key=True
    )
    link_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('links.id'), primary_key=True
    )
    created: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now())
    )
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
