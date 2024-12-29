import json
import re
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 500

media_dir='./media'
markdowns_direc = media_dir+'/markdown'  # tener ojo con esta ruta, porque sino no se hace el embeddign correcto

archivos_md = [f'{markdowns_direc}/{file.name.split('.md')[0]}/{file.name}' for file in Path(markdowns_direc).rglob("*.md")]

print("Files Fund:", archivos_md)

docs = []
for archivo in archivos_md:
    loader = UnstructuredMarkdownLoader(file_path=archivo)
    docs.extend(loader.load())

for doc in docs:
    doc.page_content = re.sub(r'\n\*?\s*\n\*?', ' ', doc.page_content)
    doc.page_content = re.sub(r'\s+\b', ' ', doc.page_content)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

chunks = text_splitter.split_documents(docs)

output_file = media_dir+"/JSON/chunks.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump([{"content": chunk.page_content, "metadata": chunk.metadata} for chunk in chunks], f, ensure_ascii=False, indent=4)

print(f"Chunks exportados a {output_file}")