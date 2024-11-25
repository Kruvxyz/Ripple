from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    id = Column("id", Integer, primary_key=True)
    title = Column("title", Text)
    author = Column("author", String(300))
    publication_date = Column("publication_date", DateTime)
    tldr = Column("tldr", Text)
    content = Column("content", Text)
    link = Column("link", String(300))
    source = Column("source", String(300))
    tags = Column("tags", String(300))
    created_at = Column("created_at", DateTime, default=datetime.now)
    
    def __init__(
            self, 
            title: str,
            author: str,
            publication_date: datetime,
            content: str,
            link: str,
            source: str,
            tags: Optional[str],
    ) -> None:
        self.title = title
        self.author = author
        self.publication_date = publication_date
        self.content = content
        self.link = link
        self.source = source
        self.tags = tags

    def __repr__(self) -> str:
        return f"<Article | {self.title} | {self.author} | {self.publication_date} | {self.source}>"
