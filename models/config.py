from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")


class AppConfig(BaseModel):
    debug: bool = Field(False, description="Enable debug mode")

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(debug=os.getenv("DEBUG", "false").lower() == "true")


class SupabaseConfig(BaseModel):
    url: HttpUrl = Field(..., description="Supabase project URL")
    key: str = Field(..., min_length=1, description="Supabase anon key")
    jwt_secret: str = Field(..., description="JWT secret")

    @classmethod
    def from_env(cls) -> "SupabaseConfig":
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if url is None or key is None or jwt_secret is None:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY and SUPABASE_JWT_SECRET must be set in environment variables"
            )
        return cls(url=HttpUrl(url), key=key, jwt_secret=jwt_secret)


class OpenAIConfig(BaseModel):
    api_key: str = Field(..., min_length=1, description="OpenAI API key")

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        return cls(api_key=api_key)
