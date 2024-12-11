import os
from dotenv import load_dotenv 
load_dotenv()

PGV_USER=os.getenv("PGV_USER")
PGV_PASSWORD=os.getenv("PGV_PASSWORD")
PGV_HOST=os.getenv("PGV_HOST")
PGV_PORT=os.getenv("PGV_PORT")
PGV_DATABASE_NAME=os.getenv("PGV_DATABASE_NAME")    

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
UCN_MODEL_NAME=os.getenv('UCN_MODEL_NAME')

OLLAMA_HOST= os.getenv("OLLAMA_HOST")
OLLAMA_PORT= int(os.getenv("OLLAMA_PORT")) 
url = f"http://localhost:{OLLAMA_PORT}/api/chat"