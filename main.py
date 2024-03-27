import time
from noveler.application import Noveler
from configparser import ConfigParser
from ollama import Client
import threading


def print_cube(num):
    print("Cube: {}".format(num * num * num))


def print_square(num):
    print("Square: {}".format(num * num))


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

# config = ConfigParser()
# config.read("config.cfg")
# user = config.get("mysql", "user")
# password = config.get("mysql", "password")
# host = config.get("mysql", "host")
# port = config.get("mysql", "port")
# database = config.get("mysql", "database")
# print(f"Connecting to database: {database}...")
# noveler = Noveler(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")


def chat():
    message = {'role': 'user', 'content': 'Why is the sky blue?'}
    client = Client(host="http://violet:11434")
    resp = client.chat(model='llama2:7b', messages=[message])
    print(resp)
    

t_chat = threading.Thread(target=chat)
t_cube = threading.Thread(target=print_cube, args=(10,))
t_square = threading.Thread(target=print_square, args=(10,))

t_chat.start()
print("Made remote call to ollama...")
t_cube.start()
print("Ran the cube function...")
t_square.start()
print("Ran the square function...")
print("Probably still waiting on that chat response...")

t_chat.join()
t_cube.join()
t_square.join()

print("Now all threads are done.")
