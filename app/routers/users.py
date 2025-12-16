import json
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.aws_cognito import AWSCognito, UserSignin, UserSignup, UserVerify
from app.dependencies import (
    CurrentActiveUser,
    SessionDep,
    Token,
    TokenDep,
    get_aws_cognito,
    get_password_hash,
    logger,
)
from app.models import User, UserPublic
from app.services.cognito import AuthService

router = APIRouter()


@router.post("/users/signup", tags=["Authentication"])
async def create_users(
    user: UserSignup,
    session: SessionDep,
    cognito: AWSCognito = Depends(get_aws_cognito),
):
    resp = AuthService.user_signup(user, cognito)
    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return resp


@router.post("/users/login", tags=["Authentication"])
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    cognito: AWSCognito = Depends(get_aws_cognito),
) -> Token:
    resp = AuthService.user_signin(
        UserSignin(username=form_data.username, password=form_data.password), cognito
    )
    content = json.loads(resp.body.decode("utf-8"))
    return Token(access_token=content.get("AccessToken"), token_type="bearer")


@router.post("/users/verify", tags=["Authentication"])
async def verify(data: UserVerify, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.verify_account(data, cognito)


@router.post("/users/resend_confirmation_code", tags=["Authentication"])
async def resend_code(username: str, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.resend_confirmation(username, cognito)


@router.get("/users/me", response_model=UserPublic, tags=["Authentication"])
async def read_users_me(current_user: CurrentActiveUser):
    return current_user


# TODO: Using the Authorize form the authentication token is set in the header via Swagger UI
# even if we call /users/logout, the auth token will still be in the headers; the only way to logout in the swagger UI is via the same authorize form > logout link
@router.get("/users/logout", tags=["Authentication"])
async def logout(
    token: TokenDep,
    current_user: CurrentActiveUser,
    cognito: AWSCognito = Depends(get_aws_cognito),
):
    return AuthService.logout(token, cognito)
