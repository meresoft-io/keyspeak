from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    quantity: int
    image_url: str | None = None
