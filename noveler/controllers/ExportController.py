import os
import re
from configparser import ConfigParser
from datetime import datetime
from typing import Type
from sqlalchemy.orm import Session
from noveler.controllers import BaseController
from noveler.models import User, Story, Chapter, Scene, Activity, Author, AuthorStory


class ExportController(BaseController):
    """Export controller encapsulates export functionality"""

    _export_root: str

    def __init__(self, session: Session, owner: Type[User]):
        """Initialize the class"""

        super().__init__(session, owner)

        try:

            config = ConfigParser()
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config.read(f"{project_root}/config.cfg")
            export_root = config.get("export", "root")
            self._export_root = export_root
            user_folder = f"{export_root}/{self._owner.uuid}"
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)

        except Exception as e:
            raise e

    def export_json(self, story_id: int) -> bool:
        """Export a story to a JSON file

        This method exports a story to a JSON file and stores that file in a
        folder named with the story id. So, for example, if the story id is 1,
        the file would be stored in the folder export/<user UUID>/1/story.json.

        Story size can potentially be huge, so this method uses strategies for
        limiting memory usage. It reads the story in chunks and writes it to
        the file in chunks. The method will return False if the story id is not
        found. If a file already exists, it will be overwritten.

        Parameters
        ----------
        story_id : int
            The id of the story to export

        Returns
        -------
        bool
            True if successful, False otherwise
        """

        with self._session as session:

            story = session.query(Story).filter(
                Story.id == story_id,
                Story.user_id == self._owner.id
            ).first()

            if not story:
                return False

        user_folder = f"{self._export_root}/{self._owner.uuid}"
        story_folder = f"{user_folder}/{story_id}"

        if not os.path.exists(story_folder):
            os.makedirs(story_folder)

        story_file = f"{story_folder}/story.json"

        with open(story_file, "w") as output:

            output.write('{')
            output.write(f'"id":{story.id},')
            output.write(f'"user_id":{story.user_id},')
            output.write(f'"title":"{story.title}",')
            output.write(f'"description":"')

            # chop up the description into 120 character chunks
            # escape any HTML in the description
            description = story.description.replace('"', '\\"')
            description = description.replace('/', "\\/")
            length = len(description)

            while length > 0:
                output.write(description[:120])
                length = length - 120

            output.write('"', )
            output.write(f'"created":"{str(story.created)}",')
            output.write(f'"modified":"{str(story.modified)}",')

            authors = []

            with self._session as session:
                try:

                    authors = session.query(Author).join(
                        AuthorStory,
                        Author.id == AuthorStory.author_id
                    ).filter(
                        AuthorStory.story_id == story_id,
                        AuthorStory.user_id == self._owner.id
                    ).all()

                except Exception as e:
                    raise e

            if authors:

                output.write('"authors":[')

                for author in authors:
                    output.write('{')
                    output.write(f'"id":{author.id},')
                    output.write(f'"user_id":{author.user_id},')
                    output.write(f'"is_pseudonym":{author.is_pseudonym},')
                    output.write(f'"name":"{author.name}",')
                    output.write(f'"initials":"{author.initials}",')
                    output.write(f'"created":"{str(author.created)}",')
                    output.write(f'"modified":"{str(author.modified)}"')
                    output.write('},')

                output.write('],')

            chapters = []

            with self._session as session:
                try:

                    chapters = session.query(Chapter).filter(
                        Chapter.story_id == story_id,
                        Chapter.user_id == self._owner.id
                    ).order_by(Chapter.position).all()

                except Exception as e:
                    raise e

            if chapters:

                output.write('"chapters":[')

                for chapter in chapters:

                    output.write('{')
                    output.write(f'"id":{chapter.id},')
                    output.write(f'"user_id":{chapter.user_id},')
                    output.write(f'"story_id":{chapter.story_id},')
                    output.write(f'"position":{chapter.position},')
                    output.write(f'"title":"{chapter.title}",')
                    output.write(f'"description":"')

                    # chop up the description into 120 character chunks
                    # escape any HTML tags and raw quotes in the description
                    description = chapter.description.replace('"', '\\"')
                    description = description.replace('/', "\\/")
                    length = len(description)

                    while length > 0:
                        output.write(description[:120])
                        length = length - 120

                    output.write('"', )
                    output.write(f'"created":"{str(chapter.created)}",')
                    output.write(f'"modified":"{str(chapter.modified)}",')

                    scenes = []

                    with self._session as session:
                        try:

                            scenes = session.query(Scene).filter(
                                Scene.chapter_id == chapter.id,
                                Scene.user_id == self._owner.id
                            ).order_by(Scene.position).all()

                        except Exception as e:
                            raise e

                    if scenes:

                        output.write('"scenes":[')

                        for scene in scenes:

                            output.write('{')
                            output.write(f'"id":{scene.id},')
                            output.write(f'"user_id":{scene.user_id},')
                            output.write(f'"story_id":{scene.story_id},')
                            output.write(f'"chapter_id":{scene.chapter_id},')
                            output.write(f'"position":{scene.position},')
                            output.write(f'"title":"{scene.title}",')
                            output.write(f'"description":"')

                            # chop up the description into 120 character chunks
                            # escape any HTML tags and raw quotes in the description
                            description = scene.description.replace('"', '\\"')
                            description = description.replace('/', "\\/")
                            length = len(description)

                            while length > 0:
                                output.write(description[:120])
                                length = length - 120

                            output.write('"', )
                            output.write(f'"content":"')

                            # chop up the content into 120 character chunks
                            # escape any HTML tags and raw quotes in the content
                            content = scene.content.replace('"', '\\"')
                            content = content.replace('/', "\\/")
                            length = len(content)

                            while length > 0:
                                output.write(content[:120])
                                length = length - 120

                            output.write('"', )
                            output.write(f'"created":"{str(scene.created)}",')
                            output.write(f'"modified":"{str(scene.modified)}"')
                            output.write('},')

                        output.write(']')
                    output.write('},')
                output.write(']')
            output.write('}')

        with self._session as session:

            try:

                activity = Activity(
                    user_id=self._owner.id, summary=f'Story exported to JSON by \
                    {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()

        return True

    def export_text(self, story_id: int) -> bool:
        """Export a story to a text file

        This method exports a story to a text file and stores that file in a
        folder named with the story id. So, for example, if the story id is 1,
        the file would be stored in the folder export/<user UUID>/1/story.txt.

        Story size can potentially be huge, so this method uses strategies for
        limiting memory usage. It reads the story in chunks and writes it to
        the file in chunks. The method will return False if the story id is not
        found. If a file already exists, it will be overwritten.

        Parameters
        ----------
        story_id : int
            The id of the story to export

        Returns
        -------
        bool
            True if successful, False otherwise
        """

        with self._session as session:

            story = session.query(Story).filter(
                Story.id == story_id,
                Story.user_id == self._owner.id
            ).first()

            if not story:
                return False

        user_folder = f"{self._export_root}/{self._owner.uuid}"
        story_folder = f"{user_folder}/{story_id}"

        if not os.path.exists(story_folder):
            os.makedirs(story_folder)

        story_file = f"{story_folder}/story.txt"

        with open(story_file, "w") as output:

            output.write(" ")
            output.write(story.title)

            authors = []

            with self._session as session:
                try:

                    authors = session.query(Author).join(
                        AuthorStory,
                        Author.id == AuthorStory.author_id
                    ).filter(
                        AuthorStory.story_id == story_id,
                        AuthorStory.user_id == self._owner.id
                    ).all()

                except Exception as e:
                    raise e

            if authors:

                author_count = 0
                num_authors = len(authors)
                author_line = ''
                first_item = True

                for author in authors:

                    author_count += 1

                    if first_item:
                        author_line += f"by {author.name}"
                        first_item = False

                    elif author_count <= (num_authors - 2):
                        author_line += f", {author.name}"

                    elif author_count == (num_authors - 1):
                        author_line += f" and {author.name}"

                output.write(author_line)

            output.write(" ")

            chapters = []

            with self._session as session:
                try:

                    chapters = session.query(Chapter).filter(
                        Chapter.story_id == story_id,
                        Chapter.user_id == self._owner.id
                    ).order_by(Chapter.position).all()

                except Exception as e:
                    raise e

            if chapters:

                for chapter in chapters:

                    output.write(" ")
                    output.write(chapter.title)

                    scenes = []

                    with self._session as session:
                        try:

                            scenes = session.query(Scene).filter(
                                Scene.chapter_id == chapter.id,
                                Scene.user_id == self._owner.id
                            ).order_by(Scene.position).all()

                        except Exception as e:
                            raise e

                    if scenes:

                        for scene in scenes:

                            output.write(" ")
                            # strip any HTML out of the content
                            content = re.compile(r'<[^>]+>').sub(
                                '', scene.content
                            )
                            length = len(content)

                            while length > 0:
                                output.write(content[:80])
                                length = length - 80

                    output.write(" ")

        with self._session as session:

            try:

                activity = Activity(
                    user_id=self._owner.id, summary=f'Story exported to TEXT by \
                    {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()

        return True
