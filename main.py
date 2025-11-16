import random
from typing import Annotated, Any
import logging
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlmodel import Session, select
from models import SessionDep, engine, RandomItem, RandomItemCreate, RandomItemPublic


app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/")
def home():
    return {"message": "Home page of randomizer"}


#### Testing DB
print("Initialize database...")
try:
    with Session(engine) as session:
        session.exec(select(1))
except Exception as e:
    logger.error(e)
    raise e


@app.post("/randoms/", response_model=RandomItemPublic)
def create_random(item: RandomItemCreate, session: SessionDep):
    # NOTE: We use update here to set the num attribute dynamically which is a field in RandomItem but not in RandomItemCreate to solve pydantic missing attribute error
    new_item = RandomItem.model_validate(item, update={"num": random.randint(item.min_value, item.max_value)})
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return new_item
