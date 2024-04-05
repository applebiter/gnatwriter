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
3. From the project root, activate the virtual environment by running 
`source .venv/bin/activate` on Linux or `.\.venv\Scripts\activate` on Windows.
4. Install the project dependencies by running 
`pip install -r requirements.txt`.
5. Create a configuration file in the project root called `noveler.cfg`