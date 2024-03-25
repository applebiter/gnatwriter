from noveler.application import Noveler

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

noveler = Noveler("sqlite:///noveler/noveler.db")

# Scene 1: Introduction:
content = """Noveler is a writing tool that helps the author manage story structure, and also separately develop 
characters, locations, and events. It's built ready to accommodate a universe, rather than just one story. Noveler is 
a framework for developing an API or a desktop application with a robust SQL back end. The framework itself can be used 
for a a single-user application or a multi-user application, with core user management features built in.

The framework is minimal but solid, and it is all it can be without a friendly user interface, and a paradigm choice 
to guide project file structure and state structure. I have been unable to settle on a paradigm, and have considered the 
following candidates:

1. A GUI front-end like PySide6 or PyQt6, which would be a lot of work, but would be the most user-friendly.
2. A REST API using Flask, which would be a lot of work, and still wouldn't provide a front end.
3. A command-line interface, which would be the least work, but would be the least user-friendly.

I have decided to go with both a GUI front end and a REST API, each separate but interoperable projects. The GUI front
end will be a PySide6 application, and the REST API will be a Flask application. So, two more git repositories to 
manage.
"""
scene_1 = noveler("scene").get_scene_by_id

if noveler("story").has_stories():
    print("Stories found:")
    print(" ")
    for story in noveler("story").get_all_stories():
        print(f"\t{story.title}")
        print("\t\tContents:")
        if noveler("story").has_chapters(story.id):
            for chapter in noveler("chapter").get_chapters_by_story_id(story.id):
                print(f"\t\t\t{chapter.title}  # Chapter ID# {chapter.id}")
                if noveler("chapter").has_scenes(chapter.id):
                    for scene in noveler("scene").get_scenes_by_chapter_id(chapter.id):
                        print(f"\t\t\t\t{scene.title}  # Scene ID# {scene.id}")

else:
    print("No stories found")
