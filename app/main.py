from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.dependencies import logger
from app.models import engine
from app.core.application import create_app


if __name__ == "__main__":
    #### Testing DB
    logger.info("Initialize database...")
    try:
        with Session(engine) as session:
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e

    app = create_app()
