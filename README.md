# noveler
Noveler is a simple novel writing tool that allows you to write and organize your novel in a clean and simple interface. 
It is designed to be easy to use and to help you focus on writing your novel. At this time, the app is in the early 
stages of development and is not yet ready for use. There will be integration with the ollama ecosystem, and the use of 
RAG and agent models to help the writer. I, for one, welcome our new language model _partners_, but I also want to do it 
on my own hardware, working just fine even in offline mode. 100% free, 100% open source, 100% private. The user can use 
which ever models they want, and the app will be able to use them, if the embeddings are compatible. 

Noveler uses the SQLAlchemy 2.0 ORM in the backend, and by default it is set to use sqlite. The user can change this to 
either postgres or mysql, but the user will have to set up the database themselves, though this is pretty easy, since 
the app will create the database tables automatically once you've given it a valid connection string. My thinking was to 
go ahead and build out the models and controllers into a working framework, and then to build the GUI on top of that. 
This way, I am free to try out different GUI libraries, and I can also use the app in the terminal. 

### How it started and how it's going
The plan was a full GUI app with a backend, but I realized that I could use the backend as a standalone library, and 
then build the GUI on top of that. This way, I can use the app in the terminal, and I can also use it in a GUI. It's 
actually a little more than a library and a little less than a full app. It's a framework that can be used to build an 
app.

Since I'm not bound to a front-end, I'm thinking that I go ahead and integrate the app with the ollama ecosystem at this 
level. That will make building a different front-end easier, and it will also make it easier to use the app in the 
terminal.
