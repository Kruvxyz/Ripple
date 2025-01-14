from .resources.Articles.routine_factory import gen_routine

def parsing_function(soup):
    article_content = ""
    article_title = soup.find('div', {"data-component": "headline-block"}).text
    articles_content = soup.findAll('div', {"data-component": "text-block"})
    for article in articles_content:
        article_content += article.text
    authors = None #soup.find('div', {"data-testid": "byline-new-contributors"}).text
    return article_title, article_content, authors

website_feeds = [
    ("news", "https://feeds.bbci.co.uk/news/rss.xml"),
    ("world", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("UK", "https://feeds.bbci.co.uk/news/uk/rss.xml"),
    ("business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("politics", "https://feeds.bbci.co.uk/news/politics/rss.xml"),
    ("health", "https://feeds.bbci.co.uk/news/health/rss.xml"),
    ("education", "https://feeds.bbci.co.uk/news/education/rss.xml"),
    ("science_and_environment", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
    ("technology", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("entertainment_and_arts", "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"),
    ("africa", "https://feeds.bbci.co.uk/news/world/africa/rss.xml"),
    ("asia", "https://feeds.bbci.co.uk/news/world/asia/rss.xml"),
    ("europe", "https://feeds.bbci.co.uk/news/world/europe/rss.xml"),
    ("latin_america", "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml"),
    ("middle_east", "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml"),
    ("us_and_canada", "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"),
    ("england", "https://feeds.bbci.co.uk/news/england/rss.xml"),
    ("northern_ireland", "https://feeds.bbci.co.uk/news/northern_ireland/rss.xml"),
    ("scotland", "https://feeds.bbci.co.uk/news/scotland/rss.xml"),
    ("wales", "https://feeds.bbci.co.uk/news/wales/rss.xml"),
]

for identifier, rss_url in website_feeds:
    exec(f"""bbc_{identifier}_routine = gen_routine(
        rss_url='{rss_url}', 
        source='bbc', 
        identifier='{identifier}', 
        time_parse_string='%a, %d %b %Y %H:%M:%S GMT',
        parsing_function=parsing_function
    )""")


# Generated routines:
#     bbc_news_routine
#     bbc_world_routine
#     bbc_UK_routine
#     bbc_business_routine
#     bbc_politics_routine
#     bbc_health_routine
#     bbc_education_routine
#     bbc_science_and_environment_routine
#     bbc_technology_routine
#     bbc_entertainment_and_arts_routine
#     bbc_africa_routine
#     bbc_asia_routine
#     bbc_europe_routine
#     bbc_latin_america_routine
#     bbc_middle_east_routine
#     bbc_us_and_canada_routine
#     bbc_england_routine
#     bbc_northern_ireland_routine
#     bbc_scotland_routine
#     bbc_wales_routine