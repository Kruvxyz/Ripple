from RoutineManager import Routine, Task
from ..bs_functions import check_if_rss_was_updated, get_soup_from_link
from . import add_article, check_article_exists
from datetime import datetime
import logging
from typing import Any, Tuple, Optional
from collections.abc import Callable

logger = logging.getLogger(__name__)

def gen_routine(
        rss_url: str, 
        source: str, 
        parsing_function: Callable[[Any], Tuple[str, str, str]],
        time_parse_string: str,
        identifier: Optional[str] = None,
        raise_parsing_error: bool = False # If True, the routine will stop if an error occurs while parsing an article
    ) -> Routine:
    
    decorated_source = source   
    if identifier:
        decorated_source = f"{source}_{identifier}"

    def get_all_items_task() -> bool:
        soup = get_soup_from_link(rss_url)
        logger.info(f"{decorated_source} | soup created")
        all_items = soup.findAll('item')
        for item in all_items:
            logger.info(f"{decorated_source} | processing item")
            article_link = item.guid.text
            if check_article_exists(article_link, source):
                logger.info(f"{decorated_source} | article already exists")
                break
            
            logger.info(f"{decorated_source} | article does not exist")
            article_soup = get_soup_from_link(article_link)
            logger.info(f"{decorated_source} | article soup created")
            try:
                article_title, article_content, authors = parsing_function(article_soup)
            except Exception as e:
                logger.error(f"{decorated_source} | error parsing article with link: {article_link} with error: {e}")
                article_title, article_content, authors = None, None, None
                if raise_parsing_error:
                    return False
            try:
                logger.info(f"{decorated_source} | article content extracted")
                add_article(
                    link=article_link,
                    title=article_title, 
                    content=article_content, 
                    author=authors,
                    publication_date=parse_date_and_assign(item.pubdate.text),
                    source=source
                )
            except Exception as e:
                logger.error(f"{decorated_source} | error pushing article to db , article link: {article_link} with error: {e}")
                return False
            logger.info(f"{decorated_source} | article added | {article_link}")
        logger.info(f"{decorated_source} | task completed")
        return True

    def parse_date_and_assign(date_string) -> datetime:
        # Parse the date string into a datetime object
        logger.info(f"{decorated_source} | parsing date")
        publication_datetime = datetime.strptime(date_string, time_parse_string)
        return publication_datetime

    task = Task(
        name=f"{decorated_source}_scraper",
        function=get_all_items_task
    )

    routine = Routine(
        name=f"{decorated_source}_scraper",
        description=f"This routine scrapes {decorated_source} news",
        task=task,
        interval=60,
        condition_function=lambda: check_if_rss_was_updated(rss_url, source),
        retry_delay=60,
        retry_limit=5
    )

    return routine
