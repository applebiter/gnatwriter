from configparser import ConfigParser
from datetime import datetime
from typing import Type, List
from sqlalchemy.orm import Session
from gnatwriter.controllers.BaseController import BaseController
from gnatwriter.models import User, Image, Activity, ImageLocation


class ImageController(BaseController):
    """Image controller encapsulates image management functionality

    Attributes
    ----------
    _instance : ImageController
        The instance of the image controller
    _config: ConfigParser
        The configuration parser
    _owner : User
        The current user of the image controller
    _session : Session
        The database session

    Methods
    -------
    create_image(caption: str, filename: str, dirname: str, size_in_bytes: int, mime_type: str)
        Create a new image
    update_image(image_id: int, caption: str)
        Update an image
    delete_image(image_id: int)
        Delete an image
    get_all_images()
        Get all images associated with a user
    get_all_images_page(page: int, per_page: int)
        Get a single page of images associated with a user from the database
    search_images(search: str)
        Search for images by caption
    get_images_by_character_id(character_id: int)
        Get all images associated with a character
    get_images_page_by_character_id(character_id: int, page: int, per_page: int)
        Get a single page of images associated with a character from the database
    get_images_by_location_id(location_id: int)
        Get all images associated with a location
    get_images_page_by_location_id(location_id: int, page: int, per_page: int)
        Get a single page of images associated with a location from the database
    """

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_image(
        self, filename: str, dirname: str, size_in_bytes: int, mime_type: str,
        caption: str = None
    ) -> Image:
        """Create a new image

        Parameters
        ----------
        filename : str
            The filename of the image
        dirname : str
            The directory name of the image
        size_in_bytes : int
            The size of the image in bytes
        mime_type : str
            The mime type of the image
        caption : str
            The caption of the image, optional

        Returns
        -------
        Image
            The new image object
        """

        with self._session as session:
            try:
                created = datetime.now()
                modified = created

                image = Image(
                    user_id=self._owner.id, caption=caption, filename=filename,
                    dirname=dirname, size_in_bytes=size_in_bytes,
                    mime_type=mime_type, created=created, modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Image {image.id} created \
                    by {self._owner.username}', created=datetime.now()
                )

                session.add(image)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return image

    def update_image(self, image_id: int, caption: str = None) -> Type[Image]:
        """Update an image

        Parameters
        ----------
        image_id : int
            The id of the image
        caption : str
            The caption of the image, optional

        Returns
        -------
        Image
            The updated image object
        """

        with self._session as session:
            try:
                image = session.query(Image).filter(
                    Image.id == image_id,
                    Image.user_id == self._owner.id
                ).first()

                if not image:
                    raise ValueError('Image not found.')

                image.caption = caption
                image.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Image {image.id} updated \
                    by {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return image

    def delete_image(self, image_id: int) -> bool:
        """Delete an image

        Parameters
        ----------
        image_id : int
            The id of the image

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                image = session.query(Image).filter(
                    Image.id == image_id,
                    Image.user_id == self._owner.id
                ).first()

                if not image:
                    raise ValueError('Image not found.')

                activity = Activity(
                    user_id=self._owner.id, summary=f'Image {image.id} deleted \
                    by {self._owner.username}', created=datetime.now()
                )

                session.delete(image)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_all_images(self) -> List[Type[Image]]:
        """Get all images associated with a user

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            return session.query(Image).filter(
                Image.user_id == self._owner.id
            ).all()

    def get_all_images_page(
        self, page: int, per_page: int
    ) -> List[Type[Image]]:
        """Get a single page of images associated with a user from the database

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Image).filter(
                Image.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def search_images(self, search: str) -> List[Type[Image]]:
        """Search for images by caption

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            return session.query(Image).filter(
                Image.caption.like(f'%{search}%'),
                Image.user_id == self._owner.id
            ).all()

    def get_images_by_character_id(
        self, character_id: int
    ) -> List[Type[Image]]:
        """Get all images associated with a character

        Parameters
        ----------
        character_id : int
            The id of the character

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            return session.query(Image).filter(
                Image.character_id == character_id,
                Image.user_id == self._owner.id
            ).all()

    def get_images_page_by_character_id(
        self, character_id: int, page: int, per_page: int
    ) -> List[Type[Image]]:
        """Get a single page of images associated with a character from the database

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
            A list of image objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Image).filter(
                Image.character_id == character_id,
                Image.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def get_images_by_location_id(self, location_id: int) -> List[Type[Image]]:
        """Get all images associated with a location

        Images and Locations are associated through ImageLocation objects. This method will use yield to return the
        images one at a time.

        Parameters
        ----------
        location_id : int
            The id of the location

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            for image_location in session.query(ImageLocation).filter(
                ImageLocation.location_id == location_id,
                    ImageLocation.user_id == self._owner.id
            ).all():
                yield session.query(Image).filter(
                    Image.id == image_location.image_id,
                    Image.user_id == self._owner.id
                ).first()

    def get_images_page_by_location_id(
        self, location_id: int, page: int, per_page: int
    ) -> List[Type[Image]]:
        """Get a single page of images associated with a location from the database

        Images and Locations are associated through ImageLocation objects. This method will use yield to return the
        images one at a time.

        Parameters
        ----------
        location_id : int
            The id of the location
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of image objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            for image_location in session.query(ImageLocation).filter(
                ImageLocation.location_id == location_id,
                ImageLocation.user_id == self._owner.id
            ).offset(offset).limit(per_page).all():
                yield session.query(Image).filter(
                    Image.id == image_location.image_id,
                    Image.user_id == self._owner.id
                ).first()
