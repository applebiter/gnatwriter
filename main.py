import threading
import time
from configparser import ConfigParser

from ollama import Client
from noveler.application import Noveler


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


config = ConfigParser()
config.read("config.cfg")
# db stuff
user = config.get("mysql", "user")
password = config.get("mysql", "password")
host = config.get("mysql", "host")
port = config.get("mysql", "port")
database = config.get("mysql", "database")
noveler = Noveler(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")
# ollama stuff
messages = [{'role': 'user', 'content': 'Why is the sky blue?'}]


def chat():
    """Example of how to use the chat method of the ChatController class.

    response = noveler("chat-assistant").chat('model name', [
        {'role': 'user', 'content': 'Why is the sky blue?'},
        {'role': 'assistant', 'content': 'Because the atmosphere scatters sunlight.'},
    ])

    The method is a wrapper around the chat method of the Ollama Client class. It takes a list of messages as input and
    returns a list of responses. The messages are dictionaries with two keys: role and content. The role key is a string
    that can be either 'user' or 'assistant'. The content key is a string that contains the message history of the chat
    session. The ollama system allows keeping models in memory for an arbitrary duration, but my concept for this app is
    that it could share an ollama server on a local network, and that means freeing up resources and making all
    interactions "one shot" interactions. This is why the keep_alive parameter is set to 0. There is overhead incurred
    loading the model with each call, but chat models are relatively small and load quickly.

    THAT BEING SAID - there's no way to integrate the ollama system with your own application without the use of either
    asynchronous programming or threading. No one is going to want to stop work altogether to wait for every response
    from the ollama models, as that would only magnify the latency inherent in running models on end-user hardware.
    """

    assistant = noveler("chat-assistant")
    response = assistant.chat(
        model='dolphin-phi:2.7b', messages=messages, stream=False, format='',
        options={'temperature': 1.0}, keep_alive=0)

    print(response)


t_chat = threading.Thread(target=chat)
t_cube = threading.Thread(target=print_cube, args=(10,))
t_square = threading.Thread(target=print_square, args=(10,))

t_chat.start()
print("Made remote call to ollama...")
t_cube.start()
print("Ran the cube function...")
t_square.start()
print("\nRan the square function...")
print("Probably still waiting on that chat response...")

t_chat.join()
t_cube.join()
t_square.join()

print("Now all threads are done.")
