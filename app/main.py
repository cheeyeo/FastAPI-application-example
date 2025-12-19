from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.dependencies import logger
from app.models import engine
from app.routers import randoms, users

#### Testing DB
logger.info("Initialize database...")
try:
    with Session(engine) as session:
        session.exec(select(1))
except Exception as e:
    logger.error(e)
    raise e


# Customize swagger docs
tags_metadata = [
    {"name": "Random Playground", "description": "Generate random numbers"},
    {
        "name": "Random Items Management",
        "description": "Create, read, update and delete random numbers",
    },
    {"name": "Authentication", "description": "OAUTH2 authentication flow via Cognito"},
]


app = FastAPI(
    title="Randomizer API",
    description="Generates random numbers between a min and max value",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(randoms.router)
app.include_router(users.router)


@app.get("/", tags=["Random Playground"])
def home():
    return {"message": "Home page of randomizer"}
