from openai import AsyncOpenAI
from fastapi import Depends
from models.config import OpenAIConfig


def get_openai_config() -> OpenAIConfig:
    return OpenAIConfig.from_env()


def get_openai_client(config: OpenAIConfig = Depends(get_openai_config)) -> AsyncOpenAI:
    return AsyncOpenAI(api_key=config.api_key)


class ChatService:
    def __init__(self, openai: AsyncOpenAI = Depends(get_openai_client)):
        self.openai = openai

    async def get_chat_response(self, script: str) -> str:
        response = await self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Act as a customer: {script}"}],
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content returned from OpenAI")
        return content


async def get_chat_service(openai: AsyncOpenAI = Depends(get_openai_client)):
    return ChatService(openai)
