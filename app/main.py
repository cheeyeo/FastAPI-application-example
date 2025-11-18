import random
from typing import Annotated, Any
import logging
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from app.models import SessionDep, engine, RandomItem, RandomItemCreate, RandomItemPublic, RandomItemUpdate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#### Testing DB
logger.info("Initialize database...")
try:
    with Session(engine) as session:
        session.exec(select(1))
except Exception as e:
    logger.error(e)
    raise e


# Customize swagger docs
tags_metadata = [
    {
        "name": "Random Playground",
        "description": "Generate random numbers"
    },
    {
        "name": "Random Items Management",
        "description": "Create, read, update and delete random numbers"
    }
]


app = FastAPI(
    title="Randomizer API",
    description="Generates random numbers between a min and max value",
    version="1.0.0",
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Random Playground"])
def home():
    return {"message": "Home page of randomizer"}


@app.get("/randoms/", response_model=list[RandomItemPublic], tags=["Random Playground"])
async def read_randoms(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    randoms = session.exec(select(RandomItem).offset(offset).limit(limit)).all()
    return randoms


@app.get("/randoms/{random_id}", response_model=RandomItemPublic, tags=["Random Playground"])
async def read_random(random_id: int, Session: SessionDep):
    random_db = session.get(RandomItem, random_id)
    if not random_db:
        raise HTTPException(status_code=404, detail="Random Item not found")
    return random_db


@app.post("/randoms/", response_model=RandomItemPublic, tags=["Random Items Management"])
async def create_random(item: RandomItemCreate, session: SessionDep):
    # NOTE: We use update here to set the num attribute dynamically which is a field in RandomItem but not in RandomItemCreate to solve pydantic missing attribute error
    new_item = RandomItem.model_validate(item, update={"num": random.randint(item.min_value, item.max_value)})
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    logger.info("Created new random...")
    return new_item


@app.patch("/randoms/{random_id}", response_model=RandomItemPublic, tags=["Random Items Management"])
async def update_random(random_id: int, random_item: RandomItemUpdate, session: SessionDep):
    random_db = session.get(RandomItem, random_id)
    if not random_db:
        raise HTTPException(status_code=404, detail="Random item not found")
    
    random_data = random_item.model_dump(exclude_unset=True)
    logger.info(f"DATA IN PATCH: {random_data}")
    random_db.sqlmodel_update(random_data, update={"num": random.randint(random_data.get("min_value"), random_data.get("max_value"))})
    session.add(random_db)
    session.commit()
    session.refresh(random_db)
    return random_db


@app.delete("/randoms/{random_id}", tags=["Random Items Management"])
async def delete_random(random_id: int, session: SessionDep):
    random_db = session.get(RandomItem, random_id)
    if not random_db:
        raise HTTPException(status_code=404, detail="Random item not found")
    session.delete(random_db)
    session.commit()
    return {"ok": True}