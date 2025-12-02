import logging
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.models import get_session


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")

SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
