from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    Form,
    File,
    UploadFile,
    Response,
)
from services.item import ItemService, get_item_service
from services.chat import ChatService, get_chat_service
from services.auth import AuthService, get_auth_service
from models.item import Item
from models.auth import UserCreate, UserLogin, AuthResponse

api_router = APIRouter(prefix="/api")


# Auth API Endpoints
@api_router.post("/auth/register", response_model=AuthResponse)
async def api_register(
    user_data: UserCreate, service: AuthService = Depends(get_auth_service)
):
    return await service.register(user_data)


@api_router.post("/auth/login", response_model=AuthResponse)
async def api_login(
    credentials: UserLogin, service: AuthService = Depends(get_auth_service)
):
    return await service.login(credentials)


@api_router.post("/auth/logout")
async def api_logout(service: AuthService = Depends(get_auth_service)):
    return await service.logout()


@api_router.post("/auth/refresh")
async def api_refresh_token(
    request: Request, service: AuthService = Depends(get_auth_service)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )
    auth_response = await service.refresh_token(refresh_token)
    response = Response(content="Token refreshed")
    response.set_cookie(
        key="access_token",
        value=auth_response.access_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response


# Core API Endpoints
@api_router.get("/items/", response_model=list[Item])
async def api_get_items(service: ItemService = Depends(get_item_service)):
    return await service.get_items()


@api_router.post("/items/", response_model=Item)
async def api_add_item(
    name: str = Form(...),
    quantity: int = Form(...),
    image: UploadFile | None = File(None),
    service: ItemService = Depends(get_item_service),
):
    image_content = await image.read() if image else None
    return await service.add_item(name, quantity, image_content)


@api_router.post("/chat/")
async def api_chat(
    script: str = Form(...), service: ChatService = Depends(get_chat_service)
):
    response = await service.get_chat_response(script)
    return {"response": response}
