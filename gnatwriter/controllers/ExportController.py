import json
import os
from configparser import ConfigParser
from datetime import datetime
from typing import Type
from sqlalchemy.orm import Session
from gnatwriter.controllers import BaseController
from gnatwriter.models import User, Story, Activity, Character, Event


class ExportController(BaseController):
    """Export controller encapsulates export functionality"""

    _export_root: str

    def __init__(
            self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

        try:

            export_root = self._config.get("export", "root")
            self._export_root = export_root

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

        user_folder = f"{self._export_root}/{self._owner.uuid}"

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        with self._session as session:

            story = session.query(Story).filter(
                Story.id == story_id,
                Story.user_id == self._owner.id
            ).first()

            if not story:
                return False

            json_story = json.dumps(story.serialize(), indent=4)
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

        user_folder = f"{self._export_root}/{self._owner.uuid}"

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        with self._session as session:

            story = session.query(Story).filter(
                Story.id == story_id,
                Story.user_id == self._owner.id
            ).first()

            if not story:
                return False

            story_folder = f"{user_folder}/stories/{story_id}"

            if not os.path.exists(story_folder):
                os.makedirs(story_folder)

            story_file = f"{story_folder}/story.txt"
            dict_story = story.serialize()

            with open(story_file, "w") as output:

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

                    if chapter['description']:
                        output.write(f"\n\n{chapter['description']}\n\n")

                    for scene in chapter["scenes"]:

                        if chapter['title']:
                            output.write(f"{scene['title']}\n")

                        if scene['content']:
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

    def export_character_to_json(self, character_id: int) -> bool:
        """Export a character to a JSON file

        Parameters
        ----------
        character_id : int
            The id of the character to export

        Returns
        -------
        bool
            True if successful, False otherwise
        """

        user_folder = f"{self._export_root}/{self._owner.uuid}"

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        with self._session as session:

            character = session.query(Character).filter(
                Character.id == character_id,
                Character.user_id == self._owner.id
            ).first()

            if not character:
                return False

            json_character = json.dumps(character.serialize(), indent=4)
            character_folder = f"{user_folder}/characters/{character_id}"

            if not os.path.exists(character_folder):
                os.makedirs(character_folder)

            character_file = f"{character_folder}/character.json"

            with open(character_file, "w") as output:

                output.write(json_character)

        with self._session as session:

            try:

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character exported to \
                    JSON by {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()

        return True

    def export_character_to_text(self, character_id: int) -> bool:
        """Export a character to a text file

        Parameters
        ----------
        character_id : int
            The id of the character to export

        Returns
        -------
        bool
            True if successful, False otherwise
        """

        user_folder = f"{self._export_root}/{self._owner.uuid}"

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        with self._session as session:

            character = session.query(Character).filter(
                Character.id == character_id,
                Character.user_id == self._owner.id
            ).first()

            if not character:
                return False

            character_folder = f"{user_folder}/characters/{character_id}"

            if not os.path.exists(character_folder):
                os.makedirs(character_folder)

            character_file = f"{character_folder}/character.txt"
            dict_character = character.serialize()

            with open(character_file, "w") as output:

                output.write(
                    f"Character Profile for {dict_character['full_name']}"
                )

                if dict_character['description']:
                    output.write(f"\n\n{dict_character['description']}")

                if dict_character['wounds']:
                    output.write(f"\n\nThe character's wounds:\n{dict_character['wounds']}")

                if dict_character["gender"]:
                    output.write(f"\n\nGender: {dict_character['gender']}")

                if dict_character["sex"]:
                    output.write(f"\nSex: {dict_character['sex']}")

                if dict_character["ethnicity"]:
                    output.write(f"\nEthnicity: {dict_character['ethnicity']}")

                if dict_character["race"]:
                    output.write(f"\nRace: {dict_character['race']}")

                if dict_character["tribe_or_clan"]:
                    output.write(f"\nTribe or Clan: {dict_character['tribe_or_clan']}")

                if dict_character["nationality"]:
                    output.write(f"\nNationality: {dict_character['nationality']}")

                if dict_character["religion"]:
                    output.write(f"\nReligion: {dict_character['religion']}")

                if dict_character["mbti"]:
                    output.write(f"\nMyers-Briggs Type Indicator: {dict_character['mbti']}")

                if dict_character["enneagram"]:
                    output.write(f"\nEnneagram Type: {dict_character['enneagram']}")

                if dict_character["occupation"]:
                    output.write(f"\nOccupation: {dict_character['occupation']}")

                if dict_character["education"]:
                    output.write(f"\nEducation: {dict_character['education']}")

                if dict_character["marital_status"]:
                    output.write(f"\nMarital Status: {dict_character['marital_status']}")

                if dict_character["children"]:
                    output.write(f"\nThis character has or had children.")
                else:
                    output.write(f"\nThis character has no children.")

                if dict_character["age"]:
                    output.write(f"\nAge: {dict_character['age']}")

                if dict_character["date_of_birth"]:
                    output.write(f"\nDate of Birth: {dict_character['date_of_birth']}")

                if dict_character["date_of_death"]:
                    output.write(f"\nDate of Death: {dict_character['date_of_death']}")

                if len(dict_character["traits"]) > 0:
                    output.write("\n\nTraits and Magnitudes on 0-100 Scale (0 = undetectable, 100 = maximum level):")
                    for trait in dict_character["traits"]:
                        output.write(f"\n{trait['name']} - {trait['magnitude']}")

                if dict_character["relationships"]:
                    output.write("\n\nRelationships to other Characters:")
                    for relationship in dict_character["relationships"]:
                        output.write(
                            f"""\n\nRelationship to {relationship['related_name']} in the category of \
{relationship['relationship_type']}:
Start Date: {relationship['start_date']}
End Date: {relationship['end_date']}
                            """
                        )
                        output.write(
                            f"\nDescription:  {relationship['description']}"
                        )

                if dict_character["events"]:
                    output.write(
                        "\n\nEvents with which this character is associated:"
                    )
                    for character_event in dict_character["events"]:
                        output.write(
                            f"\n{character_event['event']}"
                        )

                if dict_character["stories"]:
                    output.write(
                        "\n\nStories in which this character appears:"
                    )
                    for character_story in dict_character["stories"]:
                        output.write(
                            f"\n{character_story['story_name']}"
                        )

        with self._session as session:

            try:

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character exported to \
                    TEXT by {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()

        return True

    def export_event_to_json(self, event_id: int) -> bool:
        """Export an event to a JSON file

        Parameters
        ----------
        event_id : int
            The id of the event to export

        Returns
        -------
        bool
            True if successful, False otherwise
        """

        user_folder = f"{self._export_root}/{self._owner.uuid}"

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        with self._session as session:

            event = session.query(Event).filter(
                Event.id == event_id,
                Event.user_id == self._owner.id
            ).first()

            if not event:
                return False

            json_event = json.dumps(event.serialize(), indent=4)
            event_folder = f"{user_folder}/events/{event_id}"

            if not os.path.exists(event_folder):
                os.makedirs(event_folder)

            event_file = f"{event_folder}/event.json"

            with open(event_file, "w") as output:

                output.write(json_event)

        with self._session as session:

            try:

                activity = Activity(
                    user_id=self._owner.id, summary=f'Event exported to JSON by \
                    {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()

        return True

    def export_event_to_text(self, event_id: int) -> bool:
        """Export an event to a text file

        Parameters
        ----------
        event_id : int
            The id of the event to export

        Returns
        -------
        bool
            True if successful, False otherwise
        """

        user_folder = f"{self._export_root}/{self._owner.uuid}"

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        with self._session as session:

            event = session.query(Event).filter(
                Event.id == event_id,
                Event.user_id == self._owner.id
            ).first()

            if not event:
                return False

            event_folder = f"{user_folder}/events/{event_id}"

            if not os.path.exists(event_folder):
                os.makedirs(event_folder)

            event_file = f"{event_folder}/event.txt"
            dict_event = event.serialize()

            with open(event_file, "w") as output:

                output.write(f"Event report for {dict_event['title']}")

                if dict_event["start_datetime"]:
                    output.write(
                        f"\n\nStart Datetime: {dict_event['start_datetime']}"
                    )

                if dict_event["end_datetime"]:
                    output.write(
                        f"\nEnd Datetime: {dict_event['end_datetime']}"
                    )

                if dict_event["description"]:
                    output.write(f"\n\n{dict_event['description']}")

        with self._session as session:

            try:

                activity = Activity(
                    user_id=self._owner.id, summary=f'Event exported to TEXT by \
                    {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()

        return True
