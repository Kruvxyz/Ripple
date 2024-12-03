from Routines.resources.Articles.routine_factory import gen_routine

def parsing_function(soup):
    article_title = soup.find('h1', class_='mainTitle').text
    article_content = soup.find('div', class_='article-body').text
    authors = soup.find('div', class_='authors').text
    return article_title, article_content, authors

ynet_routine = gen_routine(
    rss_url='http://www.ynet.co.il/Integration/StoryRss2.xml',
    source='ynet',
    parsing_function=parsing_function,
    time_parse_string='%a, %d %b %Y %H:%M:%S %z',
    identifier='hebrew'
)