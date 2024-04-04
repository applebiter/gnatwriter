import os
import sys
from os.path import realpath
from configparser import ConfigParser
from noveler.application import Noveler
from noveler.views import *
from PySide6.QtWidgets import QApplication, QTreeView

# Load the configuration
filepath = realpath(__file__)
project_root = os.path.dirname(filepath)
config = ConfigParser()
config.read(f"{project_root}/config.cfg")

# Database connection arguments
user = config.get("postgresql", "user")
password = config.get("postgresql", "password")
host = config.get("postgresql", "host")
port = config.get("postgresql", "port")
database = config.get("postgresql", "database")

# Take your pick

# PostgreSQL - Fastest, open source, and widely used by data scientists
# noveler = Noveler(f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}")

# MySQL - Fast, open source, and widely used by web developers
# noveler = Noveler(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")

# SQLite - Fast, local, lightweight, and included in the Python standard library
noveler = Noveler(f"sqlite:///{database}.db")

app = QApplication(sys.argv)
tree = QTreeView()
model = QtGui.QStandardItemModel()
# data = {"A": {"B": {"H": {}, "I": {"M": {}, "N": {}}}, "D": {}, "E": {}, "F": {}, "G": {"L": {}},
#               "C": {"J": {}, "K": {}}}}
story = noveler("story").get_story_by_id(1)
data = story.serialize()
fill_model_from_json(model.invisibleRootItem(), data)
tree.setModel(model)
tree.expandAll()
tree.resize(360, 480)
tree.show()
sys.exit(app.exec())
