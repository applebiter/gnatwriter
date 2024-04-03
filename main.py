import os
from configparser import ConfigParser
from os.path import realpath

from noveler.application import Noveler


"""Example database connection strings

noveler = Noveler(f"postgresql+psycopg://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}", echo=False)
    Shown here using the psycopg driver, also known as psycopg3
noveler = Noveler(f"mysql+mysqlconnector://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}", echo=False)
    Shown here using the mysql-connector-python driver
noveler = Noveler(f"sqlite:///{dbname}.db", echo=False)

You supply the connection string to the Noveler class, and it will automatically generate the database schema. Shown 
here using the sqlite3 driver, which is included in the Python standard library. The echo parameter is optional and
defaults to False. If set to True, it will print all SQL commands to the console. This is useful for debugging.
"""

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

# PostgreSQL - Fast, open source, and widely used by data scientists
noveler = Noveler(f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}")

# MySQL - Fast, open source, and widely used by web developers
# noveler = Noveler(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")

# SQLite - Fast, lightweight, and included in the Python standard library
# noveler = Noveler(f"sqlite:///{database}.db")
