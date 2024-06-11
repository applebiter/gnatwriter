from configparser import ConfigParser
from datetime import datetime
from typing import Type, List
from sqlalchemy import or_
from sqlalchemy.orm import Session
from gnatwriter.controllers.BaseController import BaseController
from gnatwriter.models import User, Story, Author, AuthorStory, Chapter, Activity, Character, CharacterStory, Link, \
    LinkStory, Note, NoteStory


class StoryController(BaseController):
    """Story controller encapsulates story management functionality

    Attributes
    ----------
    _instance : StoryController
        The instance of the story controller
    _config: ConfigParser
        The configuration parser
    _owner : User
        The current user of the story controller
    _session : Session
        The database session

    Methods
    -------
    create_story(title: str, description: str)
        Create a new story
    update_story(story_id: int, title: str, description: str)
        Update a story
    delete_story(story_id: int)
        Delete a story
    has_stories() : bool
        Check if a user has stories
    count_stories()
        Count the number of stories associated with a user
    get_story_by_id(story_id: int)
        Get a story by id
    get_all_stories()
        Get all stories associated with an owner
    get_all_stories_page(page: int, per_page: int)
        Get a single page of stories associated with an owner from the database
    search_stories(search: str)
        Search for stories by title and description
    append_authors_to_story(story_id: int, author_ids: list)
        Append authors to a story
    detach_authors_from_story(story_id:int, author_ids: list)
        Detach authors from a story
    has_authors( story_id ) : bool
        Check if a story has authors
    get_authors_by_story_id(story_id: int)
        Get all authors associated with a story
    has_chapters( story_id ) : bool
        Check if a story has chapters
    get_chapter_by_position(story_id: int, position: int)
        Get a chapter by position
    get_all_chapters_by_story_id(story_id: int)
        Get all chapters associated with a story
    append_characters_to_story(story_id: int, character_ids: list)
        Append characters to a story
    has_characters( story_id ) : bool
        Check if a story has characters
    get_characters_by_story_id(story_id: int)
        Get all characters associated with a story
    get_characters_page_by_story_id(story_id: int, page: int, per_page: int)
        Get a single page of characters associated with a story from the database
    append_links_to_story(story_id: int, link_ids: list)
        Append links to a story
    has_links( story_id ) : bool
        Check if a story has links
    get_links_by_story_id(story_id: int)
        Get all links associated with a story
    append_notes_to_story(story_id: int, note_ids: list)
        Append notes to a story
    has_notes( story_id ) : bool
        Check if a story has notes
    get_notes_by_story_id(story_id: int)
        Get all notes associated with a story
    """

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_story(self, title: str, description: str = None) -> Story:
        """Create a new story

        Parameters
        ----------
        title : str
            The title of the story
        description : str
            The description of the story

        Returns
        -------
        Story
            The new story object
        """

        with self._session as session:
            try:
                created = datetime.now()
                modified = created

                story = Story(
                    user_id=self._owner.id, title=title, description=description,
                    created=created, modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Story {story.title[:50]} \
                    created by {self._owner.username}', created=datetime.now()
                )

                session.add(story)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def update_story(
        self, story_id: int, title: str, description: str = None
    ) -> Type[Story]:
        """Update a story

        Parameters
        ----------
        story_id : int
            The id of the story
        title : str
            The title of the story
        description : str
            The description of the story

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                story = session.query(Story).filter(
                    Story.id == story_id,
                    Story.user_id == self._owner.id
                ).first()

                if not story:
                    raise ValueError('Story not found.')

                story.title = title
                story.description = description
                story.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Story {story.id} updated \
                    by {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def delete_story(self, story_id: int) -> bool:
        """Delete a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                story = session.query(Story).filter(
                    Story.id == story_id,
                    Story.user_id == self._owner.id
                ).first()

                if not story:
                    raise ValueError('Story not found.')

                activity = Activity(
                    user_id=self._owner.id, summary=f'Story {story.id} deleted \
                    by {self._owner.username}', created=datetime.now()
                )

                session.delete(story)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def has_stories(self) -> bool:
        """Check if a user has stories

        Returns
        -------
        bool
            True if the user has stories
        """

        with self._session as session:

            return session.query(Story).filter(
                Story.user_id == self._owner.id
            ).count() > 0

    def count_stories(self) -> int:
        """Count the number of stories associated with a user

        Returns
        -------
        int
            The number of stories
        """

        with self._session as session:

            return session.query(Story).filter(
                Story.user_id == self._owner.id
            ).count()

    def get_story_by_id(self, story_id: int) -> Type[Story] | None:
        """Get a story by id

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        Story
            The story object
        """

        with self._session as session:
            story = session.query(Story).filter(
                Story.id == story_id,
                Story.user_id == self._owner.id
            ).first()
            return story

    def get_all_stories(self) -> List[Type[Story]]:
        """Get all stories associated with an owner

        Returns
        -------
        list
            A list of story objects
        """

        with self._session as session:
            return session.query(Story).filter(
                Story.user_id == self._owner.id
            ).all()

    def get_all_stories_page(
        self, page: int, per_page: int
    ) -> List[Type[Story]]:
        """Get a single page of stories associated with an owner from the database

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of story objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Story).filter(
                Story.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def search_stories(self, search: str) -> List[Type[Story]]:
        """Search for stories by title and description

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of story objects
        """

        with self._session as session:
            return session.query(Story).filter(
                or_(
                    Story.title.like(f'%{search}%'),
                    Story.description.like(f'%{search}%')
                ),
                Story.user_id == self._owner.id
            ).all()

    def append_authors_to_story(
        self, story_id: int, author_ids: list
    ) -> Type[Story]:
        """Append authors to a story

        Parameters
        ----------
        story_id : int
            The id of the story
        author_ids : list
            The ids of the authors to append

        Returns
        -------
        Story
            The updated story object
        """

        with self._session as session:
            try:
                story = session.query(Story).filter(
                    Story.id == story_id,
                    Story.user_id == self._owner.id
                ).first()

                if not story:
                    raise ValueError('Story not found.')

                for author_id in author_ids:
                    author = session.query(Author).filter(
                        Author.id == author_id,
                        Author.user_id == self._owner.id
                    ).first()

                    if not author:
                        raise ValueError('Author not found.')

                    author_story = session.query(AuthorStory).filter(
                        AuthorStory.user_id == self._owner.id,
                        AuthorStory.author_id == author_id,
                        AuthorStory.story_id == story_id
                    ).first()

                    if not author_story:

                        author_story = AuthorStory(
                            user_id=self._owner.id, author_id=author_id,
                            story_id=story_id, created=datetime.now()
                        )
                        story.authors.append(author_story)

                        activity = Activity(
                            user_id=self._owner.id, summary=f'Authors appended to \
                            story {story.title[:50]} by {self._owner.username}',
                            created=datetime.now()
                        )

                        session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def detach_authors_from_story(
        self, story_id: int, author_ids: list
    ) -> Type[Story]:
        """Detach authors from a story

        Parameters
        ----------
        story_id : int
            The id of the story
        author_ids : list
            The ids of the authors to detach

        Returns
        -------
        Story
            The updated story object
        """

        with self._session as session:
            try:
                story = session.query(Story).filter(
                    Story.id == story_id,
                    Story.user_id == self._owner.id
                ).first()

                if not story:
                    raise ValueError('Story not found.')

                for author_id in author_ids:
                    author = session.query(Author).filter(
                        Author.id == author_id,
                        Author.user_id == self._owner.id
                    ).first()

                    if not author:
                        raise ValueError('Author not found.')

                    author_story = session.query(AuthorStory).filter(
                        AuthorStory.user_id == self._owner.id,
                        AuthorStory.author_id == author_id,
                        AuthorStory.story_id == story_id
                    ).first()

                    if not author_story:
                        return story

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Authors detached from \
                        story {story.title[:50]} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.delete(author_story)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def has_authors(self, story_id: int) -> bool:
        """Check if a story has authors

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        bool
            True if the story has authors
        """

        with self._session as session:

            return session.query(Author).join(AuthorStory).filter(
                AuthorStory.story_id == story_id,
                AuthorStory.user_id == self._owner.id
            ).count() > 0

    def get_authors_by_story_id(self, story_id: int) -> List[Type[Author]]:
        """Get all authors associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of author objects
        """

        with self._session as session:
            return session.query(Author).join(AuthorStory).filter(
                AuthorStory.story_id == story_id,
                AuthorStory.user_id == self._owner.id
            ).all()

    def has_chapters(self, story_id: int) -> bool:
        """Check if a story has chapters

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        bool
            True if the story has chapters
        """

        with self._session as session:

            return session.query(Chapter).filter(
                Chapter.story_id == story_id,
                Chapter.user_id == self._owner.id
            ).count() > 0

    def get_chapter_by_position(
        self, story_id: int, position: int
    ) -> Type[Chapter]:
        """Get a chapter by position

        Parameters
        ----------
        story_id : int
            The id of the story
        position : int
            The position of the chapter

        Returns
        -------
        Chapter
            The chapter object
        """

        with self._session as session:

            return session.query(Chapter).filter(
                Chapter.story_id == story_id,
                Chapter.user_id == self._owner.id,
                Chapter.position == position
            ).first()

    def get_all_chapters_by_story_id(
        self, story_id: int
    ) -> List[Type[Chapter]]:
        """Get all chapters associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of chapter objects
        """

        with self._session as session:

            return session.query(Chapter).filter(
                Chapter.story_id == story_id,
                Chapter.user_id == self._owner.id
            ).order_by(Chapter.position).all()

    def append_characters_to_story(
        self, story_id: int, character_ids: list
    ) -> Type[Story]:
        """Append characters to a story

        Parameters
        ----------
        story_id : int
            The id of the story
        character_ids : list
            The ids of the characters to append

        Returns
        -------
        Story
            The updated story object
        """

        with self._session as session:

            try:

                story = session.query(Story).filter(
                    Story.id == story_id,
                    Story.user_id == self._owner.id
                ).first()

                if not story:
                    raise ValueError('Story not found.')

                for character_id in character_ids:
                    character = session.query(Character).filter(
                        Character.id == character_id,
                        Character.user_id == self._owner.id
                    ).first()

                    if not character:
                        raise ValueError('Character not found.')

                    character_story = CharacterStory(
                        user_id=self._owner.id, character_id=character_id,
                        story_id=story_id, created=datetime.now()
                    )

                    story.characters.append(character_story)

                activity = Activity(
                    user_id=self._owner.id, summary=f'Characters appended to \
                    story {story.title[:50]} by {self._owner.username}',
                    created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def has_characters(self, story_id: int) -> bool:
        """Check if a story has characters

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        bool
            True if the story has characters
        """

        with self._session as session:

            return session.query(Character).join(CharacterStory).filter(
                CharacterStory.story_id == story_id, Character
            ).count() > 0

    def get_characters_by_story_id(
        self, story_id: int
    ) -> List[Type[Character]]:
        """Get all characters associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of character objects
        """

        with self._session as session:

            return session.query(Character).join(CharacterStory).filter(
                CharacterStory.story_id == story_id, Character
            ).all()

    def get_characters_page_by_story_id(
        self, story_id: int, page: int, per_page: int
    ) -> List[Type[Character]]:
        """Get a single page of characters associated with a story from the database

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
            A list of character objects
        """

        with self._session as session:

            offset = (page - 1) * per_page

            return session.query(Character).join(CharacterStory).filter(
                CharacterStory.story_id == story_id, Character
            ).offset(offset).limit(per_page).all()

    def append_links_to_story(
        self, story_id: int, link_ids: list
    ) -> Type[Story]:
        """Append links to a story

        Parameters
        ----------
        story_id : int
            The id of the story
        link_ids : list
            The ids of the links to append

        Returns
        -------
        Story
            The updated story object
        """

        with self._session as session:
            try:
                story = session.query(Story).filter(
                    Story.id == story_id,
                    Story.user_id == self._owner.id
                ).first()

                if not story:
                    raise ValueError('Story not found.')

                for link_id in link_ids:
                    link = session.query(Link).filter(
                        Link.id == link_id,
                        Link.user_id == self._owner.id
                    ).first()

                    if not link:
                        raise ValueError('Link not found.')

                    link_story = LinkStory(
                        user_id=self._owner.id, story_id=story_id,
                        link_id=link_id, created=datetime.now()
                    )

                    story.links.append(link_story)

                activity = Activity(
                    user_id=self._owner.id, summary=f'Links appended to story \
                    {story.title[:50]} by {self._owner.username}',
                    created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def has_links(self, story_id: int) -> bool:
        """Check if a story has links

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        bool
            True if the story has links
        """

        with self._session as session:
            return session.query(Link).join(LinkStory).filter(
                LinkStory.story_id == story_id, LinkStory
            ).count() > 0

    def get_links_by_story_id(self, story_id: int) -> List[Type[Link]]:
        """Get all links associated with a story

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

    def append_notes_to_story(
        self, story_id: int, note_ids: list
    ) -> Type[Story]:
        """Append notes to a story

        Parameters
        ----------
        story_id : int
            The id of the story
        note_ids : list
            The ids of the notes to append

        Returns
        -------
        Story
            The updated story object
        """

        with self._session as session:
            try:
                story = session.query(Story).filter(
                    Story.id == story_id,
                    Story.user_id == self._owner.id
                ).first()

                if not story:
                    raise ValueError('Story not found.')

                for note_id in note_ids:
                    note = session.query(Note).filter(
                        Note.id == note_id,
                        Note.user_id == self._owner.id
                    ).first()

                    if not note:
                        raise ValueError('Note not found.')

                    note_story = NoteStory(
                        user_id=self._owner.id, story_id=story_id,
                        note_id=note_id, created=datetime.now()
                    )

                    story.notes.append(note_story)

                activity = Activity(
                    user_id=self._owner.id, summary=f'Notes appended to story \
                    {story.title[:50]} by {self._owner.username}',
                    created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return story

    def has_notes(self, story_id: int) -> bool:
        """Check if a story has notes

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        bool
            True if the story has notes
        """

        with self._session as session:

            return session.query(Note).join(NoteStory).filter(
                NoteStory.story_id == story_id, NoteStory
            ).count() > 0

    def get_notes_by_story_id(self, story_id: int) -> List[Type[Note]]:
        """Get all notes associated with a story

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            return session.query(Note).join(NoteStory).filter(
                NoteStory.story_id == story_id,
                NoteStory.user_id == self._owner.id
            ).all()
