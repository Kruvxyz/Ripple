from .resources.Articles.routine_factory import gen_routine

def parsing_function(soup):
    article_title = soup.find('h1', class_='title').text
    article_content = soup.find('section', class_='article-content').text
    authors = soup.find('div', class_='writers-names').text
    return article_title, article_content, authors

walla_routine = gen_routine(
    rss_url='https://rss.walla.co.il/feed/1?type=main',
    source='walla',
    time_parse_string='%a, %d %b %Y %H:%M:%S GMT',
    parsing_function=parsing_function,
)