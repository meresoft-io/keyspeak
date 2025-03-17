import uuid
from fastapi import (
    APIRouter,
    Request,
    Depends,
    Form,
    Response,
    status,
    HTTPException,
    FastAPI,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.auth import AuthService, get_auth_service, require_auth
from models.auth import UserCreate, UserLogin, User, UserUpdate
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

web_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@web_router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token = request.cookies.get("access_token")
    current_user = None
    if access_token:
        current_user = await auth_service.get_current_user(access_token)
    return templates.TemplateResponse(
        "pages/index.html", {"request": request, "current_user": current_user}
    )


@web_router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("pages/register.html", {"request": request})


@web_router.post("/register", response_class=HTMLResponse)
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
        response = RedirectResponse(url="/chat", status_code=status.HTTP_302_FOUND)
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


@web_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("pages/login.html", {"request": request})


@web_router.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    service: AuthService = Depends(get_auth_service),
):
    try:
        credentials = UserLogin(email=email, password=password)
        auth_response = await service.login(credentials)
        next_url = request.cookies.get("next", "/chat")
        response = Response(content="Logged in successfully")
        response.set_cookie(
            key="access_token",
            value=auth_response.access_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=auth_response.refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        response.delete_cookie(key="next")
        response.headers["HX-Redirect"] = next_url
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


@web_router.post("/logout", response_class=HTMLResponse)
async def logout_web_client(request: Request):
    response = Response(content="Logged out successfully")
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    response.headers["HX-Redirect"] = "/"
    return response


@web_router.get("/chat", response_class=HTMLResponse)
async def chat_dashboard(request: Request, current_user: User = Depends(require_auth)):
    active_session = request.cookies.get("chat_session_id")
    if active_session:
        return RedirectResponse(f"/chat/{active_session}", status_code=302)
    return templates.TemplateResponse(
        "pages/chat_dashboard.html", {"request": request, "current_user": current_user}
    )

@web_router.get("/chat/{session_id}", response_class=HTMLResponse)
async def chat(
    request: Request,
    session_id: str,
    current_user: User = Depends(require_auth)
):
    response = templates.TemplateResponse(
        "pages/chat.html", 
        {
            "request": request, 
            "current_user": current_user,
            "session_id": session_id
        }
    )
    response.set_cookie("chat_session_id", session_id, max_age=86400)  # 24 hour expiry
    return response


@web_router.get("/chat/create/wizard", response_class=HTMLResponse)
async def chat_create_wizard(
    request: Request, auth_response: User = Depends(require_auth)
):
    return templates.TemplateResponse(
        "components/chat_create_wizard.html", {"request": request}
    )

@web_router.post("/chat/create", response_class=HTMLResponse)
async def create_chat(
    request: Request,
    budget_min: int = Form(...),
    budget_max: int = Form(...),
    urgency_level: int = Form(...),
    current_user: User = Depends(require_auth),
):
    try:
        if budget_min > budget_max:
            return templates.TemplateResponse(
                "components/error_message.html",
                {"request": request, "message": "Minimum budget cannot be greater than maximum budget"},
            )

        session_id = str(uuid.uuid4())
        response = Response(content="Chat created successfully")
        response.headers["HX-Redirect"] = f"/chat/{session_id}"
        return response
    except Exception as e:
        return templates.TemplateResponse(
            "components/error_message.html",
            {"request": request, "message": str(e)},
        )


@web_router.get("/settings", response_class=HTMLResponse)
@web_router.get("/settings/account", response_class=HTMLResponse)
async def account_settings(
    request: Request,
    current_user: User = Depends(require_auth),
):
    return templates.TemplateResponse(
        "pages/account_settings.html",
        {
            "request": request,
            "current_user": current_user,
            "email": current_user.email,
        },
    )


async def async_template_response(template_name: str, context: dict) -> Response:
    return templates.TemplateResponse(template_name, context)


async def update_user_profile_handler(
    email: str | None,
    phone_number: str | None,
    request: Request,
    user: User,
    service: AuthService,
) -> Response:
    try:
        # Create update data
        user_data = UserUpdate(email=email, phone_number=phone_number)

        # Update user
        updated_user = await service.update_user(user, user_data)

        # Return success message
        return templates.TemplateResponse(
            "components/success_message.html",
            {
                "request": request,
                "message": "Account updated successfully",
            },
        )

    except HTTPException as e:
        return templates.TemplateResponse(
            "components/error_message.html",
            {"request": request, "message": e.detail},
            status_code=e.status_code,
        )
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        return templates.TemplateResponse(
            "components/error_message.html",
            {
                "request": request,
                "message": "An error occurred while updating your profile. Please try again.",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@web_router.post("/settings/update", response_class=HTMLResponse)
async def update_user_profile(
    request: Request,
    email: str | None = Form(None),
    phone_number: str | None = Form(None),
    current_user: User = Depends(require_auth),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await update_user_profile_handler(
        email, phone_number, request, current_user, auth_service
    )