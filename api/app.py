from fastapi import FastAPI, Request, Form, File, UploadFile, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from services.item import (
    ItemService,
    get_item_service,
)
from services.chat import (
    ChatService,
    get_chat_service,
)
from models.item import Item

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Core API Endpoints
@app.get("/api/items/", response_model=list[Item])
async def api_get_items(service: ItemService = Depends(get_item_service)):
    return await service.get_items()


@app.post("/api/items/", response_model=Item)
async def api_add_item(
    name: str = Form(...),
    quantity: int = Form(...),
    image: UploadFile | None = File(None),
    service: ItemService = Depends(get_item_service),
):
    image_content = await image.read() if image else None
    return await service.add_item(name, quantity, image_content)


@app.post("/api/chat/")
async def api_chat(
    script: str = Form(...), service: ChatService = Depends(get_chat_service)
):
    response = await service.get_chat_response(script)
    return {"response": response}


# HTMX Endpoints
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, service: ItemService = Depends(get_item_service)):
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html", {"request": request}
    )


@app.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    # This is a placeholder - actual authentication will be implemented later
    # Just redirect back to home page for now
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request}
    )


@app.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    # This is a placeholder - actual authentication will be implemented later
    # Just redirect back to home page for now
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )


@app.post("/htmx/add/", response_class=HTMLResponse)
async def htmx_add_item(
    request: Request,
    name: str = Form(...),
    quantity: int = Form(...),
    image: UploadFile | None = File(None),
    service: ItemService = Depends(get_item_service),
):
    image_content = await image.read() if image else None
    item = await service.add_item(name, quantity, image_content)
    return templates.TemplateResponse("_item.html", {"request": request, "item": item})


@app.post("/htmx/chat/", response_class=HTMLResponse)
async def htmx_chat(
    request: Request,
    script: str = Form(...),
    service: ChatService = Depends(get_chat_service),
):
    response = await service.get_chat_response(script)
    return templates.TemplateResponse(
        "_chat.html", {"request": request, "response": response}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
