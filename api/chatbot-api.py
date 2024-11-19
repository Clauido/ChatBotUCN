from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
import os
from langchain_postgres.vectorstores import PGVector
from dotenv import load_dotenv
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
import asyncio


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

moder_for_embedding = FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)

model = OllamaLLM(model=UCN_MODEL_NAME,host=OLLAMA_HOST,port=OLLAMA_PORT)

class Item(BaseModel):
    input: str

app = FastAPI()

# CORS middleware. Restringir acceso antes de producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def initialize_retriever():
    connection = f'postgresql+psycopg://{PGV_USER}:{PGV_PASSWORD}@{PGV_HOST}:{PGV_PORT}/{PGV_DATABASE_NAME}'
    vector_store = PGVector(
                embeddings=moder_for_embedding,
                connection=connection,
                use_jsonb=True,
            )
    retriever = vector_store.as_retriever(kwargs={"k":2})
    
    return retriever

retriever= initialize_retriever()


async def stream(query):
    loop = asyncio.get_event_loop()
    
    documents = retriever.invoke(input=query)

    context = "\n".join([doc.page_content for doc in documents])

    prompt = f"""
        Contexto : {context}
        Pregunta Alumno: {query}    
    """

    stream_gen = await loop.run_in_executor(None, model.stream, prompt)
    for response in stream_gen:
        print(response)
        yield response



@app.websocket("/ws/generate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            async for response in stream(data):
                await websocket.send_text(response)
    except WebSocketDisconnect:
        print("Client disconnected")



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

