from enum import Enum


class ImageMimeTypes(Enum):
    """The ImageMimeTypes class represents the types of image mime types.

    Attributes
    ----------
        JPEG: str
            The image is in JPEG format
        PNG: str
            The image is in PNG format
        GIF: str
            The image is in GIF format
    """
    JPEG = 'image/jpeg'
    PNG = 'image/png'
    GIF = 'image/gif'
