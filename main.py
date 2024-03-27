from noveler.application import Noveler
from noveler.ollama import Client
from configparser import ConfigParser

"""Example database connection strings

noveler = Noveler("postgresql+psycopg://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}", echo=False)
    Shown here using the psycopg driver, also known as psycopg3
noveler = Noveler("mysql+mysqlconnector://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}", echo=False)
    Shown here using the mysql-connector-python driver
noveler = Noveler("sqlite:///{dbname}.db", echo=False)

You supply the connection string to the Noveler class, and it will automatically generate the database schema. Shown 
here using the sqlite3 driver, which is included in the Python standard library. The echo parameter is optional and
defaults to False. If set to True, it will print all SQL commands to the console. This is useful for debugging.
"""

config = ConfigParser()
config.read("config.cfg")
user = config.get("mysql", "user")
password = config.get("mysql", "password")
host = config.get("mysql", "host")
port = config.get("mysql", "port")
database = config.get("mysql", "database")
print(f"Connecting to database: {database}...")
noveler = Noveler(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")

print("Connecting to the ollama server on a remote host on the home network...")
client = Client()
response = client.list()
if response.get("models"):
    for model in response.get("models"):
        print(model.get("name"))
