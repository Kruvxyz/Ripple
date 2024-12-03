from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy import create_engine, exc, Engine
import logging
import os
import time

logger = logging.getLogger(__name__)


def generate_engine(retries: int = 5, delay: int = 2) -> Engine:
    MYSQL_USER = os.environ.get("MYSQL_ARTICLES_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_ARTICLES_PASSWORD")
    MYSQL_HOST = os.environ.get("MYSQL_ARTICLES_HOST")
    MYSQL_DATABASE = os.environ.get("MYSQL_ARTICLES_DATABASE")
    connection_string = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    logger.info(f"Connecting to database with connection string: {connection_string}")

    for i in range(retries):
        try:
            engine = create_engine(connection_string, echo=True)
            # Try connecting
            with engine.connect() as connection:
                logger.info("Successfully connected to the database!")
                return engine
        except exc.OperationalError:
            logger.error(f"Attempt {i+1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Could not connect to the database after several attempts.")

def generate_session(engine: Engine) -> Session:
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)  # Thread-safe session
    return Session()