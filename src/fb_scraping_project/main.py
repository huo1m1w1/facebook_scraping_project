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
import json
import re
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .scraper import check_comments
from .scraper import create_url_with_keys
from .scraper import FacebookScraper
from .scraper import get_superlinks


async def main():
    """
    Entry point of the script.

    Initializes a FacebookScraper and performs a sample scraping operation.

    Args:
        None

    Returns:
        None
    """

    # Initialize FacebookScraper
    scraper = FacebookScraper()

    # Set the target URL
    URL = 'https://www.facebook.com/'

    # Log in to Facebook
    await scraper.login(URL)

    # Define search keys by inputting a list of key words

    user_input = input(
        "Please enter your key words in a list, for example: ['fintech', 'company', 'us']: ",
    )
    keys = eval(user_input)

    # Create URL with search keys
    base_url = 'https://www.facebook.com/search/posts/?q='
    url = await create_url_with_keys(base_url, keys)

    # load webpage with search keys to start scraping
    scraper.driver.get(url)

    nth_of_posts = 0
    parent_element_xpath = (
        "//*[@id[starts-with(., 'mount_0_')] and descendant::*[@role='feed']]/"
        'div/div/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div'
    )
    nth_of_posts = 0
    nth_of_records = 0
    post_list = []
    while True:
        # 1. if possible move bottom of the element to the bottom of window
        # screen get all the posts
        all_posts = scraper.find_elements_with_wait(
            'XPATH',
            parent_element_xpath,
        )
        # position the post at right place
        scraper.position_the_element(all_posts[nth_of_posts])

        # 2. Get information of current element get all info of current element
        post_detail = all_posts[nth_of_posts].text
        # Get all reaction part
        reaction_list = post_detail.split('All reactions:')[-1].split('\n')

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
            row_comments = scraper.find_elements_with_wait('XPATH', comment_element_xpath)

            try:
                time.sleep(3)
                all_c = WebDriverWait(scraper.driver, 20).until(
                    EC.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            f'//span[text()="{post_info.get("n_comments")}"]',
                        ),
                    ),
                )
                for ele in all_c:
                    try:
                        ele.click()
                        print('right button clicked')
                        break
                    except Exception as e:
                        print(f"An error occurred when clicking commentbutton"
                              f" contains, will try next: {e}")
                        continue

            except Exception as e:
                time.sleep(3)
                print(f"An error occurred when opening comment pop up contains: {e}")

            post_xpath = (
                '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/'
                'div/div/div/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div/'
                'div/div/div[8]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span'
            )

            try:
                post_elem = WebDriverWait(scraper.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, post_xpath)),
                )
                post_elem.click()
                time.sleep(5)
                print(get_superlinks(post_elem))
                post_list.append(get_superlinks(post_elem))
            except Exception as e:
                print('post element are not found: ', e)

            scraper.click_element_with_retry()
            scraper.click_all_comments_button()

            post_url = scraper.driver.current_url
            post_hash_match = re.search(r'/posts/([^/?]+)', post_url)
            if not post_hash_match:
                scraper.driver.back()
                time.sleep(5)
                close_buttons = WebDriverWait(scraper.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[aria-label="Close"]')),
                )
                # Click the button
                try:
                    if len(close_buttons) == 1:
                        close_buttons[0].click()
                    else:
                        for close_button in close_buttons.reverse():
                            close_button.click()
                except Exception:
                    close_xpath = (
                        '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div'
                        '/div[2]/div/div/div/div/div/div/div[1]/div/div[2]/div/svg'
                    )
                    WebDriverWait(scraper.driver, 10).until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                close_xpath,
                            ),
                        ),
                    ).click()

                nth_of_posts += 1
                continue
            post_info['SN'] = nth_of_records + 1
            post_info['key words'] = 'fintech company us'
            post_info['facebook url'] = post_url
            list_row_comments = []
            original_position = scraper.driver.execute_script('return window.scrollY;')

            comments_xpath = (
                '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/'
                'div/div/div/div/div/div/div/div/div/div/div/div/div[8]/div/div/div[4]/div/div'
                '/div[2]/div[3]/div| /html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]'
                '/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[8]/div/div'
                '/div[4]/div/div/div[2]/div[3]/div'
            )
            # all comments information will be save here
            comment_contains = []
            while True:
                try:
                    scraper.driver.execute_script(
                        'window.scrollTo(0, document.body.scrollHeight);',
                    )
                    time.sleep(5)

                    view_more_button = WebDriverWait(scraper.driver, 10).until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                '//span[contains(text(), " more comments")]',
                            ),
                        ),
                    )
                    view_more_button.click()
                    time.sleep(5)

                except Exception as e:
                    print('No more comments: ', e)
                    break
            scraper.driver.execute_script('window.scrollTo(0, 0);')
            while True:
                result = await scraper.extent_comment_contains()
                if result == 'No more extensions':
                    break
                time.sleep(5)
            row_comments = WebDriverWait(scraper.driver, 20).until(
                lambda driver: driver.find_elements(By.XPATH, comments_xpath),
            )
            await scraper.extract_and_save_comment(
                row_comments,
                comment_contains,
                list_row_comments,
            )
            time.sleep(5)

            post_info['comments'] = comment_contains
            dt = datetime.now()
            post_info['timestamp'] = datetime.timestamp(dt)

            time.sleep(3)

            scraper.driver.execute_script(f"window.scrollTo(0, {original_position});")

            scraper.driver.back()
            time.sleep(5)

            await scraper.close_popup()

            print('post_info:', post_info)

            try:
                with open('data_list.json') as file:
                    existing_data_list = json.load(file)
            except FileNotFoundError:
                existing_data_list = []

            # Append the new dictionary to the list
            existing_data_list.append(post_info)

            # Write the updated list of dictionaries back to the file
            with open('data_list.json', 'w') as file:
                json.dump(existing_data_list, file, indent=2)

            # filename = "data_list.json"
            # await save_to_json(post_info, filename)

            nth_of_records += 1

            if nth_of_records == 20:
                scraper.driver.quit()
                break
        nth_of_posts += 1


if __name__ == '__main__':
    asyncio.run(main())
