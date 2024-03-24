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

scene = noveler("scene").create_scene(
    story_id=1, chapter_id=5, title="Base",
    description="This scene will provide info on the Base model.",
    content="@todo: Write the content for this scene."
)
scene = noveler("scene").change_scene_position(scene_id=scene.id, position=5)

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
