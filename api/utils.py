import asyncio
from langchain_postgres.vectorstores import PGVector
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_ollama import OllamaLLM
from typing import List
from squeme import BodyGenerate
from config import (PGV_USER,PGV_PASSWORD,PGV_HOST,PGV_PORT,
                 PGV_DATABASE_NAME,EMBEDDING_MODEL,UCN_MODEL_NAME,
                 OLLAMA_HOST,OLLAMA_PORT)

def initialize_retriever():
    connection = f'postgresql+psycopg://{PGV_USER}:{PGV_PASSWORD}@{PGV_HOST}:{PGV_PORT}/{PGV_DATABASE_NAME}'
    vector_store = PGVector(
                embeddings=moder_for_embedding,
                connection=connection,
                use_jsonb=True,
            )
    retriever = vector_store.as_retriever(kwargs={"k":2})
    
    return retriever

def get_context(query):

    documents = retriever.invoke(input=query)

    context = "\n".join([doc.page_content for doc in documents])

    return context

def format_ollama_messages(body:BodyGenerate):
    history= body.history
    messages = []
    
    for item in history:
        messages.append({
            "role": "user",
            "content": item.query
        })
        messages.append({
            "role": "assistant",
            "content": item.answer
        })

    messages.append({"role":"user","content":item.query})
    print(messages)
    return messages


#for websocket endpoint
async def stream(query):
    loop = asyncio.get_event_loop()
    context= get_context()

    prompt = f"""
        Contexto : {context}
        Pregunta Alumno: {query}    
    """
    print(prompt)
    stream_gen = await loop.run_in_executor(None, model.stream, prompt)
    for response in stream_gen:
        print(response)
        yield response


ollam_url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat"

model = OllamaLLM(model=UCN_MODEL_NAME,host=OLLAMA_HOST,port=OLLAMA_PORT)

moder_for_embedding = FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)

retriever= initialize_retriever()