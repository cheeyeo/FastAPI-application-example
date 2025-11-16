import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select


postgresql_url = f"postgresql://{os.environ.get('RDS_USERNAME')}:{os.environ.get('RDS_PASSWORD')}@{os.environ.get('RDS_HOSTNAME')}:{os.environ.get('RDS_PORT')}/{os.environ.get('RDS_DB_NAME')}"

engine = create_engine(postgresql_url, connect_args={})


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class RandomItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    min_value: int
    max_value: int
    num: int
