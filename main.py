import random
from typing import Annotated, Any
import logging
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlmodel import Session, select
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self
from models import SessionDep, engine, RandomItem


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


class RandomItemRequest(BaseModel):
    min_value: int = Field(ge=1, le=100, description="Min random number")
    max_value: int = Field(ge=1, le=1000, description="Max random number", default=99)
    
    @model_validator(mode='after')
    def check_values(self) -> Self:
        if self.min_value > self.max_value:
            raise ValueError("min value can't be greater than max value")
        return self


@app.post("/randoms")
def create_random(item: RandomItemRequest, session: SessionDep) -> RandomItem:
    logger.info(f"ITEM: {item}")
    new_item = RandomItem()
    new_item.min_value = item.min_value
    new_item.max_value = item.max_value
    new_item.num = random.randint(item.min_value, item.max_value)
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return new_item
