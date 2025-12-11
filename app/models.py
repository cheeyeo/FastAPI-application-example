import os
from typing import Self

from dotenv import load_dotenv
from pydantic import model_validator
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

load_dotenv()

postgresql_url = f"postgresql://{os.environ.get('RDS_USERNAME')}:{os.environ.get('RDS_PASSWORD')}@{os.environ.get('RDS_HOSTNAME')}:{os.environ.get('RDS_PORT')}/{os.environ.get('RDS_DB_NAME')}"


engine = create_engine(postgresql_url, connect_args={})


def get_session():
    with Session(engine) as session:
        yield session


class UserBase(SQLModel):
    username: str
    email: str | None = None
    full_name: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str
    disabled: bool = False
    randomitems: list["RandomItem"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    id: int
    disabled: bool


class RandomItemBase(SQLModel):
    min_value: int
    max_value: int


class RandomItem(RandomItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    num: int
    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="randomitems")


class RandomItemPublic(RandomItemBase):
    id: int
    num: int


class RandomItemCreate(RandomItemBase):
    @model_validator(mode="after")
    def check_values(self) -> Self:
        if self.min_value > self.max_value:
            raise ValueError("min value can't be greater than max value")
        return self


class RandomItemUpdate(RandomItemBase):
    @model_validator(mode="after")
    def check_values(self) -> Self:
        if self.min_value > self.max_value:
            raise ValueError("min value can't be greater than max value")
        return self
