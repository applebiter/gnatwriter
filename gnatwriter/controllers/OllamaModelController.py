from configparser import ConfigParser
from datetime import datetime
from typing import Type, List
from sqlalchemy.orm import Session
from gnatwriter.controllers import BaseController
from gnatwriter.models import User, OllamaModel, Activity


class OllamaModelController(BaseController):
    """The OllamaModelController class encapsulates the logic for managing
    Ollama models in the database.
    """

    def __init__(
        self, config: ConfigParser, session: Session, owner: Type[User]
    ):
        """Initialize the class"""

        super().__init__(config, session, owner)

    def create_model(
        self, title: str, model: str, description: str = None,
        template: str = None, example: str = None, priming: str = None,
        params: str = None
    ) -> OllamaModel:
        """Create a model

        Parameters
        ----------
        title : str
            The title of the model
        model : str
            The model name
        description : str
            The model description
        template : str
            The model template
        example : str
            The model example
        priming : str
            The model priming
        params : str
            The model params

        Returns
        -------
        OllamaModel
            The model object
        """

        with self._session as session:

            try:

                created = datetime.now()
                modified = created

                model = OllamaModel(
                    title=title, model=model, description=description,
                    template=template, example=example, priming=priming,
                    params=params, created=created, modified=modified
                )

                activity = Activity(
                    user_id=self._owner.id, summary=f'Ollama model \
                    {model.title[:50]} created by {self._owner.username}',
                    created=datetime.now()
                )

                session.add(model)
                session.add(activity)

            except Exception as e:
                session.rollback()
                raise e

            else:
                session.commit()
                return model

    def get_model(self, model: str) -> Type[OllamaModel] | None:
        """Get an activity by id

        Parameters
        ----------

        Returns
        -------
        """

        with self._session as session:

            model = session.query(OllamaModel).filter(
                OllamaModel.model == model
            ).first()

            return model if model else None

    def get_models(self) -> List[Type[OllamaModel]]:
        """Get all models stored in the database

        Returns
        -------
        list
            A list of model objects
        """

        with self._session as session:
            return session.query(OllamaModel).all()

