from typing import List

from fastapi.responses import JSONResponse
from auth.jwt_utils import verify_token
from fastapi import HTTPException, Request

class JWTMiddleware():
    def __init__(self, protected_routes: List[str]):
        self.protected_routes = protected_routes

    async def __call__(self, request: Request, call_next):
        # Proteger rutas
        if request.method == "OPTIONS":
            return await call_next(request)

        if request.url.path in self.protected_routes:
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

        # Saltar rutas desprotegidas
        return await call_next(request)
            