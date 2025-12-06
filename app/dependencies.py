import logging
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import Session

from app.models import get_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")

SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


def fake_decode_token(token):
    return User(
        username=f"{token}-fakecoded", email="john@example.com", full_name="John Doe"
    )


async def get_current_user(token: TokenDep):
    user = fake_decode_token(token)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
