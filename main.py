import threading
from configparser import ConfigParser
from noveler.application import Noveler
import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings


def print_cube(num):
    print("Cube: {}".format(num * num * num))


def print_square(num):
    print("Square: {}".format(num * num))


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

config = ConfigParser()
config.read("config.cfg")

# db stuff
user = config.get("mysql", "user")
password = config.get("mysql", "password")
host = config.get("mysql", "host")
port = config.get("mysql", "port")
database = config.get("mysql", "database")

# noveler = Noveler(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")
noveler = Noveler(f"sqlite:///{database}.db")

# reach out to the ollama server for updates
noveler("assistant").update_models()

# ollama RAG stuff
export_root = config.get("export", "root")
user_uuid = "33e3f024-cf90-428c-97b0-b1202f0507ce"
story_textfile = f"{export_root}/{user_uuid}/stories/1/story.txt"
# load input documents
loader = TextLoader(story_textfile)
input_docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(input_docs)
# Create Ollama embeddings and vector store
embeddings = OllamaEmbeddings(model="mistral-openorca:7b")
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
# Create the retriever
retriever = vectorstore.as_retriever()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Define the Ollama LLM function
def ollama_llm(question, context):
    formatted_prompt = f"Question: {question}\n\nContext: {context}"
    response = ollama.chat(
        model="mistral-openorca:7b",
        messages=[{'role': 'user', 'content': formatted_prompt, 'options': {
            'temperature': 0.5, "keep_alive": 0
        }}]
    )
    return response['message']['content']


# Define the RAG chain
def rag_chain(question):
    retrieved_docs = retriever.invoke(question)
    formatted_context = format_docs(retrieved_docs)
    return ollama_llm(question, formatted_context)


# Use the RAG chain
result = rag_chain("Who is Flando?")  # medllama2:7b only model so far to correctly name him as the rat
print(result)
#
# Export the existing story to JSON and text
# noveler("export").export_story_to_json(story_id=1)
noveler("export").export_story_to_text(story_id=1)

# def chat(prompt):
#     """Example of how to use the chat method of the ChatController class.
#
#     response = noveler("assistant").chat('Why is the sky blue?')
#
#     The method is a wrapper around the chat method of the Ollama Client class. It takes a list of messages as input and
#     returns a list of responses. The messages are dictionaries with two keys: role and content. The role key is a string
#     that can be either 'user' or 'assistant'. The content key is a string that contains the message history of the chat
#     session. The ollama system allows keeping models in memory for an arbitrary duration, but my concept for this app is
#     that it could share an ollama server on a local network, and that means freeing up resources and making all
#     interactions "one shot" interactions. This is why the keep_alive parameter is set to 0. There is overhead incurred
#     loading the model with each call, but chat models are relatively small and load quickly.
#
#     THAT BEING SAID - there's no way to integrate the ollama system with your own application without the use of either
#     asynchronous programming or threading. No one is going to want to stop work altogether to wait for every response
#     from the ollama models, as that would only magnify the latency inherent in running models on end-user hardware.
#     """
#
#     response = noveler("assistant").chat(prompt=prompt, temperature=1.0)
#
#     print(response["message"]["content"])
#

# t_chat = threading.Thread(target=chat, args=("Who is Black Sabbath?",))
# t_cube = threading.Thread(target=print_cube, args=(10,))
# t_square = threading.Thread(target=print_square, args=(10,))
#
# t_chat.start()
# print("Made remote call to ollama...")
# t_cube.start()
# print("Ran the cube function...")
# t_square.start()
# print("\nRan the square function...")
# print("Probably still waiting on that chat response...")
#
# t_chat.join()
# t_cube.join()
# t_square.join()
#
# print("Now all threads are done.")
