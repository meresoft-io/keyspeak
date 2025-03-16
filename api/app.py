from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
import logging
import os
from routes.api_routes import api_router
from routes.web_routes import web_router
from api.middleware import TokenRefreshMiddleware
from services.auth import get_auth_service

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Get the absolute path to the static directory
static_dir = os.path.join(os.path.dirname(__file__), "../static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(api_router)
app.include_router(web_router)

app.add_middleware(TokenRefreshMiddleware)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
