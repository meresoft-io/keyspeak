from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.responses import RedirectResponse, Response
from fastapi.security import OAuth2PasswordBearer
from supabase import Client, create_client
from models.auth import JWTStatus
from models.config import SupabaseConfig, AppConfig
from models.auth import User, UserCreate, UserLogin, AuthResponse, UserUpdate
from typing import Callable, Optional, Union, Dict, Any, Coroutine
from jose import jwt, JWTError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_supabase_config() -> SupabaseConfig:
    return SupabaseConfig.from_env()


def get_app_config() -> AppConfig:
    return AppConfig.from_env()


def get_supabase_client(
    config: SupabaseConfig = Depends(get_supabase_config),
) -> Client:
    return create_client(str(config.url), config.key)


def set_token_cookies(
    response: Response, access_token: str, refresh_token: str
) -> Response:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response


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

    async def get_current_user(self, access_token: str) -> Optional[User]:
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

    # Static version of refresh_token with no dependencies for use in middleware
    @staticmethod
    async def refresh_token_static(refresh_token: str) -> AuthResponse:
        supabase_config = get_supabase_config()
        supabase = get_supabase_client(supabase_config)
        auth_service = AuthService(supabase, get_app_config())
        return await auth_service.refresh_token(refresh_token)

    async def update_user(self, user: User, user_data: UserUpdate) -> User:
        update_data: Dict[str, Any] = {}

        if (
            user_data.phone_number is not None
            and user_data.phone_number != user.phone_number
        ):
            update_data["phone_number"] = user_data.phone_number

        # Handle email update separately as it's a special case
        if user_data.email is not None and user_data.email != user.email:
            update_data["email"] = str(user_data.email)

        # Update the user in Supabase using the access token
        response = self.supabase.auth.update_user(update_data)  # type: ignore

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update user",
            )

        email = response.user.email
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email cannot be None",
            )

        # Return updated user
        return User(
            id=response.user.id,
            email=email,
            email_confirmed=response.user.email_confirmed_at is not None,
            last_sign_in=response.user.last_sign_in_at,
            phone_number=response.user.user_metadata.get("phone_number"),
        )

    @staticmethod
    def get_jwt_status(access_token: str) -> JWTStatus:
        supabase_config = get_supabase_config()
        try:
            jwt.decode(
                access_token,
                supabase_config.jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            return JWTStatus.VALID
        except JWTError as e:
            if "expired" in str(e).lower():
                return JWTStatus.EXPIRED
            return JWTStatus.INVALID


async def get_auth_service(
    supabase: Client = Depends(get_supabase_client),
    app_config: AppConfig = Depends(get_app_config),
) -> AuthService:
    return AuthService(supabase, app_config)


async def require_auth(
    access_token: str | None = Cookie(default=None),
    config: SupabaseConfig = Depends(get_supabase_config),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    if access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode and verify the JWT using Supabase's secret
    payload = jwt.decode(
        access_token,
        config.jwt_secret,
        algorithms=["HS256"],
        options={"verify_aud": False},  # Supabase JWTs may not always include 'aud'
    )
    # 'sub' is the user ID in Supabase JWTs
    user_id: str | None = payload.get("sub")
    email: str | None = payload.get("email")
    if user_id is None or email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(id=user_id, email=email)
