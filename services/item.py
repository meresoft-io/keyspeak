from fastapi import Depends
from models.config import SupabaseConfig
from models.item import Item
from supabase import Client, create_client
import os


def get_supabase_config() -> SupabaseConfig:
    return SupabaseConfig.from_env()


def get_supabase_client(
    config: SupabaseConfig = Depends(get_supabase_config),
) -> Client:
    return create_client(str(config.url), config.key)


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


async def get_item_service(
    supabase: Client = Depends(get_supabase_client),
    config: SupabaseConfig = Depends(get_supabase_config),
):
    return ItemService(supabase, config)
