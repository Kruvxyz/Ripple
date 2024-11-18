from Routine import Routine
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from shared.models import StockOfTheDay
from typing import Dict


def gen_stock_of_the_day_routine(session) -> Routine:
    def get_stock_of_the_day() -> bool:
        print("Start collecting data for the stock of the day")
        zacks_crawler = ZacksCrawler(session)
        return zacks_crawler.update_bull_of_the_day()

    return Routine(
        "Stock_Of_The_Day",
        "This routine collects the stock (bull) of the day from Zacks.",
        get_stock_of_the_day,
        20*60*60, # 20 hours
    )


def get_driver():
        op = webdriver.ChromeOptions()
        # op.add_argument('headless')
        # op.add_argument("--headless")  # Run headless to save resources
        op.add_argument('--ignore-ssl-errors=yes')
        op.add_argument('--ignore-certificate-errors')
        op.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues
        op.add_argument("--no-sandbox")  # Bypass sandboxing; useful for Docker
        op.add_argument("--disable-gpu")  # Disable GPU if it's not needed
        op.add_argument("--remote-debugging-port=9222")  # Avoid page crash issues
        op.add_argument("--disable-extensions")        # Disable Chrome extensions
        op.add_argument("--disable-software-rasterizer")  # Disable unneeded rasterizer
        op.add_argument('--ignore-ssl-errors=yes')
        # op.add_argument("--window-size=800,600")  # Prevent viewport issues
        # op.add_argument("--disable-application-cache")  # No need for cache
        # op.add_argument("--disk-cache-size=0")           # Disable disk caching
        driver = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            options=op
        )
        driver.implicitly_wait(1)
        return driver

class ZacksCrawler:
    def __init__(self, session) -> None:
        self.session = session

    def get_driver(self, implicitly_wait: int = 5) -> webdriver.Chrome:
        op = webdriver.ChromeOptions()
        # op.add_argument('headless')
        # op.add_argument("--headless")  # Run headless to save resources
        op.add_argument('--ignore-ssl-errors=yes')
        op.add_argument('--ignore-certificate-errors')
        # op.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues
        op.add_argument("--no-sandbox")  # Bypass sandboxing; useful for Docker
        op.add_argument("--disable-gpu")  # Disable GPU if it's not needed
        op.add_argument("--disable-extensions")        # Disable Chrome extensions
        op.add_argument("--disable-software-rasterizer")  # Disable unneeded rasterizer
        op.add_argument("--remote-debugging-port=9222")  # Avoid page crash issues
        # op.add_argument("--window-size=800,600")  # Prevent viewport issues
        # op.add_argument("--disable-application-cache")  # No need for cache
        # op.add_argument("--disk-cache-size=0")           # Disable disk caching
        driver = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            options=op
        )
        driver.implicitly_wait(implicitly_wait)
        return driver

    def get_bull_of_the_day(self) -> Dict[str, str]:
        """
        Get the bull of the day
        """
        print("------------------ZacksCrawler: Get bull of the day----------------")
        driver = self.get_driver()
        driver.get("https://www.zacks.com/")
        bull_element_symbol=driver.find_element(By.CSS_SELECTOR, "article.bull_of_the_day>span").get_attribute("title")
        symbol = bull_element_symbol[bull_element_symbol.find("(")+1: bull_element_symbol.find(")")]
        bull_element_link=driver.find_element(By.CSS_SELECTOR, "article.bull_of_the_day>span>a").get_attribute("href")
        driver.get(bull_element_link)
        reasoning = driver.find_element(By.CSS_SELECTOR, "article>.commentary_body").text
        driver.quit()
        return {
            "status": "success",
            "symbol": symbol,
            "reasoning": reasoning
        }

    def update_bull_of_the_day(self) -> None:
        """
        Update the bull of the day in the database
        """
        bull_of_the_day = self.get_bull_of_the_day()
        
        symbol = bull_of_the_day.get("symbol", None)
        reasoning = bull_of_the_day.get("reasoning", None)
        status = bull_of_the_day.get("status", None)
        if status != "success":
            print("Error in getting the bull of the day")
            return False
        
        try:
            self.session.add(StockOfTheDay(symbol, reasoning))
            self.session.commit()
            return True
        except:
            print(f"Error in adding price for {symbol}")
            self.session.rollback()
            return False
        

