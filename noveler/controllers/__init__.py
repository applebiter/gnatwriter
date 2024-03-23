from typing import Type
import bcrypt
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
import uuid
from noveler.controllers.BaseController import BaseController
from noveler.controllers.ActivityController import ActivityController
from noveler.controllers.AuthorController import AuthorController
from noveler.controllers.BibliographyController import BibliographyController
from noveler.controllers.ChapterController import ChapterController
from noveler.controllers.CharacterController import CharacterController
from noveler.controllers.EventController import EventController
from noveler.controllers.ImageController import ImageController
from noveler.controllers.LinkController import LinkController
from noveler.controllers.LocationController import LocationController
from noveler.controllers.NoteController import NoteController
from noveler.controllers.SceneController import SceneController
from noveler.controllers.StoryController import StoryController
from noveler.controllers.SubmissionController import SubmissionController
from noveler.controllers.UserController import UserController


def hash_password(password):
    """Hash a password, return hashed password"""

    if password == '':
        raise ValueError('The password cannot be empty.')

    if len(password) < 8:
        raise ValueError('The password must be at least 8 characters.')

    if len(password) > 24:
        raise ValueError('The password cannot be more than 24 characters.')

    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(rounds=12)).decode('utf8')


def verify_password(password, hashed_password):
    """Verify a password, return true if verified, false if not"""

    return bcrypt.checkpw(password.encode('utf8'), hashed_password.encode('utf8'))




