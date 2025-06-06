import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config import app_config
from app.api.router import router

app = FastAPI(title="Geo Preprocessing Module", version="0.1.0")
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host=app_config.FASTAPI_HOST, port=app_config.FASTAPI_PORT, reload=False)
