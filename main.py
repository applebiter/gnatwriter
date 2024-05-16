from noveler import Noveler

nov = Noveler('noveler.cfg')
story = nov("story").get_story_by_id(1)
print(story.serialize())
