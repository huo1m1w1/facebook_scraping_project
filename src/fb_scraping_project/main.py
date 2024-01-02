"""
Main Script for Facebook Scraping Project

This script initializes a FacebookScraper and performs a sample scraping operation.

Usage:
    Run this script to execute a basic Facebook scraping operation.

Attributes:
    None

Methods:
    main(): Entry point of the script. Initializes the scraper and performs scraping.

"""
from __future__ import annotations

import asyncio
import re
import time

from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .scraper import check_comments
from .scraper import create_url_with_keys
from .scraper import FacebookScraper
# from selenium.common.exceptions import TimeoutException
# from selenium.common.exceptions import WebDriverException
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.remote.webdriver import WebDriver


def main():
    """
    Entry point of the script.

    Initializes a FacebookScraper and performs a sample scraping operation.

    Args:
        None

    Returns:
        None
    """

    # Initialize FacebookScraper
    scraper_driver = FacebookScraper()

    # Set the target URL
    URL = 'https://www.facebook.com/'

    # Log in to Facebook
    asyncio.run(scraper_driver.login(URL))

    # Define search keys
    keys = ['fintech', 'company', 'us']

    # Create URL with search keys
    base_url = 'https://www.facebook.com/search/posts/?q='
    url = asyncio.run(create_url_with_keys(base_url, keys))

    # Perform scraping operation
    scraper_driver.driver.get(url)

    nth_of_posts = 0
    parent_element_xpath = (
        "//*[@id[starts-with(., 'mount_0_')] and descendant::*[@role='feed']]/"
        'div/div/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div'
    )
    nth_of_posts = 0
    nth_of_records = 0
    while True:
        # 1. if possible move bottom of the element to the bottom of window
        # screen get all the posts
        all_posts = scraper_driver.find_elements_with_wait(
            'XPATH', parent_element_xpath,
        )
        # position the post at right place
        scraper_driver.position_the_element(all_posts[nth_of_posts])

        # 2. Get information of current element get all info of current element
        post_detail = all_posts[nth_of_posts].text
        # Get all reaction part
        reaction_list = post_detail.split('All reactions:')[-1].split('\n')
        # Get post detail part
        # list_details_of_post = post_detail.split(
        #     'All reactions:',
        # )[
        #     0
        # ].split('\n')

        # 3. if there are comments, collect post information and move the
        # bottom of element to the the bottom of the browser window
        # click comments button
        # initialise data of dictionary of post information
        post_info = {
            'post_id': '',
            'user_id': '',
            'group_id': '',
            'company_name': '',
            'post_hash': '',
            'n_comments': 0,
            'post_name': '',
            'Auther': '',
            'timestamp': '',
            'comments': [],
        }

        if check_comments(reaction_list)[0]:
            # assign `n_comment` to post_info
            post_info['n_comments'] = check_comments(reaction_list)[1]
            print("post_info.get('n_comments')", post_info.get('n_comments'))
            # find and click comment button.
            comment_element_xpath = f'//span[text()="{post_info.get("n_comments")}"]'
            row_comments = scraper_driver.find_element_with_wait('XPATH', comment_element_xpath)
            if row_comments:
                for row_comment in row_comments:
                    try:
                        print('right button found and clicked')
                        row_comment.click()
                    except ElementNotInteractableException as e:
                        print(f"An error occurred when clicking comments button contains: {e}")
                        # Handle ElementNotInteractableException specific actions, if needed
                        continue
                    except StaleElementReferenceException as e:
                        print(f"An error occurred due to a stale element reference: {e}")
                        # Handle StaleElementReferenceException specific actions, if needed
                        continue
                    except Exception as e:
                        print(
                            f"An unexpected error occurred when clicking comments button contains,"
                            f"will try next:: {e}",
                        )
                        # Handle other exceptions if needed
                        continue
                    except Exception:
                        print('An error occurred ')
                        continue
            post_xpath = (
                '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/'
                'div/div/div/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div/'
                'div/div/div[8]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span'
            )
            post_element = scraper_driver.find_element_with_wait('XPATH', post_xpath)
            if post_element:
                post_element.click()

            post_url = scraper_driver.driver.current_url
            post_hash_match = re.search(r'/posts/([^/?]+)', post_url)
            if not post_hash_match:
                scraper_driver.driver.back()
                time.sleep(2)
                close_button = WebDriverWait(scraper_driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Close"]')),
                )

                # Click the button
                close_button.click()
                nth_of_posts += 1
                continue
            post_info['SN'] = nth_of_records + 1
            post_info['key words'] = 'fintech company us'
            post_info['facebook url'] = post_url
            # author_elem_xpath = (
            #     '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div[1]/div'
            #     '/div/div/div/div/div/div/div/div/div/div/div/div/div[8]/div/div'
            #     '/div[2]/div/div[2]/div/div[1]/span/h2/span[1]/a/strong/span'
            # )
            # auther_element = scraper_driver.find_element_with_wait('XPATH', author_elem_xpath)

        pass


if __name__ == '__main__':
    main()
