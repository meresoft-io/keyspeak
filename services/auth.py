from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, Response
from supabase import Client, create_client
from models.config import SupabaseConfig, AppConfig
import os
from models.auth import User, UserCreate, UserLogin, AuthResponse
from typing import Optional, Union
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest


def get_supabase_config() -> SupabaseConfig:
    return SupabaseConfig.from_env()


def get_app_config() -> AppConfig:
    return AppConfig.from_env()


def get_supabase_client(
    config: SupabaseConfig = Depends(get_supabase_config),
) -> Client:
    return create_client(str(config.url), config.key)


class AuthService:
    def __init__(
        self,
        supabase: Client,
        app_config: AppConfig,
    ):
        self.supabase = supabase
        self.app_config = app_config

    async def register(self, user_data: UserCreate) -> AuthResponse:
        try:
            auth_response = self.supabase.auth.sign_up(
                {"email": user_data.email, "password": user_data.password}
            )

            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed",
                )

            email = auth_response.user.email
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email cannot be None",
                )

            user = User(
                id=auth_response.user.id,
                email=email,
                email_confirmed=auth_response.user.email_confirmed_at is not None,
                last_sign_in=auth_response.user.last_sign_in_at,
            )

            if not auth_response.session:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session cannot be None",
                )

            return AuthResponse(
                user=user,
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def login(self, credentials: UserLogin) -> AuthResponse:
        try:
            auth_response = self.supabase.auth.sign_in_with_password(
                {"email": credentials.email, "password": credentials.password}
            )

            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            email = auth_response.user.email
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email cannot be None",
                )

            user = User(
                id=auth_response.user.id,
                email=email,
                email_confirmed=auth_response.user.email_confirmed_at is not None,
                last_sign_in=auth_response.user.last_sign_in_at,
            )

            if not auth_response.session:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session cannot be None",
                )

            return AuthResponse(
                user=user,
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    async def logout(self) -> bool:
        try:
            # Sign out and invalidate the current session
            self.supabase.auth.sign_out()
            return True
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_current_user(
        self, access_token: Optional[str] = None
    ) -> Optional[User]:
        if not access_token:
            return None

        try:

            auth_response = self.supabase.auth.get_user(access_token)

            if not auth_response or not auth_response.user:
                return None

            email = auth_response.user.email
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email cannot be None",
                )

            return User(
                id=auth_response.user.id,
                email=email,
                email_confirmed=auth_response.user.email_confirmed_at is not None,
                last_sign_in=auth_response.user.last_sign_in_at,
            )
        except Exception:
            return None

    async def refresh_token(self, refresh_token: str) -> AuthResponse:
        try:

            auth_response = self.supabase.auth.refresh_session(refresh_token)

            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            email = auth_response.user.email
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email cannot be None",
                )

            user = User(
                id=auth_response.user.id,
                email=email,
                email_confirmed=auth_response.user.email_confirmed_at is not None,
                last_sign_in=auth_response.user.last_sign_in_at,
            )

            if not auth_response.session:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session cannot be None",
                )

            return AuthResponse(
                user=user,
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


async def get_auth_service(
    supabase: Client = Depends(get_supabase_client),
    app_config: AppConfig = Depends(get_app_config),
) -> AuthService:
    return AuthService(supabase, app_config)


async def require_auth(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> Union[User, Response]:
    # Try to get access token from cookies
    access_token = request.cookies.get("access_token")
    if access_token:
        # Try to get user with current access token
        current_user = await auth_service.get_current_user(access_token)
        if current_user:
            return current_user

    # If access token is invalid or missing, try to refresh
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            # Try to refresh the token
            auth_response = await auth_service.refresh_token(refresh_token)

            # Create a response that will be used to set cookies
            response = RedirectResponse(url=request.url.path)
            response.set_cookie(
                key="access_token",
                value=auth_response.access_token,
                httponly=True,
                secure=True,
                samesite="lax",
            )
            response.set_cookie(
                key="refresh_token",
                value=auth_response.refresh_token,
                httponly=True,
                secure=True,
                samesite="lax",
            )

            # Store the response in request state for later use
            request.state.auth_response = response
            return auth_response.user
        except:
            pass

    # If we get here, authentication failed
    # Store the original URL in the session for redirect after login
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="next", value=str(request.url), httponly=True, secure=True, samesite="lax"
    )

    return response
