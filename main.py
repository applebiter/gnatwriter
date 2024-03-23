import json
from application import Core
from controllers import verify_password

"""Example database connection strings

PostgreSQL = Core("postgresql+psycopg://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}", echo=False)
    Shown here using the psycopg driver, also known as psycopg3
MySQL = Core("mysql+mysqlconnector://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}", echo=False)
    Shown here using the mysql-connector-python driver
SQLite = Core("sqlite:///{dbname}.db", echo=False)

You supply the connection string to the Application class, and it will automatically generate the database schema. Shown 
here using the sqlite3 driver, which is included in the Python standard library. The echo parameter is optional and
defaults to False. If set to True, it will print all SQL commands to the console. This is useful for debugging.
"""

noveler = Core("sqlite:///noveler.db")

