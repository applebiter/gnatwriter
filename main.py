from noveler.noveler import Noveler

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

noveler = Noveler("sqlite:///noveler/noveler.db")

if noveler("story").count_stories() > 0:
    print("Stories found:")
    print(" ")
    for story in noveler("story").get_all_stories():
        print(f"\t{story.title}")
        print("\t\tContents:")
        chapter_count = noveler("chapter").count_chapters_by_story_id(story.id)
        if chapter_count > 0:
            for chapter in noveler("chapter").get_chapters_by_story_id(story.id):
                print(f"\t\t\t{chapter.title}  # Chapter ID# {chapter.id}")
                scene_count = noveler("scene").count_scenes_by_chapter_id(chapter.id)
                if scene_count > 0:
                    for scene in noveler("scene").get_scenes_by_chapter_id(chapter.id):
                        print(f"\t\t\t\t{scene.title}  # Scene ID# {scene.id}")
else:
    print("No stories found")
