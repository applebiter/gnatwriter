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
