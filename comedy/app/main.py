from fastapi import Depends, FastAPI
from fastapi import APIRouter
from routers import contents
from fastapi.middleware.cors import CORSMiddleware
router = APIRouter(prefix="/contents", responses={404: {"description": "Not found"}})

origins = [
    "http://localhost",
    "http://localhost:8080",

]


app = FastAPI()
@app.on_event("startup")
async def startup_event():
    print("this happened")
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api/v1",)
api_router.include_router(contents.router,)


app.include_router(api_router)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)