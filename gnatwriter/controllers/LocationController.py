from configparser import ConfigParser
from datetime import datetime
from typing import Type, List
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from gnatwriter.controllers.BaseController import BaseController
from gnatwriter.models import User, Location, Activity, Image, ImageLocation, Link, LinkLocation, Note, LocationNote


class LocationController(BaseController):
    """Location controller encapsulates location management functionality

    Attributes
    ----------
    _instance : LocationController
        The instance of the location controller
    _config: ConfigParser
        The configuration parser
    _owner : User
        The current user of the location controller
    _session : Session
        The database session

    Methods
    -------
    create_location(title: str, description: str, address: str, city: str, state: str, country: str, zip_code: str, \
                    latitude: float, longitude: float)
        Create a new location
    update_location(location_id: int, title: str, description: str, address: str, city: str, state: str, country: str, \
                    zip_code: str, latitude: float, longitude: float)
        Update a location
    delete_location(location_id: int)
        Delete a location
    get_all_locations()
        Get all locations associated with a user
    get_all_locations_page(page: int, per_page: int)
        Get a single page of locations associated with a user from the database
    search_locations_by_title_and_description(search: str)
        Search for locations by title and description
    search_locations_by_address(search: str)
        Search for locations by address
    search_locations_by_city(search: str)
        Search for locations by city
    search_locations_by_state(search: str)
        Search for locations by state
    search_locations_by_country(search: str)
        Search for locations by country
    search_locations_by_zip_code(search: str)
        Search for locations by zip code
    append_images_to_location(location_id: int, images: list)
        Append images to a location
    get_images_by_location_id(location_id: int)
        Get all images associated with a location
    get_images_page_by_location_id(location_id: int, page: int, per_page: int)
        Get a single page of images associated with a location from the database
    append_links_to_location(location_id: int, links: list)
        Append links to a location
    get_links_by_location_id(location_id: int)
        Get all links associated with a location
    get_links_page_by_location_id(location_id: int, page: int, per_page: int)
        Get a single page of links associated with a location from the database
    append_notes_to_location(location_id: int, notes: list)
        Append notes to a location
    get_notes_by_location_id(location_id: int)
        Get all notes associated with a location
    get_notes_page_by_location_id(location_id: int, page: int, per_page: int)
        Get a single page of notes associated with a location from the database
    """

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_location(
        self, title: str, description: str = None, address: str = None,
        city: str = None, state: str = None, country: str = None,
        zip_code: str = None, latitude: float = None, longitude: float = None
    ) -> Location:
        """Create a new location

        Parameters
        ----------
        title : str
            The title of the location
        description : str
            The description of the location, optional
        address : str
            The address of the location, optional
        city : str
            The city of the location, optional
        state : str
            The state of the location, optional
        country : str
            The country of the location, optional
        zip_code : str
            The zip code of the location, optional
        latitude : float
            The latitude of the location, optional
        longitude : float
            The longitude of the location, optional

        Returns
        -------
        Location
            The new location object
        """

        with self._session as session:
            try:
                created = datetime.now()
                modified = created

                location = Location(
                    user_id=self._owner.id, title=title,
                    description=description, address=address, city=city,
                    state=state, country=country, zip_code=zip_code,
                    latitude=latitude, longitude=longitude, created=created,
                    modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Location {location.id} \
                    created by {self._owner.username}', created=datetime.now()
                )

                session.add(location)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return location

    def update_location(
        self, location_id: int, title: str, description: str = None,
        address: str = None, city: str = None, state: str = None,
        country: str = None, zip_code: str = None, latitude: float = None,
        longitude: float = None
    ) -> Type[Location]:
        """Update a location

        Parameters
        ----------
        location_id : int
            The id of the location
        title : str
            The title of the location
        description : str
            The description of the location
        address : str
            The address of the location
        city : str
            The city of the location
        state : str
            The state of the location
        country : str
            The country of the location
        zip_code : str
            The zip code of the location
        latitude : float
            The latitude of the location
        longitude : float
            The longitude of the location

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                location = session.query(Location).filter(
                    Location.id == location_id,
                    Location.user_id == self._owner.id
                ).first()

                if not location:
                    raise ValueError('Location not found.')

                location.title = title
                location.description = description
                location.address = address
                location.city = city
                location.state = state
                location.country = country
                location.zip_code = zip_code
                location.latitude = latitude
                location.longitude = longitude
                location.modified = datetime.now()

                activity = Activity(
                    user_id=self._owner.id, summary=f'Location {location.id} \
                    updated by {self._owner.username}', created=datetime.now()
                )

                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return location

    def delete_location(self, location_id: int) -> bool:
        """Delete a location

        Parameters
        ----------
        location_id : int
            The id of the location

        Returns
        -------
        bool
            True on success
        """

        with self._session as session:
            try:
                location = session.query(Location).filter(
                    Location.id == location_id,
                    Location.user_id == self._owner.id
                ).first()

                if not location:
                    raise ValueError('Location not found.')

                activity = Activity(
                    user_id=self._owner.id, summary=f'Location {location.id} \
                    deleted by {self._owner.username}', created=datetime.now()
                )

                session.delete(location)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return True

    def get_all_locations(self) -> List[Type[Location]]:
        """Get all locations associated with an owner

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(
                Location.user_id == self._owner.id
            ).all()

    def get_all_locations_page(
        self, page: int, per_page: int
    ) -> List[Type[Location]]:
        """Get a single page of locations associated with an owner from the database

        Parameters
        ----------
        page : int
            The page number
        per_page : int
            The number of rows per page

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(Location).filter(
                Location.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def search_locations_by_title_and_description(
        self, search: str
    ) -> List[Type[Location]]:
        """Search for locations by title and description

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(
                Location.user_id == self._owner.id,
                or_(
                    Location.title.like(f'%{search}%'),
                    Location.description.like(f'%{search}%')
                )
            ).all()

    def search_locations_by_address(self, search: str) -> List[Type[Location]]:
        """Search for locations by address

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(
                Location.address.like(f'%{search}%'),
                Location.user_id == self._owner.id
            ).all()

    def search_locations_by_city(self, search: str) -> List[Type[Location]]:
        """Search for locations by city

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(
                Location.city.like(f'%{search}%'),
                Location.user_id == self._owner.id
            ).all()

    def search_locations_by_state(self, search: str) -> List[Type[Location]]:
        """Search for locations by state

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(
                Location.state.like(f'%{search}%'),
                Location.user_id == self._owner.id
            ).all()

    def search_locations_by_country(self, search: str) -> List[Type[Location]]:
        """Search for locations by country

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(
                Location.country.like(f'%{search}%'),
                Location.user_id == self._owner.id
            ).all()

    def search_locations_by_zip_code(self, search: str) -> List[Type[Location]]:
        """Search for locations by zip code

        Parameters
        ----------
        search : str
            The search string

        Returns
        -------
        list
            A list of location objects
        """

        with self._session as session:
            return session.query(Location).filter(
                Location.zip_code.like(f'%{search}%'),
                Location.user_id == self._owner.id
            ).all()

    def append_images_to_location(
        self, location_id: int, image_ids: list
    ) -> Type[Location]:
        """Append images to a location

        Parameters
        ----------
        location_id : int
            The id of the location
        image_ids : list
            A list of image ids

        Returns
        -------
        Location
            The updated location object
        """

        with self._session as session:
            try:
                location = session.query(Location).filter(
                    Location.id == location_id,
                    Location.user_id == self._owner.id
                ).first()

                if not location:
                    raise ValueError('Location not found.')

                for image_id in image_ids:
                    image = session.query(Image).filter(
                        Image.id == image_id,
                        Image.user_id == self._owner.id
                    ).first()

                    if not image:
                        raise ValueError('Image not found.')

                    position = session.query(
                        func.max(ImageLocation.position)
                    ).filter(
                        ImageLocation.location_id == location_id
                    ).scalar()
                    position = position + 1 if position else 1
                    is_default = False
                    created = datetime.now()
                    modified = created

                    image_location = ImageLocation(
                        user_id=self._owner.id, location_id=location_id,
                        image_id=image_id, position=position,
                        is_default=is_default, created=created,
                        modified=modified
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Image \
                        {image.caption[:50]} associated with location \
                        {location.title[:50]} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.add(image_location)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return location

    def get_images_by_location_id(self, location_id: int) -> List[Type[Image]]:
        """Get all images associated with a location

        The images should be returned in the order determined by the position field in the ImageLocation table.

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
            ).order_by(ImageLocation.position).all():

                yield session.query(Image).filter(
                    Image.id == image_location.image_id,
                    Image.user_id == self._owner.id
                ).first()

    def get_images_page_by_location_id(
        self, location_id: int, page: int, per_page: int
    ) -> List[Type[Image]]:
        """Get a single page of images associated with a location from the database

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
            return session.query(ImageLocation).filter(
                ImageLocation.location_id == location_id,
                ImageLocation.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_links_to_location(
        self, location_id: int, link_ids: list
    ) -> Type[Location]:
        """Append links to a location

        Parameters
        ----------
        location_id : int
            The id of the location
        link_ids : list
            A list of link ids

        Returns
        -------
        Location
            The updated location object
        """

        with self._session as session:
            try:
                location = session.query(Location).filter(
                    Location.id == location_id,
                    Location.user_id == self._owner.id
                ).first()

                if not location:
                    raise ValueError('Location not found.')

                for link_id in link_ids:
                    link = session.query(Link).filter(
                        Link.id == link_id,
                        Link.user_id == self._owner.id
                    ).first()

                    if not link:
                        raise ValueError('Link not found.')

                    link_location = LinkLocation(
                        user_id=self._owner.id, location_id=location_id,
                        link_id=link_id, created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Link \
                        {link.title[:50]} associated with location \
                        {location.title[:50]} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.add(link_location)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return location

    def get_links_by_location_id(self, location_id: int) -> List[Type[Link]]:
        """Get all links associated with a location

        Parameters
        ----------
        location_id : int
            The id of the location

        Returns
        -------
        list
            A list of link objects
        """

        with self._session as session:
            for link_location in session.query(LinkLocation).filter(
                LinkLocation.location_id == location_id,
                LinkLocation.user_id == self._owner.id
            ).all():
                yield session.query(Link).filter(
                    Link.id == link_location.link_id,
                    Link.user_id == self._owner.id
                ).first()

    def get_links_page_by_location_id(
        self, location_id: int, page: int, per_page: int
    ) -> List[Type[Link]]:
        """Get a single page of links associated with a location from the database

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
            A list of link objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(LinkLocation).filter(
                LinkLocation.location_id == location_id,
                LinkLocation.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()

    def append_notes_to_location(
        self, location_id: int, note_ids: list
    ) -> Type[Location]:
        """Append notes to a location

        Parameters
        ----------
        location_id : int
            The id of the location
        note_ids : list
            A list of note ids

        Returns
        -------
        Location
            The updated location object
        """

        with self._session as session:
            try:
                location = session.query(Location).filter(
                    Location.id == location_id,
                    Location.user_id == self._owner.id
                ).first()

                if not location:
                    raise ValueError('Location not found.')

                for note_id in note_ids:
                    note = session.query(Note).filter(
                        Note.id == note_id,
                        Note.user_id == self._owner.id
                    ).first()

                    if not note:
                        raise ValueError('Note not found.')

                    location_note = LocationNote(
                        user_id=self._owner.id, location_id=location_id,
                        note_id=note_id, created=datetime.now()
                    )

                    activity = Activity(
                        user_id=self._owner.id, summary=f'Note \
                        {note.title[:50]} associated with location \
                        {location.title[:50]} by {self._owner.username}',
                        created=datetime.now()
                    )

                    session.add(location_note)
                    session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return location

    def get_notes_by_location_id(self, location_id: int) -> List[Type[Note]]:
        """Get all notes associated with a location

        Parameters
        ----------
        location_id : int
            The id of the location

        Returns
        -------
        list
            A list of note objects
        """

        with self._session as session:
            for location_note in session.query(LocationNote).filter(
                LocationNote.location_id == location_id,
                LocationNote.user_id == self._owner.id
            ).all():
                yield session.query(Note).filter(
                    Note.id == location_note.note_id,
                    Note.user_id == self._owner.id
                ).first()

    def get_notes_page_by_location_id(
        self, location_id: int, page: int, per_page: int
    ) -> List[Type[Note]]:
        """Get a single page of notes associated with a location from the database

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
            A list of note objects
        """

        with self._session as session:
            offset = (page - 1) * per_page
            return session.query(LocationNote).filter(
                LocationNote.location_id == location_id,
                LocationNote.user_id == self._owner.id
            ).offset(offset).limit(per_page).all()
