from typing import Annotated
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.dependencies import logger, fake_users_db, authenticate_user, UserInDB, CurrentActiveUser, Token, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, User
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


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub":  user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: CurrentActiveUser):
    return current_user
