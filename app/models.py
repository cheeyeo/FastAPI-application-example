import os
import random
from typing import Annotated
from typing_extensions import Self
from dotenv import load_dotenv
from fastapi import Depends
from pydantic import model_validator
from sqlmodel import Field, Session, SQLModel, create_engine, select


load_dotenv()

postgresql_url = f"postgresql://{os.environ.get('RDS_USERNAME')}:{os.environ.get('RDS_PASSWORD')}@{os.environ.get('RDS_HOSTNAME')}:{os.environ.get('RDS_PORT')}/{os.environ.get('RDS_DB_NAME')}"


engine = create_engine(postgresql_url, connect_args={})


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class RandomItemBase(SQLModel):
    min_value: int
    max_value: int


class RandomItem(RandomItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    num: int


class RandomItemPublic(RandomItemBase):
    id: int
    num: int


class RandomItemCreate(RandomItemBase):
    @model_validator(mode='after')
    def check_values(self) -> Self:
        if self.min_value > self.max_value:
            raise ValueError("min value can't be greater than max value")
        return self