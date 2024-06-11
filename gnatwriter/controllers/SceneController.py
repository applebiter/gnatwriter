import os
from configparser import ConfigParser
from datetime import datetime
from typing import Type, List
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from gnatwriter.controllers.BaseController import BaseController
from gnatwriter.models import User, Scene, Link, LinkScene, Note, NoteScene, Activity


class SceneController(BaseController):
    """Scene controller encapsulates scene management functionality

    Attributes
    ----------
    _instance : SceneController
        The instance of the scene controller
    _config: ConfigParser
        The configuration parser
    _owner : User
        The current user of the scene controller
    _session : Session
        The database session

    Methods
    -------
    create_scene(story_id: int, chapter_id: int, title: str, description: str, content: str)
        Create a new scene
    update_scene(scene_id: int, title: str, description: str, content: str)
        Update a scene
    change_scene_position(scene_id: int, position: int)
        Change the position of a scene within a chapter
    delete_scene(scene_id: int)
        Delete a scene
    count_scenes_by_chapter_id(chapter_id: int)
        Count the number of scenes associated with a chapter
    get_scene_by_id(scene_id: int)
        Get a scene by id
    get_all_scenes()
        Get all scenes associated with an owner
    get_all_scenes_page(page: int, per_page: int)
        Get a single page of scenes associated with an owner from the database
    get_scenes_by_story_id(story_id: int)
        Get all scenes associated with a story
    get_scenes_page_by_story_id(story_id: int, page: int, per_page: int)
        Get a single page of scenes associated with a story from the database
    get_scenes_by_chapter_id(chapter_id: int)
        Get all scenes associated with a chapter
    get_scenes_page_by_chapter_id(chapter_id: int, page: int, per_page: int)
        Get a single page of scenes associated with a chapter from the database
    search_scenes(search: str)
        Search for scenes by title, description, and content
    append_links_to_scene(scene_id: int, link_ids: list)
        Append links to a scene
    get_links_by_scene_id(scene_id: int)
        Get all links associated with a scene
    append_notes_to_scene(scene_id: int, note_ids: list)
        Append notes to a scene
    get_notes_by_scene_id(scene_id: int)
        Get all notes associated with a scene
    """

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_scene(
        self, story_id: int, chapter_id: int, title: str,
        description: str = None, content: str = None
    ) -> Scene:
        """Create a new scene

        Parameters
        ----------
        story_id : int
            The id of the story
        chapter_id : int
            The id of the chapter
        title : str
            The title of the scene
        description : str
            The description of the scene
        content : str
            The content of the scene

        Returns
        -------
        Scene
            The new scene object
        """

        with self._session as session:
            try:
                title_exists = session.query(Scene).filter(
                    Scene.title == title,
                    Scene.chapter_id == chapter_id,
                    Scene.user_id == self._owner.id
                ).first()

                if title_exists:
                    raise Exception('This chapter already has a scene with the same title.')

                position = session.query(
                    func.max(Scene.position)
                ).filter(Scene.chapter_id == chapter_id).scalar()
                position = int(position) + 1 if position else 1
                created = datetime.now()
                modified = created

                scene = Scene(
                    user_id=self._owner.id, story_id=story_id,
                    chapter_id=chapter_id, position=position, title=title,
                    description=description, content=content, created=created,
                    modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Scene {scene.title[:50]} \
                    created by {self._owner.username}', created=datetime.now()
                )

                session.add(scene)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return scene

    def update_scene(
        self, scene_id: int, title: str, description: str = None,
        content: str = None
    ) -> Type[Scene]:
        """Update a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene
        title : str
            The title of the scene
        description : str
            The description of the scene
        content : str
            The content of the scene

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                scene = session.query(Scene).filter(
                    Scene.id == scene_id,
                    Scene.user_id == self._owner.id
                ).first()

                if not scene:
                    raise ValueError('Scene not found.')

                scene.title = title
                scene.description = description
                scene.content = content
                scene.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Scene {scene.id} updated \
                    by {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return scene

    def change_scene_position(self, scene_id: int, position: int) -> int:
        """Change the position of a scene within a chapter

        First, determine whether the new position is closer to 1 or further from 1. If closer to one, get all sibling
        scenes with positions greater than or equal to the new position but less than the current position, and
        increment those position values by 1. If the target position is further away from 1 than the current position,
        get all sibling scenes with positions greater than the current position but less than or equal to the new
        position, and decrement those position values by 1. Finally, set the position of the target scene to the new
        position. Return the new position.

        Parameters
        ----------
        scene_id : int
            The id of the scene
        position : int
            The position of the scene

        Returns
        -------
        int
            The new position value
        """

        config = ConfigParser()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config.read(f"{project_root}/config.cfg")

        with self._session as session:
            try:
                scene = session.query(Scene).filter(
                    Scene.id == scene_id,
                    Scene.user_id == self._owner.id
                ).first()

                if not scene:
                    raise ValueError('Scene not found.')

                if scene.position == position:
                    return position

                if scene.position > position:
                    scenes = session.query(Scene).filter(
                        Scene.chapter_id == scene.chapter_id,
                        Scene.position >= position,
                        Scene.position < scene.position,
                        Scene.user_id == self._owner.id
                    ).all()
                    for sibling in scenes:
                        sibling.position += 1
                        sibling.created = datetime.strptime(
                            str(sibling.created),
                            config.get("formats", "datetime")
                        )
                        sibling.modified = datetime.now()
                else:
                    scenes = session.query(Scene).filter(
                        Scene.chapter_id == scene.chapter_id,
                        Scene.position > scene.position,
                        Scene.position <= position,
                        Scene.user_id == self._owner.id
                    ).all()
                    for sibling in scenes:
                        sibling.position -= 1
                        sibling.created = datetime.strptime(
                            str(sibling.created),
                            config.get("formats", "datetime")
                        )
                        sibling.modified = datetime.now()

                scene.position = position
                scene.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Scene {scene.title[:50]} \
                    position changed by {self._owner.username}',
                    created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return position

    def delete_scene(self, scene_id: int) -> bool:
        """Delete a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                scene = session.query(Scene).filter(
                    Scene.id == scene_id,
                    Scene.user_id == self._owner.id
                ).first()

                if not scene:
                    raise ValueError('Scene not found.')

                siblings = session.query(Scene).filter(
                    Scene.chapter_id == scene.chapter_id,
                    Scene.user_id == self._owner.id,
                    Scene.position > scene.position
                ).all()

                for sibling in siblings:
                    sibling.position -= 1
                    sibling.created = datetime.strptime(
                        str(sibling.created),
                        self._config.get("formats", "datetime")
                    )
                    sibling.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Scene {scene.id} deleted \
                    by {self._owner.username}', created=datetime.now()
                )

                session.delete(scene)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def count_scenes_by_chapter_id(self, chapter_id: int) -> int:
        """Count the number of scenes associated with a chapter

        Parameters
        ----------
        chapter_id : int
            The id of the chapter

        Returns
        -------
        int
            The number of scenes
        """

        with self._session as session:

            return session.query(Scene).filter(
                Scene.chapter_id == chapter_id,
                Scene.user_id == self._owner.id
            ).count()

    def get_scene_by_id(self, scene_id: int) -> Type[Scene] | None:
        """Get a scene by id

        Parameters
        ----------
        scene_id : int
            The id of the scene

        Returns
        -------
        Scene
            The scene object
        """

        with self._session as session:

            return session.query(Scene).filter(
                Scene.id == scene_id,
                Scene.user_id == self._owner.id
            ).first()

    def get_all_scenes(self) -> List[Type[Scene]]:
        """Get all scenes associated with an owner

        Scenes are sorted by story id, chapter id, and position in ascending order.

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            return session.query(Scene).filter(
                Scene.user_id == self._owner.id
            ).order_by(
                Scene.story_id, Scene.chapter_id, Scene.position
            ).all()

    def get_all_scenes_page(
        self, page: int, per_page: int
    ) -> List[Type[Scene]]:
        """Get a single page of scenes associated with an owner from the database

        Scenes are sorted by story id, chapter id, and position in ascending order

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Scene).filter(
                Scene.user_id == self._owner.id
            ).order_by(
                Scene.story_id, Scene.chapter_id, Scene.position
            ).offset(offset).limit(per_page).all()

    def get_scenes_by_story_id(self, story_id: int) -> List[Type[Scene]]:
        """Get all scenes associated with a story

        Scenes are sorted by chapter id and position in ascending order

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            return session.query(Scene).filter(
                Scene.story_id == story_id,
                Scene.user_id == self._owner.id
            ).order_by(
                Scene.chapter_id, Scene.position
            ).all()

    def get_scenes_page_by_story_id(
        self, story_id: int, page: int, per_page: int
    ) -> List[Type[Scene]]:
        """Get a single page of scenes associated with a story from the database

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
            A list of scene objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Scene).filter(
                Scene.story_id == story_id,
                Scene.user_id == self._owner.id
            ).order_by(
                Scene.chapter_id, Scene.position
            ).offset(offset).limit(per_page).all()

    def get_scenes_by_chapter_id(self, chapter_id: int) -> List[Type[Scene]]:
        """Get all scenes associated with a chapter

        Scenes are sorted by position in ascending order

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

    def get_scenes_page_by_chapter_id(
        self, chapter_id: int, page: int, per_page: int
    ) -> List[Type[Scene]]:
        """Get a single page of scenes associated with a chapter from the database

        Scenes are sorted by position in ascending order

        Parameters
        ----------
        chapter_id : int
            The id of the chapter
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Scene).filter(
                Scene.chapter_id == chapter_id,
                Scene.user_id == self._owner.id
            ).order_by(Scene.position).offset(offset).limit(per_page).all()

    def search_scenes(self, search: str) -> List[Type[Scene]]:
        """Search for scenes by title, description, and content

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of scene objects
        """

        with self._session as session:
            return session.query(Scene).filter(
                or_(
                    Scene.title.like(f'%{search}%'),
                    Scene.description.like(f'%{search}%'),
                    Scene.content.like(f'%{search}%')
                ),
                Scene.user_id == self._owner.id
            ).all()

    def append_links_to_scene(
        self, scene_id: int, link_ids: list
    ) -> Type[Scene]:
        """Append links to a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene
        link_ids : list
            A list of link ids

        Returns
        -------
        Scene
            The updated scene object
        """

        with self._session as session:
            try:
                scene = session.query(Scene).filter(
                    Scene.id == scene_id,
                    Scene.user_id == self._owner.id
                ).first()

                if not scene:
                    raise ValueError('Scene not found.')

                for link_id in link_ids:
                    link = session.query(Link).filter(
                        Link.id == link_id,
                        Link.user_id == self._owner.id
                    ).first()

                    if not link:
                        raise ValueError('Link not found.')

                    link_scene = LinkScene(
                        user_id=self._owner.id, link_id=link_id,
                        scene_id=scene_id, created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Links appended to \
                        scene {scene.id} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.add(link_scene)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return scene

    def get_links_by_scene_id(self, scene_id: int) -> List[Type[Link]]:
        """Get all links associated with a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            return session.query(Link).join(LinkScene).filter(
                LinkScene.scene_id == scene_id,
                LinkScene.user_id == self._owner.id
            ).all()

    def append_notes_to_scene(
        self, scene_id: int, note_ids: list
    ) -> Type[Scene]:
        """Append notes to a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene
        note_ids : list
            A list of note ids

        Returns
        -------
        Scene
            The updated scene object
        """

        with self._session as session:
            try:
                scene = session.query(Scene).filter(
                    Scene.id == scene_id,
                    Scene.user_id == self._owner.id
                ).first()

                if not scene:
                    raise ValueError('Scene not found.')

                for note_id in note_ids:
                    note = session.query(Note).filter(
                        Note.id == note_id,
                        Note.user_id == self._owner.id
                    ).first()

                    if not note:
                        raise ValueError('Note not found.')

                    note_scene = NoteScene(
                        user_id=self._owner.id, note_id=note_id,
                        scene_id=scene_id, created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Notes appended to \
                        scene {scene.id} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.add(note_scene)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return scene

    def get_notes_by_scene_id(self, scene_id: int) -> List[Type[Note]]:
        """Get all notes associated with a scene

        Parameters
        ----------
        scene_id : int
            The id of the scene

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            return session.query(Note).join(NoteScene).filter(
                NoteScene.scene_id == scene_id,
                NoteScene.user_id == self._owner.id
            ).all()
