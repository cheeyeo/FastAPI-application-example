from fastapi import APIRouter
from app.dependencies import CurrentUser, SessionDep, logger, get_password_hash
from app.models import UserCreate, User, UserPublic


router = APIRouter()


@router.post("/users/", response_model=UserPublic)
async def create_users(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user)
    db_user.password = get_password_hash(user.password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
