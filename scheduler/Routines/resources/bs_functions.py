from bs4 import BeautifulSoup
import urllib3 
from .Articles import check_article_exists
import logging

logger = logging.getLogger(__name__)

def get_soup_from_link(link: str) -> BeautifulSoup:
    logger.info("Fetching URL: %s", link)
    http = urllib3.PoolManager()
    response = http.request('GET', link)
    logger.info("Response received for URL: %s", link)
    response_xml = response.data.decode('utf-8', errors='replace')
    soup = BeautifulSoup(response_xml, 'html.parser')
    logger.info("Soup created for URL: %s", link)
    return soup

def check_if_rss_was_updated(link: str, source: str) -> bool:
    logger.info("Checking if RSS was updated for URL: %s", link)
    soup = get_soup_from_link(link)
    logger.info("Fetched and parsed RSS feed for URL: %s", link)
    all_items = soup.findAll('item')
    if not all_items:
        logger.warning("No items found in RSS feed for URL: %s", link)
        return False
    article_link = all_items[0].guid.text
    logger.info("Latest article link found: %s", article_link)
    article_exists = check_article_exists(article_link, source)
    logger.info("Article exists: %s", article_exists)
    return not article_exists
