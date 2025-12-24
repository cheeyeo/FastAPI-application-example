from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.dependencies import logger
from app.models import get_session
from app.core.application import create_app


#### Testing DB
logger.info("Initialize database...")
try:
    for session in get_session():
        session.exec(select(1))
except Exception as e:
    logger.error(e)
    raise e

App = create_app()
