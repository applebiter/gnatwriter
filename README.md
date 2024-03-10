# noveler
Noveler is a simple novel writing tool that allows you to write and organize your novel in a clean and simple interface. 
It is designed to be easy to use and to help you focus on writing your novel. It is written in Python and will use the 
Pyside6 library for the GUI. At this time, the app is in the early stages of development and is not yet ready for use. 
There will be integration with the ollama ecosystem, and the use of RAG and agent-based models to help the writer. I, 
for one, welcome our new language model _partners_, but I also want to do it on my own hardware, working just fine even 
in offline mode. 100% free, 100% open source, 100% private. The user can use which ever models they want, and the app 
will be able to use them, if the embeddings are compatible. 

Noveler uses the sqlalchemy ORM in the backend, and by default it is set to use sqlite. The user can change this to 
either postgres or mysql, but the user will have to set up the database themselves. My thinking was to go ahead and 
build out the models and controllers into a working framework, and then to build the GUI on top of that. This way, I am 
free to try out different GUI libraries, and I can also use the app in the terminal. 

I have zero experience building apps with LMs in the RAG framework, but I am excited to learn. My thinking is that I can 
keep the token window larger for each task by feeding the story as it is being written into the model, and then to
use the model to generate what ever comes next with more detail. There must be a way to make it possible to give the LM 
the ability to execute the API calls that could, for example, generate a list of characters, or to generate a list of 
locations, or to generate chapters and scenes as stubs.

Since one of my interests is already low-latency audio using JACK and JackTrip, I'm going to need to develop another 
application separately before I can integrate it into Noveler. The idea here is to use OpenAI's whisper model as a 
client on the Jack bus listen to the user and transcribe that for the LMs helping to write the story. Simultaneously,
I want to use a text-to-speech model to allow the agents to respond to the user in real time. This is a long-term goal, and I am not
expecting to have this feature in the app for a long time. Obviously, I'm thinking about an ecosystem of tools for a
local network that will work online or offline, where the user can carry on running conversations with multiple agents 
from anywhere in the home, office, or lab.
