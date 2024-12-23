from typing import List

from fastapi.responses import JSONResponse
from auth.jwt_utils import verify_token
from fastapi import HTTPException, Request

class JWTMiddleware():
    def __init__(self, unprotected_routes: List[str]):
        self.unprotected_routes = unprotected_routes

    async def __call__(self, request: Request, call_next):
        # Saltar rutas desprotegidas
        if request.url.path in self.unprotected_routes:
            return await call_next(request)

        # Verificar token        
        token = request.headers.get("Authorization");
        if token:
            try:
                verify_token(token)
                return await call_next(request) 
            except Exception:
                return JSONResponse (
                    status_code=401,
                    content={"detail": "Token de autenticacion no valido."}
                )
        return JSONResponse (
            status_code=401,
            content={"detail": "Token de autenticacion no presente en la peticion."}
        )
            