import requests
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from squeme import WebSocketMessage,BodyGenerate
from utils import stream,ollam_url,format_ollama_messages,get_context
from config import UCN_MODEL_NAME


app = FastAPI()

# CORS middleware. Restringir acceso antes de producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
def proxy_request(item: BodyGenerate):

    formated_messages= format_ollama_messages(item)
    data = {
        "model": UCN_MODEL_NAME,
        "messages": formated_messages
    }

    headers = {"Content-Type": "application/json"}
    json_data = json.dumps(data)

    response = requests.post(url=ollam_url, data=json_data, headers=headers, stream=True)

    if response.status_code == 200:
        def stream_response():
            for line in response.iter_lines():
                if line:  
                    decoded_line = line.decode("utf-8")
                    
                    data = json.loads(decoded_line)
                    print(f"Line received: {data["message"]}")
                    yield json.dumps({"response": json.loads(decoded_line)}) + "\n"

        return StreamingResponse(stream_response(), media_type="application/json")
    else:
        return {"error": f"Request failed with status code {response.status_code}"}

#sin historial todavía
@app.websocket("/ws/generate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            
            try:

                data = WebSocketMessage.model_validate_json(raw_data)
                
                # Enviar respuestas como stream
                async for response in stream(data.query):
                    await websocket.send_text(response)
            
            except ValidationError as e:
                # Responder con un error si el mensaje no es válido
                await websocket.send_text(f"Error de formato: {e}")
    
    except WebSocketDisconnect:
        print("Client disconnected")



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)