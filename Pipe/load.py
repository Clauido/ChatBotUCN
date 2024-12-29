import os
import json
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_postgres.vectorstores import PGVector
from dotenv import load_dotenv

load_dotenv()

PGV_USER=os.getenv("PGV_USER")
PGV_PASSWORD=os.getenv("PGV_PASSWORD")
PGV_HOST=os.getenv("PGV_HOST")
PGV_PORT=os.getenv("PGV_PORT")
PGV_DATABASE_NAME=os.getenv("PGV_DATABASE_NAME")
connection = f'postgresql+psycopg://{PGV_USER}:{PGV_PASSWORD}@localhost:{PGV_PORT}/{PGV_DATABASE_NAME}'
model_for_embedding = FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

CHUNKS_DIR = './media/JSON/'
json_file = f'{CHUNKS_DIR}chunks.json' 

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

chunks = []
for item in data:
    content = item['content']  
    metadata = item['metadata'] 
    chunks.append(Document(page_content=content, metadata=metadata))

PGVector.from_documents(chunks,model_for_embedding,connection=connection)
print("Total document loaded:",len(chunks))
