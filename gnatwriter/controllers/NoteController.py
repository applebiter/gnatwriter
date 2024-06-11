from configparser import ConfigParser
from datetime import datetime
from typing import Type, List
from sqlalchemy import or_
from sqlalchemy.orm import Session
from gnatwriter.controllers.BaseController import BaseController
from gnatwriter.models import User, Note, Activity


class NoteController(BaseController):
    """Note controller encapsulates note management functionality

    Attributes
    ----------
    _instance : NoteController
        The instance of the note controller
    _config: ConfigParser
        The configuration parser
    _owner : User
        The current user of the note controller
    _session : Session
        The database session

    Methods
    -------
    create_note(title: str, content: str)
        Create a new note
    update_note(note_id: int, title: str, content: str)
        Update a note
    delete_note(note_id: int)
        Delete a note
    get_all_notes()
        Get all notes associated with an owner
    get_all_notes_page(page: int, per_page: int)
        Get a single page of notes associated with an owner from the database
    search_notes(search: str)
        Search for notes by title and content
    """

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_note(self, title: str, content: str) -> Note:
        """Create a new note

        Parameters
        ----------
        title : str
            The title of the note
        content : str
            The content of the note

        Returns
        -------
        Note
            The new note object
        """

        with self._session as session:

            try:

                created = datetime.now()
                modified = created

                note = Note(
                    user_id=self._owner.id, title=title, content=content,
                    created=created, modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Note {note.title[:50]} \
                    created by {self._owner.username}', created=datetime.now()
                )

                session.add(note)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return note

    def update_note(self, note_id: int, title: str, content: str) -> Type[Note]:
        """Update a note

        Parameters
        ----------
        note_id : int
            The id of the note
        title : str
            The title of the note
        content : str
            The content of the note

        Returns
        -------
        Note
            The updated note object
        """

        with self._session as session:
            try:
                note = session.query(Note).filter(
                    Note.id == note_id, Note.user_id == self._owner.id
                ).first()

                if not note:
                    raise ValueError('Note not found.')

                note.title = title
                note.content = content
                note.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Note {note.id} updated \
                    by {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return note

    def delete_note(self, note_id: int) -> bool:
        """Delete a note

        Parameters
        ----------
        note_id : int
            The id of the note

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                note = session.query(Note).filter(
                    Note.id == note_id,
                    Note.user_id == self._owner.id
                ).first()

                if not note:
                    raise ValueError('Note not found.')

                activity = Activity(
                    user_id=self._owner.id, summary=f'Note {note.id} deleted \
                    by {self._owner.username}', created=datetime.now()
                )

                session.delete(note)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_note_by_id(self, note_id: int) -> Type[Note] | None:
        """Get a note by id

        Parameters
        ----------
        note_id : int
            The id of the note

        Returns
        -------
        Note
            The note object
        """

        with self._session as session:
            return session.query(Note).filter(
                Note.id == note_id,
                Note.user_id == self._owner.id
            ).first()

    def get_all_notes(self) -> List[Type[Note]]:
        """Get all notes associated with an owner

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            return session.query(Note).filter(
                Note.user_id == self._owner.id
            ).all()

    def get_all_notes_page(self, page: int, per_page: int) -> List[Type[Note]]:
        """Get a single page of notes associated with an owner from the database

        Parameters
        ----------
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
            return session.query(Note).filter(
                Note.owner_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def search_notes(self, search: str) -> List[Type[Note]]:
        """Search for notes by title and content

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            return session.query(Note).filter(
                or_(
                    Note.title.like(f'%{search}%'),
                    Note.content.like(f'%{search}%')
                ),
                Note.user_id == self._owner.id
            ).all()
