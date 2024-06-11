from datetime import datetime
from typing import Type, List
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from gnatwriter.controllers.BaseController import BaseController
from gnatwriter.models import User, Character, CharacterStory, Activity, CharacterRelationship, CharacterTrait, Event, \
    CharacterEvent, Link, CharacterLink, Note, CharacterNote, Image, CharacterImage
from configparser import ConfigParser


class CharacterController(BaseController):
    """Character controller encapsulates characters management functionality

    Attributes
    ----------
    _instance : CharacterController
        The instance of the characters controller
    _config: ConfigParser
        The configuration parser
    _owner : User
        The current user of the characters controller
    _session : Session
        The database session

    Methods
    -------
    create_character(title: str, first_name: str, middle_name: str, last_name: str, honorific: str, nickname: str, \
                     gender: str, sex: str, ethnicity: str, race: str, tribe_or_clan: str, nationality: str, \
                     date_of_birth: str, date_of_death: str, description: str, mbti: str, enneagram: str, wounds: str)
        Create a new character
    update_character(character_id: int, title: str, first_name: str, middle_name: str, last_name: str, honorific: str, \
                     nickname: str, gender: str, sex: str, ethnicity: str, race: str, tribe_or_clan: str, \
                     nationality: str, date_of_birth: str, date_of_death: str, description: str, mbti: str, \
                     enneagram: str, wounds: str)
        Update a character
    delete_character(character_id: int)
        Delete a character
    get_character_by_id(character_id: int)
        Get a character by id
    get_character_count()
        Get character count associated with a user
    get_all_characters()
        Get all characters associated with a user
    get_all_characters_page(page: int, per_page: int)
        Get a single page of characters from the database associated with a user
    get_character_count_by_story_id(story_id: int)
        Get character count associated with a story
    get_characters_by_story_id(story_id: int)
        Get a list of characters by story id
    get_characters_page_by_story_id(story_id: int, page: int, per_page: int)
        Get a single page of characters by story id
    search_characters(search: str)
        Search for characters by title, first name, middle name, last name, nickname, and description belonging to a \
        specific user
    search_characters_by_story_id(story_id: int, search: str)
        Search for characters by title, first name, middle name, last name, nickname, and description belonging to a \
        specific story
    create_relationship(parent_id: int, related_id: int, relationship_type: str, description: str,
                        start_date: str, end_date: str)
        Create a new character relationship
    update_relationship(relationship_id: int, parent_id: int, related_id: int, relationship_type: str,
                        description: str, start_date: str, end_date: str)
        Update a character relationship
    change_relationship_position(relationship_id: int, position: int)
        Set the position of a character relationship
    delete_relationship(relationship_id: int)
        Delete a character relationship
    get_relationship_by_id(relationship_id: int)
        Get a character relationship by id
    get_relationships_by_character_id(parent_id: int)
        Get character relationships by character id, from that character's perspective
    get_relationships_page_by_character_id(parent_id: int, page: int, per_page: int)
        Get a single page of character relationships by character id, from that character's perspective
    create_trait(character_id: int, name: str, magnitude: int)
        Create a new character trait
    update_trait(trait_id: int, name: str, magnitude: int)
        Update a character trait
    change_trait_position(trait_id: int, position: int)
        Set the position of a character trait
    delete_trait(trait_id: int)
        Delete a character trait
    get_trait_by_id(trait_id: int)
        Get a character trait by id
    get_traits_by_character_id(character_id: int)
        Get character traits by character id
    get_traits_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of character traits by character id
    append_events_to_character(character_id: int, events: list)
        Append events to a character
    get_events_by_character_id(character_id: int)
        Get all events associated with a character
    get_events_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of events associated with a character from the database
    append_links_to_character(character_id: int, links: list)
        Append links to a character
    get_links_by_character_id(character_id: int)
        Get all links associated with a character
    get_links_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of links associated with a character from the database
    append_notes_to_character(character_id: int, notes: list)
        Append notes to a character
    get_notes_by_character_id(character_id: int)
        Get all notes associated with a character
    get_notes_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of notes associated with a character from the database
    append_images_to_character(character_id: int, images: list)
        Append images to a character
    change_image_position(image_id: int, position: int)
        Set the position of an image related to a character
    change_image_default_status(image_id: int, is_default: bool)
        Set the default status of an image related to a character
    delete_image(image_id: int)
        Delete an image related to a character
    get_image_count_by_character_id(character_id: int)
        Get image count associated with a character
    get_images_by_character_id(character_id: int)
        Get all images associated with a character
    get_images_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of images associated with a character from the database
    """

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_character(
        self, title: str = None, honorific: str = None, first_name: str = None,
        middle_name: str = None, last_name: str = None, nickname: str = None,
        gender: str = None, sex: str = None, ethnicity: str = None,
        race: str = None, tribe_or_clan: str = None, nationality: str = None,
        religion: str = None, occupation: str = None, education: str = None,
        marital_status: str = None, children: bool = None,
        date_of_birth: str = None, date_of_death: str = None,
        description: str = None, mbti: str = None, enneagram: str = None,
        wounds: str = None
    ) -> Character:
        """Create a new character

        Although all the attributes are technically optional, at least one of the following fields must be provided:
        title, first name, middle name, last name, or nickname.

        Parameters
        ----------
        title : str
            The title of the character, optional
        honorific : str
            The honorific of the character, optional
        first_name : str
            The first name of the character, optional
        middle_name : str
            The middle name of the character, optional
        last_name : str
            The last name of the character, optional
        nickname : str
            The nickname of the character, optional
        gender: str
            The gender of the character, optional
        sex: str
            The sex of the character, optional
        ethnicity: str
            The ethnicity of the character, optional
        race: str
            The race of the character, optional
        tribe_or_clan: str
            The tribe or clan of the character, optional
        nationality: str
            The nationality of the character, optional
        religion: str
            The religion of the character, optional
        occupation: str
            The occupation of the character, optional
        education: str
            The education of the character, optional
        marital_status: str
            The marital status of the character, optional
        children: bool
            Whether the character has children, optional
        date_of_birth: str
            The date of birth of the character, optional
        date_of_death: str
            The date of death of the character, optional
        description
            The description of the character, optional
        mbti: str
            The Myers-Briggs Type Indicator of the character, optional
        enneagram: str
            The Enneagram type of the character, optional
        wounds: str
            The wounds of the character, optional

        Returns
        -------
        Character
            The new character object
        """

        with self._session as session:

            try:

                if not title and not first_name and not last_name and not middle_name and not nickname:
                    raise ValueError("""At least one of the following fields 
                    must be provided: title, first name, middle name, last name, 
                    nickname.""")

                created = datetime.now()
                modified = created
                character = Character(
                    user_id=self._owner.id, title=title, first_name=first_name,
                    middle_name=middle_name, last_name=last_name,
                    honorific=honorific, nickname=nickname, gender=gender,
                    sex=sex, ethnicity=ethnicity, race=race,
                    tribe_or_clan=tribe_or_clan, nationality=nationality,
                    religion=religion, occupation=occupation,
                    education=education, marital_status=marital_status,
                    children=children, date_of_birth=date_of_birth,
                    date_of_death=date_of_death, description=description,
                    mbti=mbti, enneagram=enneagram, wounds=wounds,
                    created=created, modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'{character.__str__} \
                    created by {self._owner.username}', created=datetime.now()
                )

                session.add(character)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def update_character(
        self, character_id: int = None, title: str = None, honorific: str = None,
        first_name: str = None, middle_name: str = None, last_name: str = None,
        nickname: str = None, gender: str = None, sex: str = None,
        ethnicity: str = None, race: str = None, tribe_or_clan: str = None,
        nationality: str = None, religion: str = None, occupation: str = None,
        education: str = None, marital_status: str = None, children: bool = None,
        date_of_birth: str = None, date_of_death: str = None,
        description: str = None, mbti: str = None, enneagram: str = None,
        wounds: str = None
    ) -> Type[Character]:
        """Update a character

        Parameters
        ----------
        character_id : int
            The id of the character to update
        title : str
            The title of the character
        honorific : str
            The honorific of the character
        first_name : str
            The first name of the character
        middle_name : str
            The middle name of the character
        last_name : str
            The last name of the character
        nickname : str
            The nickname of the character
        gender : str
            The gender of the character
        sex : str
            The sex of the character
        ethnicity : str
            The ethnicity of the character
        race : str
            The race of the character
        tribe_or_clan : str
            The tribe or clan of the character
        nationality : str
            The nationality of the character
        religion : str
            The religion of the character
        occupation : str
            The occupation of the character
        education : str
            The education of the character
        marital_status : str
            The marital status of the character
        children : bool
            Whether the character has children
        date_of_birth : str
            The date of birth of the character
        date_of_death : str
            The date of death of the character
        description : str
            The description of the character
        mbti : str
            The Myers-Briggs Type Indicator of the character
        enneagram : str
            The Enneagram type of the character
        wounds : str
            The wounds of the character

        Returns
        -------
        Character
            The updated character object
        """

        with self._session as session:

            try:

                character = session.query(Character).filter(
                    Character.id == character_id,
                    Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                character.title = title
                character.honorific = honorific
                character.first_name = first_name
                character.middle_name = middle_name
                character.last_name = last_name
                character.nickname = nickname
                character.gender = gender
                character.sex = sex
                character.ethnicity = ethnicity
                character.race = race
                character.tribe_or_clan = tribe_or_clan
                character.nationality = nationality
                character.religion = religion
                character.occupation = occupation
                character.education = education
                character.marital_status = marital_status
                character.children = children
                character.date_of_birth = date_of_birth
                character.date_of_death = date_of_death
                character.description = description
                character.mbti = mbti
                character.enneagram = enneagram
                character.wounds = wounds
                character.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'{character.__str__} \
                    updated by {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def delete_character(self, character_id: int) -> bool:
        """Delete a character

        Character objects are even more complex than Chapter objects. Each Character can have an arbitrary number of
        Link, Note, and Image objects associated with it. Additionally, each Character has an arbitrary number of
        character relationships, an arbitrary number of character traits, and an arbitrary number of events associated
        with it. Before the Character can be deleted, the links, notes, images, relationships, traits, and events
        associated with it must be deleted. The Characters do not possess a position scheme, so there is no need to
        adjust the position of sibling characters. Finally, the Character is deleted.

        Parameters
        ----------
        character_id : int
            The id of the character to delete

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:

            try:

                character = session.query(Character).filter(
                    Character.id == character_id,
                    Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                activity = Activity(
                    user_id=self._owner.id, summary=f'{character.__str__} \
                    deleted by {self._owner.username}', created=datetime.now()
                )

                session.delete(character)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_character_by_id(self, character_id: int) -> Type[Character] | None:
        """Get a character by id

        Parameters
        ----------
        character_id : int
            The id of the character to get

        Returns
        -------
        Type[Character] | None
            The character if found, otherwise None
        """

        with self._session as session:
            character = session.query(Character).filter(
                Character.id == character_id,
                Character.user_id == self._owner.id
            ).first()
            return character if character else None

    def get_character_count(self) -> int:
        """Get character count associated with a user

        Returns
        -------
        int
            The count of characters associated with the user
        """

        with self._session as session:
            return session.query(func.count(Character.id)).filter(
                Character.user_id == self._owner.id
            ).scalar()

    def get_all_characters(self) -> List[Type[Character]]:
        """Get all characters associated with a user

        Returns
        -------
        list
            The list of characters associated with the user
        """

        with self._session as session:
            return session.query(Character).filter(
                Character.user_id == self._owner.id
            ).all()

    def get_all_characters_page(
        self, page: int, per_page: int
    ) -> List[Type[Character]]:
        """Get a single page of characters from the database associated with a user

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of characters associated with the user
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Character).filter(
                Character.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def get_character_count_by_story_id(self, story_id: int) -> int:
        """Get character count associated with a story

        The characters and stories are associated in the CharacterStory table.

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        int
            The count of characters associated with the story
        """

        with self._session as session:
            return session.query(
                func.count(CharacterStory.character_id)
            ).filter(
                CharacterStory.story_id == story_id,
                CharacterStory.user_id == self._owner.id
            ).scalar()

    def get_characters_by_story_id(
        self, story_id: int
    ) -> List[Type[Character]]:
        """Get characters by story id

        The characters and stories are associated in the CharacterStory table.

        Parameters
        ----------
        story_id : int
            The id of the story

        Returns
        -------
        list
            The list of characters associated with the story
        """

        with self._session as session:
            for character_story in session.query(CharacterStory).filter(
                CharacterStory.story_id == story_id,
                CharacterStory.user_id == self._owner.id
            ).all():
                yield session.query(Character).filter(
                    Character.id == character_story.character_id,
                    Character.user_id == self._owner.id
                ).first()

    def get_characters_page_by_story_id(
        self, story_id: int, page: int, per_page: int
    ) -> List[Type[Character]]:
        """Get a single page of characters by story id

        The characters and stories are associated in the CharacterStory table.

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
            The list of characters associated with the story
        """

        with self._session as session:
            offset = (page - 1) * per_page
            for character_story in session.query(CharacterStory).filter(
                CharacterStory.story_id == story_id,
                    CharacterStory.user_id == self._owner.id
            ).offset(offset).limit(per_page).all():
                yield session.query(Character).filter(
                    Character.id == character_story.character_id,
                    Character.user_id == self._owner.id
                ).first()

    def search_characters(self, search: str) -> List[Type[Character]]:
        """Search for characters by title, first name, middle name, last name, nickname, and description belonging to \
        a specific user

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            The list of characters associated with the user
        """

        with self._session as session:
            return session.query(Character).filter(
                or_(
                    Character.title.like(f'%{search}%'),
                    Character.first_name.like(f'%{search}%'),
                    Character.middle_name.like(f'%{search}%'),
                    Character.last_name.like(f'%{search}%'),
                    Character.nickname.like(f'%{search}%'),
                    Character.description.like(f'%{search}%')
                ),
                Character.user_id == self._owner.id
            ).all()

    def search_characters_by_story_id(
        self, story_id: int, search: str
    ) -> List[Type[Character]]:
        """Search for characters by title, first name, middle name, last name, nickname, and description belonging to \
        a specific story

        Parameters
        ----------
        story_id : int
            The id of the story
        search : str
            The search string

        Returns
        -------
        list
            The list of characters associated with the story
        """

        with self._session as session:
            return session.query(Character).join(
                CharacterStory,
                Character.id == CharacterStory.character_id
            ).filter(
                or_(
                    Character.title.like(f'%{search}%'),
                    Character.first_name.like(f'%{search}%'),
                    Character.middle_name.like(f'%{search}%'),
                    Character.last_name.like(f'%{search}%'),
                    Character.nickname.like(f'%{search}%'),
                    Character.description.like(f'%{search}%')
                ),
                CharacterStory.story_id == story_id,
                CharacterStory.user_id == self._owner.id
            ).all()

    def create_relationship(
        self, parent_id: int, related_id: int, relationship_type: str,
        description: str = None, start_date: str = None, end_date: str = None
    ) -> CharacterRelationship:
        """Create a new character relationship

        There are many relationships for each character, and the linking class, CharacterRelationship, is used to
        define the relationship between two characters. The relationship type is defined in the
        CharacterRelationshipTypes and elaborated upon in the description. Before insertion, in order to determine
        the correct position, the highest position among sibling CharacterRelationship objects is first determined.
        The new position is set to the highest position plus one. The created and modified fields are set to the
        current date and time. Finally, insert the new CharacterRelationship object into the database.

        Parameters
        ----------
        parent_id : int
            The id of the parent character
        related_id : int
            The id of the related character
        relationship_type : str
            The type of relationship
        description : str
            The description of the relationship, optional
        start_date : str
            The start date of the relationship, optional
        end_date : str
            The end date of the relationship, optional

        Returns
        -------
        CharacterRelationship
            The new character relationship object
        """

        with self._session as session:
            try:
                if not parent_id or not related_id:
                    raise ValueError('Both parent and related character ids must be provided.')

                if parent_id == related_id:
                    raise ValueError('Parent and related character ids must be different.')

                parent = session.query(Character).filter(
                    Character.id == parent_id, Character.user_id == self._owner.id
                ).first()

                if not parent:
                    raise ValueError('Parent character not found.')

                related = session.query(Character).filter(
                    Character.id == related_id, Character.user_id == self._owner.id
                ).first()

                if not related:
                    raise ValueError('Related character not found.')

                position = session.query(func.max(CharacterRelationship.position)).filter(
                    CharacterRelationship.parent_id == parent_id,
                    CharacterRelationship.user_id == self._owner.id
                ).scalar()

                position = 1 if not position else position + 1
                created = datetime.now()
                modified = created
                character_relationship = CharacterRelationship(
                    user_id=self._owner.id, parent_id=parent.id,
                    related_id=related.id, position=position,
                    relationship_type=relationship_type,
                    description=description, start_date=start_date,
                    end_date=end_date, created=created, modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character relationship \
                    created by {self._owner.username}', created=datetime.now()
                )

                session.add(character_relationship)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_relationship

    def update_relationship(
        self, relationship_id: int, parent_id: int, related_id: int,
        relationship_type: str, description: str = None, start_date: str = None,
        end_date: str = None
    ) -> Type[CharacterRelationship]:
        """Update a character relationship

        Parameters
        ----------
        relationship_id : int
            The id of the relationship to update
        parent_id : int
            The id of the parent character
        related_id : int
            The id of the related character
        relationship_type : str
            The type of relationship
        description : str
            The description of the relationship, optional
        start_date : str
            The start date of the relationship, optional
        end_date : str
            The end date of the relationship, optional

        Returns
        -------
        CharacterRelationship
            The updated character relationship object
        """

        with self._session as session:
            try:
                character_relationship = session.query(
                    CharacterRelationship
                ).filter(
                    CharacterRelationship.id == relationship_id,
                    CharacterRelationship.user_id == self._owner.id
                ).first()

                if not character_relationship:
                    raise ValueError('Character relationship not found.')

                character_relationship.parent_id = parent_id
                character_relationship.related_id = related_id
                character_relationship.relationship_type = relationship_type
                character_relationship.description = description
                character_relationship.start_date = start_date
                character_relationship.end_date = end_date
                character_relationship.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character relationship \
                    updated by {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_relationship

    def change_relationship_position(
        self, relationship_id: int, position: int
    ) -> Type[CharacterRelationship]:
        """Set the position of a character relationship

        First, determine whether the new position is closer to 1 or further from 1. If closer to one, get all sibling
        CharacterRelationship objects with positions greater than or equal to the new position but less than the current
        position, and increment those position values by 1. If the target position is further away from 1 than the
        current position, get all sibling CharacterRelationship objects with positions greater than the current position
        but less than or equal to the new position, and decrement those position values by 1. Finally, set the position
        of the target CharacterRelationship object to the new position. Return the new position.

        Parameters
        ----------
        relationship_id : int
            The id of the relationship to update
        position : int
            The new position of the relationship

        Returns
        -------
        CharacterRelationship
            The updated character relationship object
        """

        with self._session as session:
            try:
                character_relationship = session.query(CharacterRelationship).filter(
                    CharacterRelationship.id == relationship_id, CharacterRelationship.user_id == self._owner.id
                ).first()

                if not character_relationship:
                    raise ValueError('Character relationship not found.')

                if position < 1:
                    raise ValueError('Position must be greater than 0.')

                if position == character_relationship.position:
                    return character_relationship

                if position < character_relationship.position:
                    for sibling in session.query(CharacterRelationship).filter(
                        CharacterRelationship.parent_id == character_relationship.parent_id,
                        CharacterRelationship.position >= position,
                        CharacterRelationship.position < character_relationship.position,
                        CharacterRelationship.user_id == self._owner.id
                    ).all():
                        sibling.position += 1

                else:
                    for sibling in session.query(CharacterRelationship).filter(
                        CharacterRelationship.parent_id == character_relationship.parent_id,
                        CharacterRelationship.position > character_relationship.position,
                        CharacterRelationship.position <= position,
                        CharacterRelationship.user_id == self._owner.id
                    ).all():
                        sibling.position -= 1

                character_relationship.position = position
                character_relationship.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character relationship \
                    position updated by {self._owner.username}',
                    created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_relationship

    def delete_relationship(self, relationship_id: int) -> bool:
        """Delete a character relationship

        Before deleting the CharacterRelationship object, all sibling objects with positions higher than the current
        position are decremented by one. The activity is then logged and the CharacterRelationship object is deleted.

        Parameters
        ----------
        relationship_id : int
            The id of the relationship to delete

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                character_relationship = session.query(
                    CharacterRelationship
                ).filter(
                    CharacterRelationship.id == relationship_id,
                    CharacterRelationship.user_id == self._owner.id
                ).first()

                if not character_relationship:
                    raise ValueError('Character relationship not found.')

                for sibling in session.query(CharacterRelationship).filter(
                    CharacterRelationship.parent_id == character_relationship.parent_id,
                    CharacterRelationship.position > character_relationship.position,
                    CharacterRelationship.user_id == self._owner.id
                ).all():
                    sibling.position -= 1

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character relationship \
                    deleted by {self._owner.username}', created=datetime.now()
                )

                session.delete(character_relationship)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_relationship_by_id(
        self, relationship_id: int
    ) -> Type[CharacterRelationship] | None:
        """Get a character relationship by id

        Parameters
        ----------
        relationship_id : int
            The id of the relationship to get

        Returns
        -------
        Type[CharacterRelationship] | None
            The character relationship if found, otherwise None
        """

        with self._session as session:
            character_relationship = session.query(
                CharacterRelationship
            ).filter(
                CharacterRelationship.id == relationship_id,
                CharacterRelationship.user_id == self._owner.id
            ).first()
            return character_relationship if character_relationship else None

    def get_relationships_by_character_id(
        self, parent_id: int
    ) -> List[Type[CharacterRelationship]]:
        """Get character relationships by character id, from that character's perspective

        Parameters
        ----------
        parent_id : int
            The id of the character

        Returns
        -------
        list
            The list of character relationships
        """

        with self._session as session:
            return session.query(CharacterRelationship).filter(
                CharacterRelationship.parent_id == parent_id,
                CharacterRelationship.user_id == self._owner.id
            ).all()

    def get_relationships_page_by_character_id(
        self, parent_id: int, page: int, per_page: int
    ) -> List[Type[CharacterRelationship]]:
        """Get a single page of character relationships by character id, from that character's perspective

        Parameters
        ----------
        parent_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of character relationships
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(CharacterRelationship).filter(
                CharacterRelationship.parent_id == parent_id,
                CharacterRelationship.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def create_trait(
        self, character_id: int, name: str, magnitude: int
    ) -> CharacterTrait:
        """Create a new character trait

        The position of the new trait must be determined by first finding the highest existing position among siblings,
        if any. Any other CharacterTrait objects associated with the same character are those siblings.

        Parameters
        ----------
        character_id : int
            The id of the character
        name : str
            The name of the trait
        magnitude : int
            The magnitude of the trait

        Returns
        -------
        CharacterTrait
            The new character trait object
        """

        with self._session as session:
            try:
                if not character_id or not name or not magnitude:
                    raise ValueError('Character id, name, and magnitude must be provided.')

                character = session.query(Character).filter(
                    Character.id == character_id,
                    Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                position = session.query(
                    func.max(CharacterTrait.position)
                ).filter(
                    CharacterTrait.character_id == character_id,
                    CharacterTrait.user_id == self._owner.id
                ).scalar()

                position = 1 if not position else position + 1
                created = datetime.now()
                modified = created
                character_trait = CharacterTrait(
                    user_id=self._owner.id, character_id=character_id,
                    position=position, name=name, magnitude=magnitude,
                    created=created, modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character trait {name} \
                    created by {self._owner.username} for "{character.__str__}"',
                    created=datetime.now()
                )

                session.add(character_trait)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_trait

    def update_trait(
        self, trait_id: int, name: str, magnitude: int
    ) -> Type[CharacterTrait]:
        """Update a character trait

        Parameters
        ----------
        trait_id : int
            The id of the trait to update
        name : str
            The name of the trait
        magnitude : int
            The magnitude of the trait

        Returns
        -------
        CharacterTrait
            The updated character trait object
        """

        with self._session as session:
            try:
                character_trait = session.query(CharacterTrait).filter(
                    CharacterTrait.id == trait_id,
                    CharacterTrait.user_id == self._owner.id
                ).first()

                if not character_trait:
                    raise ValueError('Character trait not found.')

                character_trait.name = name
                character_trait.magnitude = magnitude
                character_trait.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character trait \
                    {character_trait.__str__} updated by {self._owner.username}',
                    created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_trait

    def change_trait_position(
        self, trait_id: int, position: int
    ) -> Type[CharacterTrait]:
        """Set the position of a character trait

        First, determine whether the new position is closer to 1 or further from 1. If closer to one, get all sibling
        CharacterTraits with positions greater than or equal to the new position but less than the current position, and
        increment those position values by 1. If the target position is further away from 1 than the current position,
        get all sibling CharacterTraits with positions greater than the current position but less than or equal to the
        new position, and decrement those position values by 1. Finally, set the position of the target chapter to the
        new position. Return the new position.

        Parameters
        ----------
        trait_id : int
            The id of the trait to update
        position : int
            The position of the trait

        Returns
        -------
        CharacterTrait
            The updated character trait object
        """

        with self._session as session:
            try:

                config = ConfigParser()
                config.read("config.cfg")
                datetime_format = config.get("formats", "datetime")
                character_trait = session.query(CharacterTrait).filter(
                    CharacterTrait.id == trait_id, CharacterTrait.user_id == self._owner.id
                ).first()

                if not character_trait:
                    raise ValueError('Character trait not found.')

                if position < 1:
                    raise ValueError('Position must be greater than 0.')

                highest_position = session.query(func.max(CharacterTrait.position)).filter(
                    CharacterTrait.character_id == character_trait.character_id,
                    CharacterTrait.user_id == self._owner.id
                ).scalar()

                if position > highest_position:
                    raise ValueError(f'Position must be less than or equal to {highest_position}.')

                if position == character_trait.position:
                    return character_trait.position

                if position < character_trait.position:
                    siblings = session.query(CharacterTrait).filter(
                        CharacterTrait.character_id == character_trait.character_id,
                        CharacterTrait.position >= position,
                        CharacterTrait.user_id == self._owner.id,
                        CharacterTrait.position < character_trait.position
                    ).all()

                    for sibling in siblings:
                        sibling.position += 1
                        sibling.created = datetime.strptime(
                            str(sibling.created), datetime_format
                        )
                        sibling.modified = datetime.now()

                else:
                    siblings = session.query(CharacterTrait).filter(
                        CharacterTrait.character_id == character_trait.character_id,
                        CharacterTrait.position > character_trait.position,
                        CharacterTrait.position <= position,
                        CharacterTrait.user_id == self._owner.id
                    ).all()

                    for sibling in siblings:
                        sibling.position -= 1
                        sibling.created = datetime.strptime(
                            str(sibling.created), datetime_format
                        )
                        sibling.modified = datetime.now()

                character_trait.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character trait \
                    {character_trait.__str__} position changed by \
                    {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_trait

    def delete_trait(self, trait_id: int) -> bool:
        """Delete a character trait

        When a trait is deleted, all sibling traits having a higher position than the deleted trait must have their
        positions each decremented by 1. The activity is then logged and the CharacterTrait object is deleted.

        Parameters
        ----------
        trait_id : int
            The id of the trait to delete

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:

                config = ConfigParser()
                config.read("config.cfg")
                datetime_format = config.get("formats", "datetime")

                character_trait = session.query(CharacterTrait).filter(
                    CharacterTrait.id == trait_id,
                    CharacterTrait.user_id == self._owner.id
                ).first()

                if not character_trait:
                    raise ValueError('Character trait not found.')

                for sibling in session.query(CharacterTrait).filter(
                    CharacterTrait.character_id == character_trait.character_id,
                    CharacterTrait.position > character_trait.position,
                    CharacterTrait.user_id == self._owner.id
                ).all():
                    sibling.position -= 1
                    sibling.created = datetime.strptime(
                        str(sibling.created), datetime_format
                    )
                    sibling.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character trait \
                    {character_trait.__str__} deleted by \
                    {self._owner.username}', created=datetime.now()
                )

                session.delete(character_trait)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_trait_by_id(self, trait_id: int) -> Type[CharacterTrait] | None:
        """Get a character trait by id

        Parameters
        ----------
        trait_id : int
            The id of the trait to get

        Returns
        -------
        Type[CharacterTrait] | None
            The character trait if found, otherwise None
        """

        with self._session as session:
            character_trait = session.query(CharacterTrait).filter(
                CharacterTrait.id == trait_id,
                CharacterTrait.user_id == self._owner.id
            ).first()
            return character_trait if character_trait else None

    def get_traits_by_character_id(
        self, character_id: int
    ) -> List[Type[CharacterTrait]]:
        """Get character traits by character id

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            The list of character traits
        """

        with self._session as session:
            return session.query(CharacterTrait).filter(
                CharacterTrait.character_id == character_id,
                CharacterTrait.user_id == self._owner.id
            ).all()

    def get_traits_page_by_character_id(
        self, character_id: int, page: int, per_page: int
    ) -> List[Type[CharacterTrait]]:
        """Get a single page of character traits by character id

        Parameters
        ----------
        character_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of character traits
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(CharacterTrait).filter(
                CharacterTrait.character_id == character_id,
                CharacterTrait.user_id == self._owner.id
            ).offset(
                offset).limit(per_page).all()

    def append_events_to_character(
        self, character_id: int, event_ids: list
    ) -> Type[Character]:
        """Append events to a character

        Parameters
        ----------
        character_id : int
            The id of the character
        event_ids : list
            A list of event ids

        Returns
        -------
        Character
            The updated character object
        """

        with self._session as session:
            try:
                character = session.query(Character).filter(
                    Character.id == character_id,
                    Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                for event_id in event_ids:
                    event = session.query(Event).filter(
                        Event.id == event_id, Event.user_id == self._owner.id
                    ).first()

                    if not event:
                        raise ValueError('Event not found.')

                    character_event = CharacterEvent(
                        user_id=self._owner.id, character_id=character_id,
                        event_id=event_id, created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Event \
                        {event.title[:50]} associated with {character.__str__} \
                        by {self._owner.username}', created=datetime.now()
                    )

                    session.add(character_event)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def get_events_by_character_id(
        self, character_id: int
    ) -> List[Type[Event]]:
        """Get all events associated with a character

        Using the association of the CharacterEvent table, get all events from teh Event table associated with a
        character.

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            The list of events
        """

        with self._session as session:
            for character_event in session.query(CharacterEvent).filter(
                CharacterEvent.character_id == character_id,
                    CharacterEvent.user_id == self._owner.id
            ).all():
                yield session.query(Event).filter(
                    Event.id == character_event.event_id,
                    Event.user_id == self._owner.id
                ).first()

    def get_events_page_by_character_id(
        self, character_id: int, page: int, per_page: int
    ) -> List[Type[Event]]:
        """Get a single page of events associated with a character from the database

        Parameters
        ----------
        character_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of events
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(CharacterEvent).filter(
                CharacterEvent.character_id == character_id,
                CharacterEvent.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_links_to_character(
        self, character_id: int, link_ids: list
    ) -> Type[Character]:
        """Append links to a character

        Parameters
        ----------
        character_id : int
            The id of the character
        link_ids : list
            A list of link ids

        Returns
        -------
        Character
            The updated character object
        """

        with self._session as session:
            try:
                character = session.query(Character).filter(
                    Character.id == character_id,
                    Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                for link_id in link_ids:
                    link = session.query(Link).filter(
                        Link.id == link_id,
                        Link.user_id == self._owner.id
                    ).first()

                    if not link:
                        raise ValueError('Link not found.')

                    character_link = CharacterLink(
                        user_id=self._owner.id, character_id=character_id,
                        link_id=link_id, created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Link \
                        {link.title[:50]} associated with {character.__str__} \
                        by {self._owner.username}', created=datetime.now()
                    )

                    session.add(character_link)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def get_links_by_character_id(self, character_id: int) -> List[Type[Link]]:
        """Get all links associated with a character

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            The list of links
        """

        with self._session as session:
            for character_link in session.query(CharacterLink).filter(
                CharacterLink.character_id == character_id,
                CharacterLink.user_id == self._owner.id
            ).all():
                yield session.query(Link).filter(
                    Link.id == character_link.link_id,
                    Link.user_id == self._owner.id
                ).first()

    def get_links_page_by_character_id(
        self, character_id: int, page: int, per_page: int
    ) -> List[Type[Link]]:
        """Get a single page of links associated with a character from the database

        Parameters
        ----------
        character_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of links
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(CharacterLink).filter(
                CharacterLink.character_id == character_id,
                CharacterLink.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_notes_to_character(
        self, character_id: int, note_ids: list
    ) -> Type[Character]:
        """Append notes to a character

        Parameters
        ----------
        character_id : int
            The id of the character
        note_ids : list
            A list of note ids

        Returns
        -------
        Character
            The updated character object
        """

        with self._session as session:
            try:
                character = session.query(Character).filter(
                    Character.id == character_id,
                    Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                for note_id in note_ids:
                    note = session.query(Note).filter(
                        Note.id == note_id,
                        Note.user_id == self._owner.id
                    ).first()

                    if not note:
                        raise ValueError('Note not found.')

                    character_note = CharacterNote(
                        user_id=self._owner.id, character_id=character_id,
                        note_id=note_id, created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Note \
                        {note.title[:50]} associated with {character.__str__} \
                        by {self._owner.username}', created=datetime.now()
                    )

                    session.add(character_note)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def get_notes_by_character_id(self, character_id: int) -> List[Type[Note]]:
        """Get all notes associated with a character

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            The list of notes
        """

        with self._session as session:
            for character_note in session.query(CharacterNote).filter(
                CharacterNote.character_id == character_id,
                CharacterNote.user_id == self._owner.id
            ).all():
                yield session.query(Note).filter(
                    Note.id == character_note.note_id,
                    Note.user_id == self._owner.id
                ).first()

    def get_notes_page_by_character_id(
        self, character_id: int, page: int, per_page: int
    ) -> List[Type[Note]]:
        """Get a single page of notes associated with a character from the database

        Parameters
        ----------
        character_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of notes
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(CharacterNote).filter(
                CharacterNote.character_id == character_id,
                CharacterNote.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_images_to_character(
        self, character_id: int, image_ids: list
    ) -> Type[Character]:
        """Append images to a character

        As images are appended to the character, before each image is appended, the highest position among other images
        associated with this object is found and the new image is appended with a position one higher than the highest
        position.

        Parameters
        ----------
        character_id : int
            The id of the character
        image_ids : list
            A list of image ids

        Returns
        -------
        Character
            The updated character object
        """

        with self._session as session:
            try:
                character = session.query(Character).filter(
                    Character.id == character_id,
                    Character.user_id == self._owner.id
                ).first()

                if not character:
                    raise ValueError('Character not found.')

                for image_id in image_ids:
                    image = session.query(Image).filter(
                        Image.id == image_id,
                        Image.user_id == self._owner.id
                    ).first()

                    if not image:
                        raise ValueError('Image not found.')

                    position = session.query(
                        func.max(CharacterImage.position)
                    ).filter(
                        CharacterImage.character_id == character_id,
                        CharacterImage.user_id == self._owner.id
                    ).scalar()

                    position = 1 if not position else position + 1
                    is_default = False
                    created = datetime.now()
                    modified = created
                    character_image = CharacterImage(
                        user_id=self._owner.id, character_id=character_id,
                        image_id=image_id, position=position,
                        is_default=is_default, created=created,
                        modified=modified
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Image \
                        {image.filename[:50]} associated with character \
                        {str(character)[:50]} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.add(character_image)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character

    def change_image_position(
        self, image_id: int, position: int
    ) -> Type[CharacterImage]:
        """Set the position of a character image

        First, determine whether the new position is closer to 1 or further from 1. If closer to one, get all sibling
        CharacterImage objects with positions greater than or equal to the new position but less than the current
        position, and increment those position values by 1. If the target position is further away from 1 than the
        current position, get all sibling CharacterImage objects with positions greater than the current position but
        less than or equal to the new position, and decrement those position values by 1. Finally, set the position of
        the target CharacterImage object to the new position. Return the new position.

        Parameters
        ----------
        image_id : int
            The id of the image to update
        position : int
            The position of the image

        Returns
        -------
        CharacterImage
            The updated character image object
        """

        with self._session as session:
            try:

                config = ConfigParser()
                config.read("config.cfg")
                datetime_format = config.get("formats", "datetime")

                character_image = session.query(CharacterImage).filter(
                    CharacterImage.id == image_id,
                    CharacterImage.user_id == self._owner.id
                ).first()

                if not character_image:
                    raise ValueError('Character image not found.')

                if position < 1:
                    raise ValueError('Position must be greater than 0.')

                highest_position = session.query(
                    func.max(CharacterImage.position)
                ).filter(
                    CharacterImage.character_id == character_image.character_id,
                    CharacterImage.user_id == self._owner.id
                ).scalar()

                if position > highest_position:
                    raise ValueError(f'Position must be less than or equal to {highest_position}.')

                if position == character_image.position:
                    return character_image.position

                if position < character_image.position:
                    siblings = session.query(CharacterImage).filter(
                        CharacterImage.character_id == character_image.character_id,
                        CharacterImage.position >= position,
                        CharacterImage.user_id == self._owner.id,
                        CharacterImage.position < character_image.position
                    ).all()

                    for sibling in siblings:
                        sibling.position += 1
                        sibling.created = datetime.strptime(
                            str(sibling.created), datetime_format
                        )
                        sibling.modified = datetime.now()

                else:
                    siblings = session.query(CharacterImage).filter(
                        CharacterImage.character_id == character_image.character_id,
                        CharacterImage.position > character_image.position,
                        CharacterImage.position <= position,
                        CharacterImage.user_id == self._owner.id
                    ).all()

                    for sibling in siblings:
                        sibling.position -= 1
                        sibling.created = datetime.strptime(
                            str(sibling.created), datetime_format
                        )
                        sibling.modified = datetime.now()

                character_image.position = position
                character_image.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character image \
                    {character_image.__str__} position changed by \
                    {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_image

    def change_image_default_status(
        self, image_id: int, is_default: bool
    ) -> Type[CharacterImage]:
        """Set the default status of a character image

        If changing the value from true to false, it is straightforward - make the value change and save the object.
        However, if the value is changed from false to true, then before saving that new value in the object, the same
        attribute must first be set to false in all sibling CharacterImage objects. This is because only one image can
        be the default image for a character. The activity is then logged and the CharacterImage object is saved.

        Parameters
        ----------
        image_id : int
            The id of the image to update
        is_default : bool
            The default status of the image

        Returns
        -------
        CharacterImage
            The updated character image object
        """

        with self._session as session:
            try:
                character_image = session.query(CharacterImage).filter(
                    CharacterImage.id == image_id,
                    CharacterImage.user_id == self._owner.id
                ).first()

                if not character_image:
                    raise ValueError('Character image not found.')

                if is_default == character_image.is_default:
                    return character_image

                if is_default:
                    for sibling in session.query(CharacterImage).filter(
                        CharacterImage.character_id == character_image.character_id,
                        CharacterImage.user_id == self._owner.id
                    ).all():
                        sibling.is_default = False
                        sibling.modified = datetime.now()

                character_image.is_default = is_default
                character_image.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character image \
                    {character_image.__str__} default status changed by \
                    {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return character_image

    def delete_image(self, image_id: int) -> bool:
        """Delete a character image

        When an image is deleted, all sibling images having a higher position than the deleted image must have their
        positions each decremented by 1. The activity is then logged and the CharacterImage object is deleted. The
        Image object is also deleted.

        Parameters
        ----------
        image_id : int
            The id of the image to delete

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:

                config = ConfigParser()
                config.read("config.cfg")
                datetime_format = config.get("formats", "datetime")

                character_image = session.query(CharacterImage).filter(
                    CharacterImage.id == image_id,
                    CharacterImage.user_id == self._owner.id
                ).first()
                image = session.query(Image).filter(
                    Image.id == character_image.image_id,
                    Image.user_id == self._owner.id
                ).first()

                if not character_image:
                    raise ValueError('Character image not found.')

                for sibling in session.query(CharacterImage).filter(
                    CharacterImage.character_id == character_image.character_id,
                    CharacterImage.position > character_image.position,
                        CharacterImage.user_id == self._owner.id
                ).all():
                    sibling.position -= 1
                    sibling.created = datetime.strptime(
                        str(sibling.created), datetime_format
                    )
                    sibling.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Character image \
                    {image.caption[:50]} deleted by {self._owner.username}',
                    created=datetime.now()
                )

                session.delete(character_image)
                session.delete(image)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_image_count_by_character_id(self, character_id: int) -> int:
        """Get image count associated with a character

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        int
            The count of images
        """

        with self._session as session:
            return session.query(func.count(CharacterImage.id)).filter(
                CharacterImage.character_id == character_id,
                CharacterImage.user_id == self._owner.id
            ).scalar()

    def get_images_by_character_id(
        self, character_id: int
    ) -> List[Type[Image]]:
        """Get all images associated with a character

        The images will be returned in the order of their position. A yield is used to return the images one at a time.

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            The list of images
        """

        with self._session as session:
            for character_image in session.query(CharacterImage).filter(
                CharacterImage.character_id == character_id,
                    CharacterImage.user_id == self._owner.id
            ).order_by(CharacterImage.position).all():
                yield session.query(Image).filter(
                    Image.id == character_image.image_id,
                    Image.user_id == self._owner.id
                ).first()

    def get_images_page_by_character_id(
        self, character_id: int, page: int, per_page: int
    ) -> List[Type[Image]]:
        """Get a single page of images associated with a character from the database

        The images will be returned in the order of their position. A yield is used to return the images one at a time.

        Parameters
        ----------
        character_id : int
            The id of the character
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            The list of images
        """

        with self._session as session:
            offset = (page - 1) * per_page
            for character_image in session.query(CharacterImage).filter(
                CharacterImage.character_id == character_id,
                    CharacterImage.user_id == self._owner.id
            ).order_by(
                CharacterImage.position
            ).offset(offset).limit(per_page).all():
                yield session.query(Image).filter(
                    Image.id == character_image.image_id,
                    Image.user_id == self._owner.id
                ).first()
