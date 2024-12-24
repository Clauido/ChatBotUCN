import requests
import json
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, HTTPException, Header, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from squeme import WebSocketMessage,BodyGenerate
from utils import stream,ollam_url,format_ollama_messages,get_context
from config import UCN_MODEL_NAME

from auth.auth_google import google_callback, google_callback_url
from auth.jwt_utils import generate_token, verify_token
from auth.jwt_middleware import JWTMiddleware

app = FastAPI()

# CORS middleware. Restringir acceso antes de producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Proteger las rutas mediante un JWT. Asignar rutas desprotegidas mediante unprotected_routes
jwt_middleware = JWTMiddleware(unprotected_routes=["/auth/login/google", "/auth/callback/google"])
app.add_middleware(BaseHTTPMiddleware, dispatch=jwt_middleware)

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

### Auth
@app.get("/auth/login/google")
async def api_google_url():
    return await google_callback_url()

@app.get("/auth/callback/google")
async def api_google_callback(code: str):
    response = await google_callback(code)
    if response:
        return response
    raise HTTPException(status_code=400, detail="Error al validar el codigo de google, ¿estas reutilizando el codigo?")
 
@app.get("/auth/validate")
async def validate(authorization: str = Header(...)):
    try:
        # El middleware ya verifica el token, pero necesitamos obtener el payload para generar el payload del token nuevo.
        # No es necesario retornar nuevamente la informacion del usuario, guardarla es tarea del frontend.
        payload = verify_token(authorization)
        token = generate_token(payload["id"], payload["email"])
        return { "token": token } 
    except Exception as e:
        raise HTTPException(status_code=401, detail="Error al validar el token de acceso")
### End auth

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
