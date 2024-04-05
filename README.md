# noveler
A novel, short story, or serial writing library for Python that uses SQLAlchemy 
to store and retrieve data from different database backends. It also optionally 
offers tools based on the Ollama ecosystem for running large language models 
(LLMs) locally. 

### Installation
I'm still a newbie Python programmer, and have never used PyPi to distribute 
anything, so until I can figure all that out:
1. Download this repo
2. Inside the project root, run `python3 -m venv .venv`. This will create a 
virtual environment in the `.venv` directory.
3. While still in the project root, activate the virtual environment by running 
`source .venv/bin/activate` on Linux or `.\.venv\Scripts\activate` on Windows.
4. Install the project dependencies by running 
`pip install -r requirements.txt`.
5. Find the example configuration file in the project root called 
`noveler.cfg.example` and copy it to `noveler.cfg`. Change the settings as
needed.

### Usage
For now, the noveler.py script in the project root demonstrates how to use the
app. Import the `Noveler` class from the `noveler` module and create a new 
instance:

    from noveler.application import Noveler

    noveler = Noveler()

To use a controller, pass a controller name to the noveler instance. For 
example, to create a story do the following:

    story = noveler("story").create_story('title', 'description')

You also create Chapter and Scene objects separately, and then append them to
stories or chapters, respectively:

    chapter = noveler("chapter").create_chapter(story.id, 'title', 'description')
    scene = noveler("scene").create_scene(story.id, chapter.id, 'title', 'description', 'content')

Notes and Links can be attached to any of the above objects, as well as the 
other objects that are in the system, such as Events, Characters, and Locations.

Each of these objects can be retrieved by their ID, and the objects can be 
serialized. Top-level objects can be serialized with their children, so that a 
whole story, and all of its notes and web links, can be serialized in one go. 
The same is true for Events, Locations, and Characters.

    story_dict = noveler("story").get_story(story.id).serialize()

Internally, the method uses the `json` module and dumps() method to 
serialize the objects, so the output is formatted as very human-readable JSON.

More documentation will be forthcoming.