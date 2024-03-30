import json
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

    def export_story_to_json(self, story_id: int) -> bool:
        """Export a story to a JSON file

        This method exports a story to a JSON file and stores that file in a
        folder named with the story id. So, for example, if the story id is 1,
        the file would be stored in the folder export/<user UUID>/1/story.json.

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

            json_story = json.dumps(story.serialize(), indent=4)

            user_folder = f"{self._export_root}/{self._owner.uuid}"
            story_folder = f"{user_folder}/stories/{story_id}"

            if not os.path.exists(story_folder):
                os.makedirs(story_folder)

            story_file = f"{story_folder}/story.json"

            with open(story_file, "w") as output:

                output.write(json_story)

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

    def export_story_to_text(self, story_id: int) -> bool:
        """Export a story to a text file

        This method exports a story to a text file and stores that file in a
        folder named with the story id. So, for example, if the story id is 1,
        the file would be stored in the folder export/<user UUID>/1/story.txt.

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
            story_folder = f"{user_folder}/stories/{story_id}"

            if not os.path.exists(story_folder):
                os.makedirs(story_folder)

            story_file = f"{story_folder}/story.txt"
            dict_story = story.serialize()

            with open(story_file, "w") as output:

                output.write(" ")
                output.write(f"{dict_story['title']}\n")
                output.write(f"{dict_story['description']}\n")

                author_count = len(dict_story["authors"])

                counter = 0
                is_first = True
                author_string = ""

                for author in dict_story["authors"]:

                    counter += 1

                    if is_first:
                        author_string += f"By {author['name']}"
                        is_first = False

                    elif counter == (author_count - 2):
                        author_string += f", {author.name}"

                    elif counter == (author_count - 1):
                        author_string += f" and {author.name}"

                output.write(f"{author_string}\n")

                for chapter in dict_story["chapters"]:

                    output.write(f"\n\n{chapter['title']}\n\n")
                    output.write(f"\n\n{chapter['description']}\n\n")

                    for scene in chapter["scenes"]:
                        output.write(f"{scene['title']}\n")
                        output.write(f"{scene['content']}\n")

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
