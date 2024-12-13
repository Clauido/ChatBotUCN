import os
import re
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

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 500


moder_for_embedding = FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

direc = './media/PDF'  # tener ojo con esta ruta, porque o sino no se hace el embeddign correcto
loader = PyPDFDirectoryLoader(direc)

pdfs = loader.load()

for pdf in pdfs:
    pdf.page_content = re.sub(r'\n\*?\s*\n\*?', ' ', pdf.page_content)
    pdf.page_content = re.sub(r'\s+\b', ' ', pdf.page_content)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

chunks = text_splitter.split_documents(pdfs)

PGVector.from_documents(chunks,moder_for_embedding,connection=connection)
print("Total document loaded:",len(chunks))
