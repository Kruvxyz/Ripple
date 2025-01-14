from .resources.Articles.routine_factory import gen_routine

def parsing_function(soup):
    article_title = soup.find('h1', class_='sdc-article-header__title').text
    article_content = soup.find('div', class_='sdc-article-body').text
    try:
        authors = soup.find('span', class_='sdc-article-author__name').text
    except Exception as e:
        authors = None
    return article_title, article_content, authors

website_feeds = [
    ("home", "https://feeds.skynews.com/feeds/rss/home.xml"), 
    ("UK", "https://feeds.skynews.com/feeds/rss/uk.xml"),
    ("world", "https://feeds.skynews.com/feeds/rss/world.xml"),
    ("US", "https://feeds.skynews.com/feeds/rss/us.xml"),
    ("business", "https://feeds.skynews.com/feeds/rss/business.xml"),
    ("politics", "https://feeds.skynews.com/feeds/rss/politics.xml"),
    ("technology", "https://feeds.skynews.com/feeds/rss/technology.xml"),
    ("entertainment", "https://feeds.skynews.com/feeds/rss/entertainment.xml"),
    ("strange", "https://feeds.skynews.com/feeds/rss/strange.xml"),
]

for identifier, rss_url in website_feeds:
    exec(f"""skynews_{identifier}_routine = gen_routine(
        rss_url='{rss_url}', 
        source='skynews', 
        identifier='{identifier}', 
        time_parse_string='%a, %d %b %Y %H:%M:%S +0000', 
        parsing_function=parsing_function
    )""")


# Generated routines:
#     skynews_home_routine
#     skynews_UK_routine
#     skynews_world_routine
#     skynews_US_routine
#     skynews_business_routine
#     skynews_politics_routine
#     skynews_technology_routine
#     skynews_entertainment_routine
#     skynews_strange_routine