from supabase import create_client, Client
from openai import AsyncOpenAI
from fastapi import Depends
import os
from dotenv import load_dotenv
from models.item import Item
from models.config import SupabaseConfig, OpenAIConfig

load_dotenv(".env.local")


# Dependency factories
def get_supabase_config() -> SupabaseConfig:
    return SupabaseConfig.from_env()


def get_openai_config() -> OpenAIConfig:
    return OpenAIConfig.from_env()


def get_supabase_client(
    config: SupabaseConfig = Depends(get_supabase_config),
) -> Client:
    return create_client(str(config.url), config.key)


def get_openai_client(config: OpenAIConfig = Depends(get_openai_config)) -> AsyncOpenAI:
    return AsyncOpenAI(api_key=config.api_key)


# Service classes
class ItemService:
    def __init__(
        self,
        supabase: Client = Depends(get_supabase_client),
        config: SupabaseConfig = Depends(get_supabase_config),
    ):
        self.supabase = supabase
        self.config = config

    async def get_items(self) -> list[Item]:
        response = self.supabase.table("items").select("*").execute()
        return [Item(**item) for item in response.data]

    async def add_item(
        self, name: str, quantity: int, image_content: bytes | None = None
    ) -> Item:
        image_url = None
        if image_content:
            file_name = f"{name}_{os.urandom(8).hex()}.jpg"
            self.supabase.storage.from_("item-images").upload(file_name, image_content)
            image_url = (
                f"{self.config.url}/storage/v1/object/public/item-images/{file_name}"
            )
        item_data = {"name": name, "quantity": quantity, "image_url": image_url}
        response = self.supabase.table("items").insert(item_data).execute()
        return Item(**response.data[0])


class ChatService:
    def __init__(self, openai: AsyncOpenAI = Depends(get_openai_client)):
        self.openai = openai

    async def get_chat_response(self, script: str) -> str:
        response = await self.openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Act as a customer: {script}"}],
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content returned from OpenAI")
        return content


# Service factories
async def get_item_service(
    supabase: Client = Depends(get_supabase_client),
    config: SupabaseConfig = Depends(get_supabase_config),
):
    return ItemService(supabase, config)


async def get_chat_service(openai: AsyncOpenAI = Depends(get_openai_client)):
    return ChatService(openai)
