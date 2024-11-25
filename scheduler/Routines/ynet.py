from RoutineManager import Routine, Task
from .resources.Articles import add_article, check_article_exists
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_all_items_task() -> bool:
    from bs4 import BeautifulSoup
    import urllib3

    YNET_RSS_URL = 'http://www.ynet.co.il/Integration/StoryRss2.xml'

    logger.info("ynet | task started")
    http = urllib3.PoolManager()
    response = http.request('GET', YNET_RSS_URL)
    logger.info("ynet | response received")
    response_xml = response.data.decode('utf-8', errors='replace')
    soup = BeautifulSoup(response_xml, 'html.parser')
    logger.info("ynet | soup created")
    all_items = soup.findAll('item')
    for item in all_items:
        logger.info("ynet | processing item")
        article_link = item.guid.text
        if check_article_exists(article_link, "ynet"):
            logger.info("ynet | article already exists")
            break
        
        logger.info("ynet | article does not exist")
        article = http.request('GET', article_link)
        article_soup = BeautifulSoup(article.data.decode('utf-8', errors='replace'), 'html.parser')
        logger.info("ynet | article soup created")
        try:
            article_title = article_soup.find('h1', class_='mainTitle').text#.encode("utf-8") 
            subTitle = article_soup.find('span', class_='subTitle').text#.encode("utf-8") 
            article_content = article_soup.find('div', class_='article-body').text#.encode("utf-8")
            authors = article_soup.find('div', class_='authors').text#.encode("utf-8") 
            logger.info("ynet | article content extracted")
            add_article(
                link=article_link,
                title=article_title, 
                content=article_content, 
                author=authors,
                publication_date=parse_date_and_assign(item.pubdate.text),
                source="ynet"
            )
        except:
            logger.error(f"ynet | error parsing article with link: {article_link}")
            continue
        logger.info(f"ynet | article added | {article_link}")
    logger.info("ynet | task completed")
    return True

def parse_date_and_assign(date_string) -> datetime:
    # Parse the date string into a datetime object
    logger.info("ynet | parsing date")
    publication_datetime = datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %z')
    return publication_datetime

ynet_task = Task(
    name="ynet_scraper",
    function=get_all_items_task
)

ynet_routine = Routine(
    name="ynet_scraper",
    description="This routine scrapes ynet news",
    task=ynet_task,
    interval=60,
    condition_function=lambda: True,
    retry_delay=60,
    retry_limit=5
)
