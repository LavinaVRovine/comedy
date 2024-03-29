from fastapi import FastAPI
from fastapi import APIRouter
from app.api.routers import contents, login, users, portals, sources, utils
from app.api.routers.user_specific import user_portals, user_sources
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
router = APIRouter(prefix="/contents", responses={404: {"description": "Not found"}})

origins = [
    "http://localhost",
    "http://localhost:8080",

]


app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")
app.mount("/static", StaticFiles(directory="media"), name='static')
# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
# TODO: if working remove
# app.add_middleware(
#     CORSMiddleware, allow_origins=origins, allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

api_router = APIRouter(prefix=settings.API_V1_STR,)
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contents.router, prefix="/contents", tags=["users"])
api_router.include_router(portals.router, prefix="/portals", tags=["portals"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(user_sources.router, prefix="/user-sources", tags=["user_sources"])
api_router.include_router(user_portals.router, prefix="/user-portals", tags=["user_portals"])
app.include_router(api_router)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
