from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, Text, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from gnatwriter.models import User, ImageLocation, LinkLocation, LocationNote, Base


class Location(Base):
    """The Location class represents a location associated with one or more stories.

    Attributes
    ----------
        id: int
            The location's id
        user_id: int
            The id of the owner of this entry
        title: str
            The location's title
        description: str
            The location's description
        address: str
            The location's address
        city: str
            The location's city
        state: str
            The location's state
        country: str
            The location's country
        zip_code: str
            The location's zip code
        latitude: float
            The location's latitude
        longitude: float
            The location's longitude
        created: str
            The creation datetime of the location
        modified: str
            The last modification datetime of the location
        user: User
            The user who owns this entry
        images: List[ImageLocation]
            The images that the location has
        links: List[LinkLocation]
            The links that the location has
        notes: List[LocationNote]
            The notes that the location has

    Methods
    -------
        __repr__()
            Returns a string representation of the location
        __str__()
            Returns a string representation of the location
        serialize()
            Returns a dictionary representation of the location
        unserialize(data: dict)
            Updates the location's attributes with the values from the dictionary
        validate_title(title: str)
            Validates the title's length
        validate_description(description: str)
            Validates the description's length
        validate_address(address: str)
            Validates the address's length
        validate_city(city: str)
            Validates the city's length
        validate_state(state: str)
            Validates the state's length
        validate_country(country: str)
            Validates the country's length
        validate_zip_code(zip_code: str)
            Validates the zip code's length
        validate_latitude(latitude: float)
            Validates the latitude's range
        validate_longitude(longitude: float)
            Validates the longitude's range
    """

    __tablename__ = 'locations'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(250), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(250), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    zip_code: Mapped[str] = mapped_column(String(20), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    created: Mapped[str] = mapped_column(DateTime, default=str(datetime.now()))
    modified: Mapped[str] = mapped_column(
        DateTime, default=str(datetime.now()), onupdate=str(datetime.now())
    )
    user: Mapped["User"] = relationship("User", back_populates="locations")
    images: Mapped[Optional[List["ImageLocation"]]] = relationship(
        "ImageLocation", back_populates="location",
        cascade="all, delete, delete-orphan")
    links: Mapped[Optional[List["LinkLocation"]]] = relationship(
        "LinkLocation", back_populates="location",
        cascade="all, delete, delete-orphan", lazy="joined")
    notes: Mapped[Optional[List["LocationNote"]]] = relationship(
        "LocationNote", back_populates="location",
        cascade="all, delete, delete-orphan", lazy="joined")

    def __repr__(self):
        """Returns a string representation of the location.

        Returns
        -------
        str
            A string representation of the location
        """

        return f'<Location {self.title!r}>'

    def __str__(self):
        """Returns a string representation of the location.

        Returns
        -------
        str
            A string representation of the location
        """

        return f'{self.title}'

    def serialize(self) -> dict:
        """Returns a dictionary representation of the location.

        Returns
        -------
        dict
            A dictionary representation of the location
        """

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created': str(self.created),
            'modified': str(self.modified),
        }

    def unserialize(self, data: dict) -> "Location":
        """Updates the location's attributes with the values from the dictionary.

        Parameters
        ----------
        data: dict
            The dictionary with the new values for the location

        Returns
        -------
        Location
            The unserialized location
        """

        self.user_id = data.get('user_id', self.user_id)
        self.title = data.get('title', self.title)
        self.description = data.get('description', self.description)
        self.address = data.get('address', self.address)
        self.city = data.get('city', self.city)
        self.state = data.get('state', self.state)
        self.country = data.get('country', self.country)
        self.zip_code = data.get('zip_code', self.zip_code)
        self.latitude = data.get('latitude', self.latitude)
        self.longitude = data.get('longitude', self.longitude)
        self.created = data.get('created', self.created)
        self.modified = data.get('modified', self.modified)

        return self

    @validates("title")
    def validate_title(self, key, title: str) -> str:
        """Validates the title's length

        Parameters
        ----------
        title: str
            The location's title

        Returns
        -------
        str
            The validated title
        """

        if title and len(title) > 250:
            raise ValueError("The location title can have no more than 250 characters.")

        return title

    @validates("description")
    def validate_description(self, key, description: str) -> str:
        """Validates the description's length

        Parameters
        ----------
        description: str
            The location's description

        Returns
        -------
        str
            The validated description
        """

        if description and len(description) > 65535:
            raise ValueError("The location description can have no more than 65,535 characters.")

        return description

    @validates("address")
    def validate_address(self, key, address: str) -> str:
        """Validates the address's length

        Parameters
        ----------
        address: str
            The location's address

        Returns
        -------
        str
            The validated address
        """

        if address and len(address) > 250:
            raise ValueError("The location address can have no more than 250 characters.")

        return address

    @validates("city")
    def validate_city(self, key, city: str) -> str:
        """Validates the city's length

        Parameters
        ----------
        city: str
            The location's city

        Returns
        -------
        str
            The validated city
        """

        if city and len(city) > 100:
            raise ValueError("The location city can have no more than 100 characters.")

        return city

    @validates("state")
    def validate_state(self, key, state: str) -> str:
        """Validates the state's length

        Parameters
        ----------
        state: str
            The location's state

        Returns
        -------
        str
            The validated state
        """

        if state and len(state) > 100:
            raise ValueError("The location state can have no more than 100 characters.")

        return state

    @validates("country")
    def validate_country(self, key, country: str) -> str:
        """Validates the country's length

        Parameters
        ----------
        country: str
            The location's country

        Returns
        -------
        str
            The validated country
        """

        if country and len(country) > 100:
            raise ValueError("The location country can have no more than 100 characters.")

        return country

    @validates("zip_code")
    def validate_zip_code(self, key, zip_code: str) -> str:
        """Validates the zip code's length

        Parameters
        ----------
        zip_code: str
            The location's zip code

        Returns
        -------
        str
            The validated zip code
        """

        if zip_code and len(zip_code) > 20:
            raise ValueError("The location zip code can have no more than 20 characters.")

        return zip_code

    @validates("latitude")
    def validate_latitude(self, key, latitude: float) -> float:
        """Validates the latitude's range

        Parameters
        ----------
        latitude: float
            The location's latitude

        Returns
        -------
        float
            The validated latitude
        """

        if type(latitude) is float:
            if latitude < -90.0 or latitude > 90.0:
                raise ValueError("The location latitude must be between -90 and 90.")

        return latitude

    @validates("longitude")
    def validate_longitude(self, key, longitude: float) -> float:
        """Validates the longitude's range

        Parameters
        ----------
        longitude: float
            The location's longitude

        Returns
        -------
        float
            The validated longitude
        """

        if type(longitude) is float:
            if longitude < -180.0 or longitude > 180.0:
                raise ValueError("The location longitude must be between -180 and 180.")

        return longitude
