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
    for story in noveler("story").get_all_stories():
        print(f"\tID#:{story.id}  {story.title}")
        chapter_count = noveler("chapter").count_chapters_by_story_id(story.id)
        print(f"\t\t{chapter_count} chapters:")
        for chapter in noveler("chapter").get_chapters_by_story_id(story.id):
            print(f"\t\t\tID#:{chapter.id}  {chapter.title}")
            scene_count = noveler("scene").count_scenes_by_chapter_id(chapter.id)
            print(f"\t\t\t{scene_count} scenes:")
            for scene in noveler("scene").get_scenes_by_chapter_id(chapter.id):
                print(f"\t\t\t\tID#:{scene.id}  {scene.title}")
                event_count = noveler("event").count_events_by_scene_id(scene.id)
                print(f"\t\t\t\t{event_count} events:")
                for event in noveler("event").get_events_by_scene_id(scene.id):
                    print(f"\t\t\t\t\tID#:{event.id}  {event.title}")
                    note_count = noveler("note").count_notes_by_event_id(event.id)
                    print(f"\t\t\t\t\t{note_count} notes:")
                    for note in noveler("note").get_notes_by_event_id(event.id):
                        print(f"\t\t\t\t\t\tID#:{note.id}  {note.title}")
else:
    print("No stories found")
