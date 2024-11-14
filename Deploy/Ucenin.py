from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
import os
from langchain_postgres.vectorstores import PGVector
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

load_dotenv()

PGV_USER=os.getenv("PGV_USER")
PGV_PASSWORD=os.getenv("PGV_PASSWORD")
PGV_HOST=os.getenv("PGV_HOST")
PGV_PORT=os.getenv("PGV_PORT")
PGV_DATABASE_NAME=os.getenv("PGV_DATABASE_NAME")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

app = FastAPI()

ollama_model = OllamaLLM(model='ucenin')

custom_prompt_template = """
Contexto: {context}
Pregunta: {question}

Responde siempre en español a no ser que te pidan lo contrario.
Respuesta útil:
"""
moder_for_embedding = FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

prompt = PromptTemplate(template=custom_prompt_template, input_variables=['context', 'question'])

def initialize_qa():
    
    connection = f'postgresql+psycopg://{PGV_USER}:{PGV_PASSWORD}@{PGV_HOST}:{PGV_PORT}/{PGV_DATABASE_NAME}'
    
    vector_store = PGVector(
                embeddings=moder_for_embedding,
                connection=connection,
                use_jsonb=True,
            )
    retriever = vector_store.as_retriever(kwargs={"k":2})

    qa = RetrievalQA.from_chain_type(
        llm=ollama_model,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt, 
                           "verbose": True
                           }
    )

    return qa

# Inicializar QA al iniciar la aplicación
qa = initialize_qa()

# Modelos de Pydantic
class Item(BaseModel):
    input: str

@app.get("/")
def read_root():
    return {"message": "¡Hola, mundo!"}

@app.post("/generate")
def process(item: Item):
    input_text = item.input
    
    try:
        response = qa.invoke({"query": input_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"response": response}

@app.websocket("/ws/generate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                response = qa.invoke({"query": data})
                print(response)
                result_text = response['result']
  
                await websocket.send_json({"response": result_text})
            except Exception as e:
                await websocket.send_json({"error": str(e)})
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
