from configparser import ConfigParser
from datetime import datetime
from typing import Type, List
from sqlalchemy.orm import Session
from gnatwriter.controllers.BaseController import BaseController
from gnatwriter.models import User, Event, CharacterEvent, Character, Activity, Location, Link, EventLink, Note, EventNote


class EventController(BaseController):
    """Event controller encapsulates event management functionality

    Attributes
    ----------
    _instance : EventController
        The instance of the event controller
    _config : ConfigParser
        The configuration parser
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
    get_all_events()
        Get all events associated with a user
    get_all_events_page(page: int, per_page: int)
        Get a single page of events associated with a user from the database
    append_characters_to_event(event_id: int, characters: list)
        Append characters to an event
    get_characters_by_event_id(event_id: int)
        Get all characters associated with an event
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

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_event(
        self, title: str, description: str = None, start_datetime: str = None,
        end_datetime: str = None
    ) -> Event:
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

                event = Event(
                    user_id=self._owner.id, title=title, description=description,
                    start_datetime=start_datetime, end_datetime=end_datetime,
                    created=created, modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Event {event.title[:50]} \
                    created by {self._owner.username}', created=datetime.now()
                )

                session.add(event)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return event

    def update_event(
        self, event_id: int, title: str, description: str, start_datetime: str,
        end_datetime: str
    ) -> Type[Event]:
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

                activity = Activity(
                    user_id=self._owner.id, summary=f'Event {event.id} updated \
                    by {self._owner.username}', created=datetime.now()
                )

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
                    Event.id == event_id,
                    Event.user_id == self._owner.id
                ).first()

                if not event:
                    raise ValueError('Event not found.')

                activity = Activity(
                    user_id=self._owner.id, summary=f'Event {event.id} deleted \
                    by {self._owner.username}', created=datetime.now()
                )

                session.delete(event)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_all_events(self) -> List[Type[Event]]:
        """Get all events associated with a user

        Returns
        -------
        list
            A list of event objects
        """

        with self._session as session:
            return session.query(Event).filter(
                Event.user_id == self._owner.id
            ).all()

    def get_all_events_page(
        self, page: int, per_page: int
    ) -> List[Type[Event]]:
        """Get a single page of events associated with a user from the database

        Parameters
        ----------
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
                Event.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_characters_to_event(
        self, event_id: int, character_ids: list
    ) -> Type[Event]:
        """Append characters to an event

        Parameters
        ----------
        event_id : int
            The id of the event
        character_ids : list
            A list of character ids

        Returns
        -------
        Event
            The updated event object
        """

        with self._session as session:
            try:
                event = session.query(Event).filter(
                    Event.id == event_id,
                    Event.user_id == self._owner.id
                ).first()

                if not event:
                    raise ValueError('Event not found.')

                for character_id in character_ids:
                    character = session.query(Character).filter(
                        Character.id == character_id,
                        Character.user_id == self._owner.id
                    ).first()

                    if not character:
                        raise ValueError('Character not found.')

                    character_event = CharacterEvent(
                        user_id=self._owner.id, event_id=event_id,
                        character_id=character_id, created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Character \
                        {character.__str__} associated with event \
                        {event.title[:50]} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.add(character_event)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return event

    def get_characters_by_event_id(
        self, event_id: int
    ) -> List[Type[Character]]:
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
                CharacterEvent.event_id == event_id,
                    CharacterEvent.user_id == self._owner.id
            ).all():
                yield session.query(Character).filter(
                    Character.id == character_event.character_id
                ).first()

    def get_characters_page_by_event_id(
        self, event_id: int, page: int, per_page: int
    ) -> List[Type[Character]]:
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
                CharacterEvent.event_id == event_id,
                CharacterEvent.user_id == self._owner.id
            ).offset(offset).limit(per_page).all():
                yield session.query(Character).filter(
                    Character.id == character_event.character_id,
                    Character.user_id == self._owner.id
                ).first()

    def append_links_to_event(
        self, event_id: int, link_ids: list
    ) -> Type[Event]:
        """Append links to an event

        Parameters
        ----------
        event_id : int
            The id of the event
        link_ids : list
            A list of link ids

        Returns
        -------
        Event
            The updated event object
        """

        with self._session as session:
            try:
                event = session.query(Event).filter(
                    Event.id == event_id,
                    Event.user_id == self._owner.id
                ).first()

                if not event:
                    raise ValueError('Event not found.')

                for link_id in link_ids:
                    link = session.query(Link).filter(
                        Link.id == link_id,
                        Link.user_id == self._owner.id
                    ).first()

                    if not link:
                        raise ValueError('Link not found.')

                    event_link = EventLink(
                        user_id=self._owner.id, event_id=event_id,
                        link_id=link_id, created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Link\
                        {link.title[:50]} associated with event \
                        {event.title[:50]} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.add(event_link)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return event

    def get_links_by_event_id(self, event_id: int) -> List[Type[Link]]:
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
                EventLink.event_id == event_id,
                    EventLink.user_id == self._owner.id
            ).all():
                yield session.query(Link).filter(
                    Link.id == event_link.link_id,
                    Link.user_id == self._owner.id
                ).first()

    def get_links_page_by_event_id(
        self, event_id: int, page: int, per_page: int
    ) -> List[Type[Link]]:

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
                EventLink.event_id == event_id,
                EventLink.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_notes_to_event(
        self, event_id: int, note_ids: list
    ) -> Type[Event]:
        """Append notes to an event

        Parameters
        ----------
        event_id : int
            The id of the event
        note_ids : list
            A list of note ids

        Returns
        -------
        Event
            The updated event object
        """

        with self._session as session:
            try:
                event = session.query(Event).filter(
                    Event.id == event_id,
                    Event.user_id == self._owner.id
                ).first()

                if not event:
                    raise ValueError('Event not found.')

                for note_id in note_ids:
                    note = session.query(Note).filter(
                        Note.id == note_id,
                        Note.user_id == self._owner.id
                    ).first()

                    if not note:
                        raise ValueError('Note not found.')

                    event_note = EventNote(
                        user_id=self._owner.id, event_id=event_id,
                        note_id=note_id, created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Note \
                        {note.title[:50]} associated with event \
                        {event.title[:50]} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.add(event_note)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return event

    def get_notes_by_event_id(self, event_id: int) -> List[Type[Note]]:
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
                EventNote.event_id == event_id,
                    EventNote.user_id == self._owner.id
            ).all():
                yield session.query(Note).filter(
                    Note.id == event_note.note_id,
                    Note.user_id == self._owner.id
                ).first()

    def get_notes_page_by_event_id(
        self, event_id: int, page: int, per_page: int
    ) -> List[Type[Note]]:
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
                EventNote.event_id == event_id,
                EventNote.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()
