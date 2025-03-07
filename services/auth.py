from fastapi import Depends, HTTPException, status
from supabase import Client, create_client
from models.config import SupabaseConfig
import os
from models.auth import User, UserCreate, UserLogin, AuthResponse
from typing import Optional


def get_supabase_config() -> SupabaseConfig:
    return SupabaseConfig.from_env()


def get_supabase_client(
    config: SupabaseConfig = Depends(get_supabase_config),
) -> Client:
    return create_client(str(config.url), config.key)


class AuthService:
    def __init__(
        self,
        supabase: Client = Depends(get_supabase_client),
    ):
        self.supabase = supabase
        
        # Set site URL for redirects (important for verification emails)
        site_url = os.environ.get("SITE_URL", None)
        if site_url:
            self.supabase.auth.set_auth_config({
                "site_url": site_url
            })

    async def register(self, user_data: UserCreate) -> AuthResponse:
        try:
            auth_response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password
            })

            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed"
                )

            email = auth_response.user.email
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email cannot be None"
                )

            user = User(
                id=auth_response.user.id,
                email=email,
                email_confirmed=auth_response.user.email_confirmed_at is not None,
                last_sign_in=auth_response.user.last_sign_in_at
            )

            return AuthResponse(
                user=user,
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def login(self, credentials: UserLogin) -> AuthResponse:
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password
            })

            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

            email = auth_response.user.email
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email cannot be None"
                )

            user = User(
                id=auth_response.user.id,
                email=email,
                email_confirmed=auth_response.user.email_confirmed_at is not None,
                last_sign_in=auth_response.user.last_sign_in_at
            )

            return AuthResponse(
                user=user,
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )

    async def logout(self, access_token: str) -> bool:
        try:
            self.supabase.auth.sign_out(access_token)
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def get_current_user(self, access_token: Optional[str] = None) -> Optional[User]:
        if not access_token:
            return None

        try:
            auth_response = self.supabase.auth.get_user(access_token)
            if not auth_response.user:
                return None

            email = auth_response.user.email
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email cannot be None"
                )

            return User(
                id=auth_response.user.id,
                email=email,
                email_confirmed=auth_response.user.email_confirmed_at is not None,
                last_sign_in=auth_response.user.last_sign_in_at
            )
        except Exception:
            return None


async def get_auth_service(
    supabase: Client = Depends(get_supabase_client),
) -> AuthService:
    return AuthService(supabase)