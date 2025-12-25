import json
from typing import Annotated

from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from app.core.aws_cognito import AWSCognito, UserSignin, UserSignup, UserVerify
from app.dependencies import (
    CurrentActiveUser,
    SessionDep,
    Token,
    TokenDep,
    get_aws_cognito,
    logger,
    CognitoDep,
)
from app.models import User, UserPublic
from app.services.cognito import AuthService

router = APIRouter()


@router.post("/users/signup", tags=["Authentication"])
async def create_users(
    user: UserSignup,
    session: SessionDep,
    cognito: CognitoDep,
):
    resp = AuthService.user_signup(user, cognito)
    content = json.loads(resp.body.decode('utf-8'))
    db_user = User(
        username=user.username,
        email=user.email,
        sub=content['sub']
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return resp


@router.get("/users/{sub_id}", response_model=UserPublic, tags=["Authentication"])
async def get_users_subid(sub_id: str, session: SessionDep):
    user = session.exec(
        select(User)
        .where(User.sub == sub_id)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users/login", tags=["Authentication"])
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    cognito: CognitoDep,
) -> Token:
    resp = AuthService.user_signin(
        UserSignin(username=form_data.username, password=form_data.password), cognito
    )
    content = json.loads(resp.body.decode("utf-8"))
    return Token(access_token=content.get("AccessToken"), token_type="bearer")


@router.post("/users/verify", tags=["Authentication"])
async def verify(data: UserVerify, cognito: CognitoDep):
    return AuthService.verify_account(data, cognito)


@router.post("/users/resend_confirmation_code", tags=["Authentication"])
async def resend_code(username: str, cognito: CognitoDep):
    return AuthService.resend_confirmation(username, cognito)


@router.get("/users/me", response_model=UserPublic, tags=["Authentication"])
async def read_users_me(current_user: CurrentActiveUser):
    return current_user


@router.post("/users/logout", tags=["Authentication"])
async def logout(
    token: TokenDep,
    cognito: CognitoDep,
):
    return AuthService.logout(token, cognito)
