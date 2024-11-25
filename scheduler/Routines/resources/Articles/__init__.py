from collections.abc import Callable
from datetime import datetime
import os
import logging
import time
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy import create_engine, exc, Engine
from typing import Optional, Tuple
from RoutineManager.Status import RoutineStatus, TaskInstanceStatus 
from .Article import Article

logger = logging.getLogger(__name__)


def connect_with_retry(db_url, retries=5, delay=2):
    for i in range(retries):
        try:
            engine = create_engine(db_url)
            # Try connecting
            with engine.connect() as connection:
                print("Successfully connected to the database!")
                return engine
        except exc.OperationalError:
            print(f"Attempt {i+1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Could not connect to the database after several attempts.")


def generate_engine(retries=5, delay=2):
    MYSQL_USER = os.environ.get("MYSQL_ARTICLES_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_ARTICLES_PASSWORD")
    MYSQL_HOST = os.environ.get("MYSQL_ARTICLES_HOST")
    MYSQL_DATABASE = os.environ.get("MYSQL_ARTICLES_DATABASE")
    connection_string = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    print(f"Connecting to database with connection string: {connection_string}")
    logger.info(f"Connecting to database with connection string: {connection_string}")

    for i in range(retries):
        try:
            engine = create_engine(connection_string, echo=True)
            # Try connecting
            with engine.connect() as connection:
                print("Successfully connected to the database!")
                return engine
        except exc.OperationalError:
            print(f"Attempt {i+1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Could not connect to the database after several attempts.")

def generate_session(engine: Engine):
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)  # Thread-safe session
    return Session()

def init_db() -> bool:
    engine = generate_engine()
    Article.metadata.create_all(engine)
    engine.dispose()
    return True

def add_article(
        link: str,
        title: str, 
        content: str, 
        author: str,
        publication_date: datetime,
        source: str
    ) -> None:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        article = Article(
            link=link,
            title=title, 
            content=content,
            author=author,
            publication_date=publication_date,
            source=source,
            tags = None
        )
        session.add(article)
        session.commit()
    except SQLAlchemyError as e:
        logger.error(e)
        session.rollback()
        raise e
    finally:
        session.close()
        engine.dispose()

    return None

def read_article(article_id: int) -> Article:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        article = session.query(Article).filter(Article.id == article_id).first()
        return article
    except SQLAlchemyError as e:
        logger.error(e)
        raise e
    finally:
        session.close()
        engine.dispose()

def check_article_exists(link: str, source: str) -> bool:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        article = session.query(Article).filter(Article.link == link, Article.source == source).first()
        return article is not None
    except SQLAlchemyError as e:
        logger.error(e)
        raise e
    finally:
        session.close()
        engine.dispose()