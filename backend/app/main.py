from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .routes import api1, api2, api3

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/img", StaticFiles(directory="img"), name="img")
app.mount('/', StaticFiles(directory='../../frontend/public', html=True), name='page')
app.include_router(api1.router)
app.include_router(api2.router)
app.include_router(api3.router)
