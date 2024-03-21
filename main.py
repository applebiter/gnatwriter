import json
from application import Application
from controllers import verify_password

"""Example database connection strings

PostgreSQL = Application("postgresql+psycopg://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}", echo=False)
    Shown here using the psycopg driver, also known as psycopg3
MySQL = Application("mysql+mysqlconnector://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}", echo=False)
    Shown here using the mysql-connector-python driver
SQLite = Application("sqlite:///{dbname}.db", echo=False)

You supply the connection string to the Application class, and it will automatically generate the database schema. Shown 
here using the sqlite3 driver, which is included in the Python standard library. The echo parameter is optional and
defaults to False. If set to True, it will print all SQL commands to the console. This is useful for debugging.
"""

# Create the application
app = Application("sqlite:///noveler.db")

# Get the system user
user = app("user").get_user_by_username("noveler")

print("Is the password hasher working?")
password = "password"
if verify_password(password, user.password):
    print(f"Password '{password}' verified!")
else:
    print(f"Password '{password}' incorrect!")

# Get all stories
stories = app("story").get_all_stories()
print("Stories:")
for story in stories:
    print(story.title)

# LM Assistant session UUID
suuid = app.assistant("image").session_uuid
print(f'Session UUID: {suuid}')

# Get some test images and have the llava model describe them
images = [
    # "images/college_library.jpeg",
    # "images/john_jacob_jingleheimer_schmidt.jpeg",
    # "images/miss_mary_mack.jpeg",
    # "images/workshop.jpeg",
    # "images/kungfu.jpeg",
    "images/turquoise_fairy.jpg",
]
response1 = app.assistant("image").describe(
    images=images, temperature=1.0, session_uuid=suuid
)
print(response1)

# Chat with the chat assistant
# prompt = """What is the oldest form of Chinese kung-fu?
#     """
# response2 = app.assistant("chat").chat(
#     prompt=prompt, session_uuid=suuid, temperature=1.0
# )
# print(response2)
