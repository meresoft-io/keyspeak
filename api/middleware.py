from fastapi import Request, Depends, FastAPI
from models.auth import JWTStatus
from services.auth import AuthService, get_auth_service
from starlette.middleware.base import BaseHTTPMiddleware


class TokenRefreshMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if access_token:
            jwt_status = AuthService.get_jwt_status(access_token)
            if jwt_status == JWTStatus.EXPIRED and refresh_token:
                refresh_response = await AuthService.refresh_token_static(refresh_token)
                access_token = refresh_response.access_token
                refresh_token = refresh_response.refresh_token

                # Update the request with the new tokens
                request.cookies["access_token"] = access_token
                request.cookies["refresh_token"] = refresh_token

                response = await call_next(request)
                response.set_cookie(
                    "access_token",
                    access_token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                )
                response.set_cookie(
                    "refresh_token",
                    refresh_token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                )
                return response
        return await call_next(request)
