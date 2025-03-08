from fastapi import (
    FastAPI,
    Request,
    Form,
    File,
    UploadFile,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
import logging
from services.item import (
    ItemService,
    get_item_service,
)
from services.chat import (
    ChatService,
    get_chat_service,
)
from services.auth import (
    AuthService,
    get_auth_service,
)
from models.item import Item
from models.auth import UserCreate, UserLogin, AuthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Auth API Endpoints
@app.post("/api/auth/register", response_model=AuthResponse)
async def api_register(
    user_data: UserCreate, service: AuthService = Depends(get_auth_service)
):
    return await service.register(user_data)


@app.post("/api/auth/login", response_model=AuthResponse)
async def api_login(
    credentials: UserLogin, service: AuthService = Depends(get_auth_service)
):
    return await service.login(credentials)


@app.post("/api/auth/logout")
async def api_logout(service: AuthService = Depends(get_auth_service)):
    return await service.logout()


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
async def index(
    request: Request,
    service: ItemService = Depends(get_item_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token = request.cookies.get("access_token")
    current_user = await auth_service.get_current_user(access_token)
    return templates.TemplateResponse(
        "index.html", {"request": request, "current_user": current_user}
    )


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    service: AuthService = Depends(get_auth_service),
):
    if password != confirm_password:
        logger.info("Registration failed: Passwords do not match")
        return templates.TemplateResponse(
            "components/error_message.html",
            {"request": request, "message": "Passwords do not match"},
        )

    try:
        user_data = UserCreate(email=email, password=password)
        auth_response = await service.register(user_data)
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="access_token", value=auth_response.access_token)
        response.set_cookie(key="refresh_token", value=auth_response.refresh_token)
        return response
    except HTTPException as e:
        logger.error(f"Registration failed: {e.detail}")
        return templates.TemplateResponse(
            "components/error_message.html",
            {"request": request, "message": e.detail},
        )
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        return templates.TemplateResponse(
            "components/error_message.html",
            {"request": request, "message": str(e)},
        )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    service: AuthService = Depends(get_auth_service),
):
    try:
        credentials = UserLogin(email=email, password=password)
        auth_response = await service.login(credentials)
        response = Response(content="Logged in successfully")
        response.set_cookie(key="access_token", value=auth_response.access_token)
        response.headers["HX-Redirect"] = "/"
        return response
    except HTTPException as e:
        return templates.TemplateResponse(
            "components/error_message.html",
            {"request": request, "message": e.detail},
        )
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return templates.TemplateResponse(
            "components/error_message.html",
            {"request": request, "message": str(e)},
        )


@app.post("/logout", response_class=HTMLResponse)
async def logout_web_client(request: Request):
    response = Response(content="Logged out successfully")
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    response.headers["HX-Redirect"] = "/"
    return response


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
