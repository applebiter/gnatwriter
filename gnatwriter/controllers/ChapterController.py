import os
from configparser import ConfigParser
from datetime import datetime
from typing import Type, List
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from gnatwriter.controllers import BaseController
from gnatwriter.models import User, Chapter, Activity, Scene, Link, ChapterLink, Note, ChapterNote


class ChapterController(BaseController):
    """Chapter controller encapsulates chapter management functionality

    Attributes
    ----------
    _instance : ChapterController
        The instance of the chapter controller
    _config: ConfigParser
        The configuration parser
    _owner : User
        The current user of the chapter controller

    Methods
    -------
    create_chapter(story_id: int, title: str, description: str)
        Create a new chapter
    update_chapter(chapter_id: int, title: str, description: str)
        Update a chapter
    delete_chapter(chapter_id: int)
        Delete a chapter
    change_chapter_position(chapter_id: int, position: int)
        Set the position of a chapter
    get_chapter_by_id(chapter_id: int)
        Get a chapter by id
    get_all_chapters()
        Get all chapters associated with a user
    get_chapters_page(page: int, per_page: int)
        Get a single page of chapters from the database associated with a user
    get_all_chapters_by_story_id(story_id: int)
        Get all chapters associated with a story
    get_chapters_page_by_story_id(story_id: int, page: int, per_page: int)
        Get a single page of chapters associated with a story from the database
    count_chapters_by_story_id(story_id: int)
        Get chapter count associated with a story
    search_chapters(search: str)
        Search for chapters by title and description belonging to a specific user
    search_chapters_by_story_id(story_id: int, search: str)
        Search for chapters by title and description belonging to a specific story
    has_scenes(chapter_id: int)
        Check if a chapter has scenes
    get_scene_by_position(chapter_id: int, position: int)
        Get a scene by position
    get_all_scenes_by_chapter_id(chapter_id: int)
        Get all scenes associated with a chapter
    append_links_to_chapter(chapter_id: int, links: list)
        Append links to a chapter
    get_links_by_chapter_id(chapter_id: int)
        Get all links associated with a chapter
    append_notes_to_chapter(chapter_id: int, notes: list)
        Append notes to a chapter
    get_notes_by_chapter_id(chapter_id: int)
        Get all notes associated with a chapter
    """

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_chapter(
        self, story_id: int, title: str, description: str = None
    ) -> Chapter:
        """Create a new chapter

        Parameters
        ----------
        story_id : int
            The id of the story
        title : str
            The title of the chapter
        description : str
            The description of the chapter, optional

        Returns
        -------
        Chapter
            The new chapter object
        """

        with self._session as session:

            try:

                title_exists = session.query(Chapter).filter(
                    Chapter.title == title, Chapter.story_id == story_id, Chapter.user_id == self._owner.id
                ).first()

                if title_exists:
                    raise Exception('This story already has a chapter with the same title.')

                position = session.query(func.max(Chapter.position)).filter(
                    Chapter.story_id == story_id, Chapter.user_id == self._owner.id
                ).scalar()
                position = int(position) + 1 if position else 1
                created = datetime.now()
                modified = created

                chapter = Chapter(
                    user_id=self._owner.id, story_id=story_id,
                    position=position, title=title, description=description,
                    created=created, modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Chapter \
                    {chapter.title[:50]} created by {self._owner.username}',
                    created=datetime.now()
                )

                session.add(chapter)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return chapter

    def update_chapter(
        self, chapter_id: int, title: str, description: str = None
    ) -> Type[Chapter]:
        """Update a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter to update
        title : str
            The title of the chapter
        description : str
            The description of the chapter, optional

        Returns
        -------
        Chapter
            The updated chapter object
        """

        with self._session as session:

            try:

                chapter = session.query(Chapter).filter(
                    Chapter.id == chapter_id,
                    Chapter.user_id == self._owner.id
                ).first()

                if not chapter:
                    raise ValueError('Chapter not found.')

                title_exists = session.query(Chapter).filter(
                    Chapter.title == title,
                    Chapter.story_id == chapter.story_id,
                    Chapter.user_id == self._owner.id
                ).first()

                if title_exists:
                    raise Exception('This story already has a chapter with the \
                    same title.')

                chapter.title = title
                chapter.description = description
                chapter.modified = str(datetime.now())

                activity = Activity(
                    user_id=self._owner.id, summary=f'Chapter {chapter.title} \
                    updated by {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return chapter

    def delete_chapter(self, chapter_id: int) -> bool:
        """Delete a chapter

        Each Chapter contains an arbitrary number of Scene objects, but before those Scenes can be deleted, the links
        and notes associated with them through the LinkScene and LinkNote objects must be deleted before deleting those
        associations. Next, the scenes are deleted. Before the Chapter can be deleted, the links, notes, and joining
        associations among the ChapterLink and NoteLink objects must be deleted. The last task to perform before the
        Chapter can be deleted is to fix the hole in the position scheme its deletion is going to leave. To do that,
        we'll decrement by 1 the position for each sibling chapter sharing the same story id and having a position that
        is greater than that of the Chapter being deleted. Finally, the Chapter is deleted.

        Parameters
        ----------
        chapter_id : int
            The id of the chapter to delete

        Returns
        -------
        bool
            True if the chapter was deleted, False if not
        """

        config = ConfigParser()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config.read(f"{project_root}/config.cfg")

        with self._session as session:

            try:

                chapter = session.query(Chapter).filter(
                    Chapter.id == chapter_id,
                    Chapter.user_id == self._owner.id
                ).first()

                if not chapter:
                    raise ValueError('Chapter not found.')

                siblings = session.query(Chapter).filter(
                    Chapter.story_id == chapter.story_id,
                    Chapter.user_id == self._owner.id,
                    Chapter.position > chapter.position
                ).all()

                for sibling in siblings:
                    sibling.position -= 1
                    sibling.created = datetime.strptime(
                        str(sibling.created),
                        config.get("formats", "datetime")
                    )
                    sibling.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Chapter {chapter.title} \
                    deleted by {self._owner.username}', created=datetime.now()
                )

                session.delete(chapter)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def change_chapter_position(
        self, chapter_id: int, position: int
    ) -> Type[Chapter]:
        """Set the position of a chapter

        First, determine whether the new position is closer to 1 or further from 1. If closer to one, get all sibling
        chapters with positions greater than or equal to the new position but less than the current position, and
        increment those position values by 1. If the target position is further away from 1 than the current position,
        get all sibling chapters with positions greater than the current position but less than or equal to the new
        position, and decrement those position values by 1. Finally, set the position of the target chapter to the new
        position. Return the new position.

        Parameters
        ----------
        chapter_id : int
            The id of the chapter to update
        position : int
            The position of the chapter

        Returns
        -------
        Chapter
            The updated chapter object
        """

        config = ConfigParser()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config.read(f"{project_root}/config.cfg")

        with self._session as session:

            try:

                chapter = session.query(Chapter).filter(
                    Chapter.id == chapter_id,
                    Chapter.user_id == self._owner.id
                ).first()

                if not chapter:
                    raise ValueError('Chapter not found.')

                if position < 1:
                    raise ValueError('Position must be greater than 0.')

                highest_position = session.query(
                    func.max(Chapter.position)
                ).filter(
                    Chapter.story_id == chapter.story_id,
                    Chapter.user_id == self._owner.id
                ).scalar()

                if position > highest_position:
                    raise ValueError(f'Position must be less than or equal to \
                    {highest_position}.')

                if position == chapter.position:
                    return chapter.position

                if position < chapter.position:
                    siblings = session.query(Chapter).filter(
                        Chapter.story_id == chapter.story_id,
                        Chapter.user_id == self._owner.id,
                        Chapter.position >= position,
                        Chapter.position < chapter.position
                    ).all()

                    for sibling in siblings:
                        sibling.position += 1
                        sibling.created = datetime.strptime(
                            str(sibling.created),
                            config.get("formats", "datetime")
                        )
                        sibling.modified = datetime.now()

                else:
                    siblings = session.query(Chapter).filter(
                        Chapter.story_id == chapter.story_id,
                        Chapter.user_id == self._owner.id,
                        Chapter.position > chapter.position,
                        Chapter.position <= position
                    ).all()

                    for sibling in siblings:
                        sibling.position -= 1
                        sibling.created = datetime.strptime(
                            str(sibling.created),
                            config.get("formats", "datetime")
                        )
                        sibling.modified = datetime.now()

                chapter.position = position
                chapter.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Chapter \
                    {chapter.title[:50]} position changed by \
                    {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return chapter

    def get_chapter_by_id(self, chapter_id: int) -> Type[Chapter] | None:
        """Get a chapter by id

        Parameters
        ----------
        chapter_id : int
            The id of the chapter to get

        Returns
        -------
        Chapter | None
            The chapter object or None if not found
        """

        with self._session as session:

            chapter = session.query(Chapter).filter(
                Chapter.id == chapter_id,
                Chapter.user_id == self._owner.id
            ).first()

            return chapter if chapter else None

    def get_all_chapters(self) -> List[Type[Chapter]]:
        """Get all chapters associated with a user

        Chapters are sorted by story id and position.

        Returns
        -------
        list | None
            A list of chapter objects or None if none are found
        """

        with self._session as session:

            return session.query(Chapter).filter(
                Chapter.user_id == self._owner.id
            ).order_by(Chapter.story_id, Chapter.position).all()

    def get_all_chapters_page(
        self, page: int, per_page: int
    ) -> List[Type[Chapter]]:
        """Get a single page of chapters from the database associated with a user

        Chapters are sorted by story id and position.

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list | None
            A list of chapter objects or None if none are found
        """

        with self._session as session:

            offset = (page - 1) * per_page

            return session.query(Chapter).filter(
                Chapter.user_id == self._owner.id
            ).order_by(
                Chapter.story_id, Chapter.position
            ).offset(offset).limit(per_page).all()

    def get_chapters_by_story_id(self, story_id: int) -> List[Type[Chapter]]:
        """Get all chapters associated with a story

        The returned list will be sorted by the position.

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list } None
            A list of chapter objects or None if none are found
        """

        with self._session as session:

            return session.query(Chapter).filter(
                Chapter.story_id == story_id,
                Chapter.user_id == self._owner.id
            ).order_by(Chapter.position).all()

    def get_chapters_page_by_story_id(
        self, story_id: int, page: int, per_page: int
    ) -> List[Type[Chapter]] | None:
        """Get a single page of chapters associated with a story from the database

        The returned list will be sorted by the position.

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
        list | None
            A list of chapter objects or None if none are found
        """

        with self._session as session:

            offset = (page - 1) * per_page

            return session.query(Chapter).filter(
                Chapter.story_id == story_id,
                Chapter.user_id == self._owner.id
            ).order_by(
                Chapter.position
            ).offset(offset).limit(per_page).all()

    def count_chapters_by_story_id(self, story_id: int) -> int:
        """Get chapter count associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        int
            The number of chapters
        """

        with self._session as session:

            return session.query(func.count(Chapter.id)).filter(
                Chapter.story_id == story_id,
                Chapter.user_id == self._owner.id
            ).scalar()

    def search_chapters(self, search: str) -> List[Type[Chapter]]:
        """Search for chapters by title and description belonging to a specific user

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of chapter objects
        """

        with self._session as session:

            return session.query(Chapter).filter(
                or_(
                    Chapter.title.like(f'%{search}%'),
                    Chapter.description.like(f'%{search}%')
                ),
                Chapter.user_id == self._owner.id
            ).all()

    def search_chapters_by_story_id(
        self, story_id: int, search: str
    ) -> List[Type[Chapter]]:
        """Search for chapters by title and description belonging to a specific story

        Parameters
        ----------
        story_id : int
            The id of the story
        search : str
            The search string

        Returns
        -------
        list
            A list of chapter objects
        """

        with self._session as session:

            return session.query(Chapter).filter(
                or_(
                    Chapter.title.like(f'%{search}%'),
                    Chapter.description.like(f'%{search}%')
                ),
                Chapter.story_id == story_id,
                Chapter.user_id == self._owner.id
            ).all()

    def has_scenes(self, chapter_id: int) -> bool:
        """Check if a chapter has scenes

        Parameters
        ----------
        chapter_id : int
            The id of the chapter

        Returns
        -------
        bool
            True if the chapter has scenes, False if not
        """

        with self._session as session:

            return session.query(Scene).filter(
                Scene.chapter_id == chapter_id,
                Scene.user_id == self._owner.id
            ).count() > 0

    def get_scene_by_position(
        self, chapter_id: int, position: int
    ) -> Type[Scene] | None:
        """Get a scene by position

        Parameters
        ----------
        chapter_id : int
            The id of the chapter
        position : int
            The position of the scene

        Returns
        -------
        Scene | None
            The scene object or None if not found
        """

        with self._session as session:

            scene = session.query(Scene).filter(
                Scene.chapter_id == chapter_id,
                Scene.position == position,
                Scene.user_id == self._owner.id
            ).first()

            return scene if scene else None

    def get_all_scenes_by_chapter_id(
        self, chapter_id: int
    ) -> List[Type[Scene]]:
        """Get all scenes associated with a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:

            return session.query(Scene).filter(
                Scene.chapter_id == chapter_id,
                Scene.user_id == self._owner.id
            ).order_by(Scene.position).all()

    def append_links_to_chapter(
        self, chapter_id: int, link_ids: list
    ) -> Type[Chapter]:
        """Append links to a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter
        link_ids : list
            A list of link ids

        Returns
        -------
        Chapter
            The updated chapter object
        """

        with self._session as session:

            try:

                chapter = session.query(Chapter).filter(
                    Chapter.id == chapter_id,
                    Chapter.user_id == self._owner.id
                ).first()

                if not chapter:
                    raise ValueError('Chapter not found.')

                for link_id in link_ids:
                    link = session.query(Link).filter(Link.id == link_id).first()

                    if not link:
                        raise ValueError('Link not found.')

                    chapter_link = ChapterLink(
                        user_id=self._owner.id, story_id=chapter.story_id,
                        chapter_id=chapter_id, link_id=link_id,
                        created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Link \
                        {link.title[:50]} associated with chapter \
                        {chapter.title[:50]} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.add(chapter_link)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return chapter

    def get_links_by_chapter_id(self, chapter_id: int) -> List[Type[Link]]:
        """Get all links associated with a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:

            return session.query(Link).join(
                ChapterLink, Link.id == ChapterLink.link_id
            ).filter(
                ChapterLink.chapter_id == chapter_id,
                ChapterLink.user_id == self._owner.id
            ).all()

    def append_notes_to_chapter(
            self, chapter_id: int, note_ids: list
    ) -> Type[Chapter]:
        """Append notes to a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter
        note_ids : list
            A list of note ids

        Returns
        -------
        Chapter
            The updated chapter object
        """

        with self._session as session:

            try:

                chapter = session.query(Chapter).filter(
                    Chapter.id == chapter_id,
                    Chapter.user_id == self._owner.id
                ).first()

                if not chapter:
                    raise ValueError('Chapter not found.')

                for note_id in note_ids:
                    note = session.query(Note).filter(
                        Note.id == note_id,
                        Note.user_id == self._owner.id
                    ).first()

                    if not note:
                        raise ValueError('Note not found.')

                    chapter_note = ChapterNote(
                        user_id=self._owner.id, story_id=chapter.story_id,
                        chapter_id=chapter_id, note_id=note_id,
                        created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Note\
                        {note.title[:50]} associated with chapter \
                        {chapter.title[:50]} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.add(chapter_note)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return chapter

    def get_notes_by_chapter_id(self, chapter_id: int) -> List[Type[Note]]:
        """Get all notes associated with a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:

            return session.query(Note).join(
                ChapterNote, Note.id == ChapterNote.note_id
            ).filter(
                ChapterNote.chapter_id == chapter_id,
                ChapterNote.user_id == self._owner.id
            ).all()
