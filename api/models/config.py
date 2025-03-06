from pydantic import BaseModel, HttpUrl, Field
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")


class SupabaseConfig(BaseModel):
    url: HttpUrl = Field(..., description="Supabase project URL")
    key: str = Field(..., min_length=1, description="Supabase anon key")

    @classmethod
    def from_env(cls) -> "SupabaseConfig":
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url is None or key is None:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )
        return cls(url=HttpUrl(url), key=key)


class OpenAIConfig(BaseModel):
    api_key: str = Field(..., min_length=1, description="OpenAI API key")

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        return cls(api_key=api_key)
