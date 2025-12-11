import random
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from app.dependencies import CurrentActiveUser, SessionDep, logger
from app.models import RandomItem, RandomItemCreate, RandomItemPublic, RandomItemUpdate

router = APIRouter()


@router.get(
    "/randoms/", response_model=list[RandomItemPublic], tags=["Random Items Management"]
)
async def read_randoms(
    session: SessionDep,
    user: CurrentActiveUser,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    randoms = session.exec(
        select(RandomItem)
        .where(RandomItem.user_id == user.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return randoms


@router.get(
    "/randoms/{random_id}",
    response_model=RandomItemPublic,
    tags=["Random Items Management"],
)
async def read_random(random_id: int, session: SessionDep, user: CurrentActiveUser):
    # random_db = session.get(RandomItem, random_id)
    random_db = session.exec(
        select(RandomItem)
        .where(RandomItem.user_id == user.id)
        .where(RandomItem.id == random_id)
    ).first()
    if not random_db:
        raise HTTPException(status_code=404, detail="Random Item not found")
    return random_db


@router.post(
    "/randoms/", response_model=RandomItemPublic, tags=["Random Items Management"]
)
async def create_random(
    item: RandomItemCreate, session: SessionDep, user: CurrentActiveUser
):
    # NOTE: We use update here to set the num attribute dynamically which is a field in RandomItem but not in RandomItemCreate to solve pydantic missing attribute error
    new_item = RandomItem.model_validate(
        item, update={"num": random.randint(item.min_value, item.max_value)}
    )
    new_item.user = user
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    logger.info("Created new random...")
    return new_item


@router.patch(
    "/randoms/{random_id}",
    response_model=RandomItemPublic,
    tags=["Random Items Management"],
)
async def update_random(
    random_id: int,
    random_item: RandomItemUpdate,
    session: SessionDep,
    user: CurrentActiveUser,
):
    random_db = session.exec(
        select(RandomItem)
        .where(RandomItem.user_id == user.id)
        .where(RandomItem.id == random_id)
    ).first()
    if not random_db:
        raise HTTPException(status_code=404, detail="Random item not found")

    random_data = random_item.model_dump(exclude_unset=True)
    logger.info(f"DATA IN PATCH: {random_data}")
    random_db.sqlmodel_update(
        random_data,
        update={
            "num": random.randint(
                random_data.get("min_value"), random_data.get("max_value")
            )
        },
    )
    session.add(random_db)
    session.commit()
    session.refresh(random_db)
    return random_db


@router.delete("/randoms/{random_id}", tags=["Random Items Management"])
async def delete_random(random_id: int, session: SessionDep, user: CurrentActiveUser):
    # random_db = session.get(RandomItem, random_id)
    random_db = session.exec(
        select(RandomItem)
        .where(RandomItem.user_id == user.id)
        .where(RandomItem.id == random_id)
    ).first()
    if not random_db:
        raise HTTPException(status_code=404, detail="Random item not found")
    session.delete(random_db)
    session.commit()
    return {"ok": True}
