from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError
from .Article import Article
from ..DBConnection import generate_engine, generate_session

logger = logging.getLogger(__name__)



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