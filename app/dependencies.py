import logging
import os
from typing import Annotated

import boto3
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.aws_cognito import AWSCognito
from app.models import User, get_session


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/users/login", scopes={"me": "Information about user", "randoms": "Random numbers API"})
SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_aws_cognito() -> AWSCognito:
    return AWSCognito(
        client=boto3.client("cognito-idp", region_name=os.getenv("AWS_REGION")), 
        region=os.getenv("AWS_REGION"),
        client_id=os.getenv("AWS_COGNITO_APP_CLIENT_ID"), 
        client_secret=os.getenv("AWS_COGNITO_APP_CLIENT_SECRET"),
        user_pool_id=os.getenv("AWS_USER_POOL_ID"))

CognitoDep = Annotated[AWSCognito, Depends(get_aws_cognito)]


class Token(BaseModel):
    access_token: str
    refresh_token: str
    id_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


async def get_current_user_cognito(security_scopes: SecurityScopes, cognito: CognitoDep, token: TokenDep, session: SessionDep):
    if security_scopes.scopes:
        authenticate_value = f"Bearer scope={security_scopes.scope_str}"
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = cognito.decode_token(token)
        username = payload.get("username")
        if username is None:
            raise credentials_exception

        scope: str = payload.get("scope", "")
        token_scopes = scope.split(" ")
        token_data = TokenData(scopes=token_scopes, username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    
    # logger.info(f"SECURITY SCOPES: {security_scopes.scopes}")
    # logger.info(f"TOKEN DATA SCOPES: {token_data.scopes}")

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value}
            )
    return user


async def get_current_active_user(current_user: Annotated[User, Security(get_current_user_cognito, scopes=["me"])]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentActiveUserRandoms = Annotated[User, Security(get_current_active_user, scopes=["randoms"])]
