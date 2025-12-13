from datetime import timedelta
from typing import Annotated
import json

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    CurrentActiveUser,
    SessionDep,
    Token,
    TokenDep,
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_aws_cognito,
    logger
)
from app.models import User, UserCreate, UserPublic
from app.core.aws_cognito import AWSCognito, UserSignup, UserSignin, UserVerify
from app.services.cognito import AuthService


router = APIRouter()


@router.post("/users/signup", tags=["Authentication"])
async def create_users(user: UserSignup, session: SessionDep, cognito: AWSCognito = Depends(get_aws_cognito)):
    resp = AuthService.user_signup(user, cognito)
    db_user = User(username=user.username, email=user.email, password=get_password_hash(user.password))
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return resp


@router.get("/users/me", response_model=UserPublic, tags=["Authentication"])
async def read_users_me(current_user: CurrentActiveUser):
    return current_user


@router.post("/users/login", tags=["Authentication"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], cognito: AWSCognito = Depends(get_aws_cognito)) -> Token:
    resp = AuthService.user_signin(UserSignin(username=form_data.username, password=form_data.password), cognito)
    logger.info(resp)
    content = json.loads(resp.body.decode("utf-8"))
    return Token(access_token=content.get("AccessToken"), token_type="bearer")


# TODO: The auth token is set inside the header via CurrentActiveUser but not accessible
# hence we get it through the request header but need better way to handle this...
@router.post("/users/logout", tags=["Authentication"])
async def logout(response: Response, token: TokenDep, current_user: CurrentActiveUser, cognito: AWSCognito = Depends(get_aws_cognito)):
    response.delete_cookie("bearer")
    return AuthService.logout(token, cognito)


@router.post("/users/verify", tags=["Authentication"])
async def verify(data: UserVerify, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.verify_account(data, cognito)


@router.post("/users/resend_confirmation_code", tags=["Authentication"])
async def resend_code(username: str, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.resend_confirmation(username, cognito)
