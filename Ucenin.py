from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from langchain_ollama import OllamaLLM

app = FastAPI()

# Configura el modelo de Ollama
ollama_model = OllamaLLM(model='ucenin')

class Item(BaseModel):
    input: str

@app.get("/")
def read_root():
    return {"message": "¡Hola, mundo!"}

@app.post("/process")
def process(item: Item):
    input_text = item.input
    
    try:
        response = ollama_model.generate(prompts=[input_text])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"response": response}

@app.websocket("/ws/process")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                # Procesa el input con el modelo de Ollama
                response = ollama_model.generate(prompts=[data])
                
                # Extrae el texto de la respuesta
                result_text = response.generations[0][0].text if response.generations else "No response"
                
                # Envía la respuesta serializada
                await websocket.send_json({"response": result_text})
            except Exception as e:
                await websocket.send_json({"error": str(e)})
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
