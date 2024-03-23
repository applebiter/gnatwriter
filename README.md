# noveler
Noveler is a framework for building a novel, short-story, or serial-writing app. It can be used-as is in scripts or in a
REPL, or it can be used as a back-end in a GUI app. Noveler uses a simple, plain-text format for writing and storing 
stories. It's designed to be easy to use and easy to extend. The app has a set of Assistants that help with writing,
editing, and managing stories. These Assistants are designed around the ollama ecosystem, allowing the user to use the 
GGUF models of their choice, and different models for different kinds of tasks. 

### How to install
Clone the repo and run `pip install .` in the root directory. If you use PyCharm, you can also open the project folder 
and the IDE will automatically install the dependencies. 

### How to use
Well, it's a framework without a front end, so the project becomes the basis of your own app. Consider this a skeleton 
application. You can use the `noveler` module in your own scripts, or you can use the `noveler` module in a GUI app.

## Getting started
Open main.py and begin using the framework. More helpful instructions will be added as the project develops.

### Examples
I'm currently using the framework to write the documentation for the project. I am including the noveler.db file in the 
project as both an example and documentation of how to use the framework. I will update the included database as I
continue to develop the project. If you execute the main.py file, you will see the following output:

```Stories found:
 
Noveler Documentation v.1.0
    Contents:
        Overview  # Chapter ID# 1
            Introduction  # Scene ID# 1
            Installation  # Scene ID# 2
        Getting Started  # Chapter ID# 2
            Creating a New Story, a New Chapter, and a New Scene  # Scene ID# 3
            Managing Story Submissions  # Scene ID# 4
            Attaching Notes and Web Links to Stories, Chapters, and Scenes  # Scene ID# 5
            Managing Characters  # Scene ID# 6
            Managing Events  # Scene ID# 7
            Managing Locations  # Scene ID# 8
            Managing Users  # Scene ID# 9
        Assistants  # Chapter ID# 3
            Introduction to the Ollama Ecosystem  # Scene ID# 10
            The Chat Assistant  # Scene ID# 11
            The Image Assistant  # Scene ID# 12
            The Generative Assistant  # Scene ID# 13
        Settings  # Chapter ID# 4
            General Settings  # Scene ID# 14
            User Settings  # Scene ID# 15
            Model Settings  # Scene ID# 16
        Models API  # Chapter ID# 5
            Activity  # Scene ID# 17
            Author  # Scene ID# 18
            AuthorStory  # Scene ID# 19
            Bibliography  # Scene ID# 20
            BibliographyAuthor  # Scene ID# 21
            Chapter  # Scene ID# 22
            ChapterLink  # Scene ID# 23
            ChapterNote  # Scene ID# 24
            Character  # Scene ID# 25
            CharacterEvent  # Scene ID# 26
            CharacterImage  # Scene ID# 27
            CharacterLink  # Scene ID# 28
            CharacterNote  # Scene ID# 29
            CharacterRelationshipTypes  # Scene ID# 30
            CharacterRelationship  # Scene ID# 31
            CharacterStory  # Scene ID# 32
            CharacterTrait  # Scene ID# 33
            Event  # Scene ID# 34
            EventLink  # Scene ID# 35
            EventLocation  # Scene ID# 36
            EventNote  # Scene ID# 37
            ImageMimeTypes  # Scene ID# 38
            Image  # Scene ID# 39
            ImageLocation  # Scene ID# 40
            Link  # Scene ID# 41
            LinkLocation  # Scene ID# 42
            LinkScene  # Scene ID# 43
            LinkStory  # Scene ID# 44
            Location  # Scene ID# 45
            LocationNote  # Scene ID# 46
            Note  # Scene ID# 47
            NoteScene  # Scene ID# 48
            NoteStory  # Scene ID# 49
            Scene  # Scene ID# 50
            Story  # Scene ID# 51
            SubmissionResultType  # Scene ID# 52
            Submission  # Scene ID# 53
            User  # Scene ID# 54
        Controllers API  # Chapter ID# 6
            ActivityController  # Scene ID# 55
            AuthorController  # Scene ID# 56
            BibliographyController  # Scene ID# 57
            ChapterController  # Scene ID# 58
            CharacterController  # Scene ID# 59
            EventController  # Scene ID# 60
            ImageController  # Scene ID# 61
            LinkController  # Scene ID# 62
            LocationController  # Scene ID# 63
            NoteController  # Scene ID# 64
            SceneController  # Scene ID# 65
            StoryController  # Scene ID# 66
            SubmissionController  # Scene ID# 67
            UserController  # Scene ID# 68
        Assistants API  # Chapter ID# 7
            ChatAssistant  # Scene ID# 69
            ImageAssistant  # Scene ID# 70
            GenerativeAssistant  # Scene ID# 71
