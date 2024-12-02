from .resources.Articles.routine_factory import gen_routine

def parsing_function(soup):
    article_content = ""
    article_title = soup.find('div', {"data-component": "headline-block"}).text
    articles_content = soup.findAll('div', {"data-component": "text-block"})
    for article in articles_content:
        article_content += article.text
    authors = None #soup.find('div', {"data-testid": "byline-new-contributors"}).text
    return article_title, article_content, authors

bbc_routine = gen_routine(
    rss_url='https://feeds.bbci.co.uk/news/rss.xml',
    source='bbc',
    time_parse_string='%a, %d %b %Y %H:%M:%S GMT',
    parsing_function=parsing_function,
)
