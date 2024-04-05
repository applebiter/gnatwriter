# noveler
A novel, short story, or serial writing library for Python that uses SQLAlchemy 
to store and retrieve data from different database backends. It also optionally 
offers tools based on the Ollama ecosystem for running large language models 
(LLMs) locally. 

### Installation
Manually:
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

Using pip:
From within your activated project, run `pip install noveler`.

### Usage
Import the `Noveler` class from the `noveler` module and create a new 
instance. Pass in the path to the configuration file as the only argument.

    from noveler import Noveler

    noveler = Noveler('path/to/noveler.cfg')

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

Noveler also exports Story and Character objects to plain text files, mainly to 
use as input for the LLM tools. Noveler uses the Ollama ecosystem and supporting
libraries to deliver a Retrieval-Augmented Generation session wherein the user 
may talk to the LLM about a story and/or characters. The ability to export Events and
Locations is not yet supported but will be in future releases.

More documentation can be found in [this project's wiki](https://github.com/applebiter/noveler/wiki/Introduction-to-Noveler).