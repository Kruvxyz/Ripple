from .resources.Articles.routine_factory import gen_routine

def parsing_function(soup):
    article_title = soup.find('div', class_='headline__wrapper').text
    article_content = soup.find('div', class_='article__content-container').text
    authors = soup.find('div', class_='headline__sub-container').text
    return article_title, article_content, authors

cnn_routine = gen_routine(
    rss_url='http://rss.cnn.com/rss/cnn_topstories.rss',
    source='cnn',
    time_parse_string='%a, %d %b %Y %H:%M:%S GMT',
    parsing_function=parsing_function,
)