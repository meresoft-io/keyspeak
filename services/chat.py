from openai import AsyncOpenAI
from fastapi import Depends
from models.config import OpenAIConfig, SupabaseConfig, AppConfig
from models.chat import ChatSession, ClientParameters, User, ChatSessionStatus
from supabase import create_client, Client


def get_openai_config() -> OpenAIConfig:
    return OpenAIConfig.from_env()


def get_openai_client(config: OpenAIConfig = Depends(get_openai_config)) -> AsyncOpenAI:
    return AsyncOpenAI(api_key=config.api_key)


def get_supabase_config() -> SupabaseConfig:
    return SupabaseConfig.from_env()


def get_app_config() -> AppConfig:
    return AppConfig.from_env()


def get_supabase_client(
    config: SupabaseConfig = Depends(get_supabase_config),
) -> Client:
    return create_client(str(config.url), config.key)


class ChatService:
    def __init__(
        self,
        openai: AsyncOpenAI = Depends(get_openai_client),
        app_config: AppConfig = Depends(get_app_config),
        supabase: Client = Depends(get_supabase_client),
    ):
        self.openai = openai
        self.supabase = supabase
        self.app_config = app_config

    async def get_chat_response(self, script: str) -> str:
        response = await self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Act as a customer: {script}"}],
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content returned from OpenAI")
        return content

    async def create_chat_session(
        self, user: User, min_budget: int, max_budget: int, urgency_level: str
    ) -> int:
        supabase_response = (
            self.supabase.table("client_parameters")
            .insert(
                {
                    "user_id": user.id,
                    "min_budget": min_budget,
                    "max_budget": max_budget,
                    "urgency_level": urgency_level,
                    "status": ChatSessionStatus.active,
                }
            )
            .execute()
        )

        chat_session_data = supabase_response.data[0]

        return chat_session_data.id


async def get_chat_service(openai: AsyncOpenAI = Depends(get_openai_client)):
    return ChatService(openai)
