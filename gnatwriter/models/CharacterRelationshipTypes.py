from enum import Enum


class CharacterRelationshipTypes(Enum):
    """The CharacterRelationshipTypes class represents the types of relationships between characters.

    Attributes
    ----------
        FAMILY: str
            The relationship is familial
        PERSONAL: str
            The relationship is personal
        ROMANTIC: str
            The relationship is romantic
        PROFESSIONAL: str
            The relationship is professional
        OTHER: str
            The relationship is other
    """

    FAMILY = 'Family'
    PERSONAL = 'Personal'
    ROMANTIC = 'Romantic'
    PROFESSIONAL = 'Professional'
    OTHER = 'Other'
