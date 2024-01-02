"""
This module provides a Python class for scraping data from Facebook based
on search keywords.

The FacebookScraper class allows you to perform the following tasks:

* Login to Facebook using credentials stored in a separate YAML file.
* Search for posts based on user-provided keywords.
* Extract information from Facebook posts, including comments, links, and IDs.

Please note that using this script to scrape data against Facebook's
terms of service is not recommended. Always be responsible and respectful
of user privacy when collecting data.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from pathlib import Path

import yaml
from aiofiles import open as aio_open
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
# from typing import Union
# import csv
# from typing import Dict, List, Optional, Tuple
# from selenium.common.exceptions import ElementNotInteractableException
# from selenium.common.exceptions import StaleElementReferenceException
# from selenium.common.exceptions import WebDriverException
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.keys import Keys


def check_comments(list_text: list[str]) -> tuple[bool, str]:
    """
    Checks if a list of text elements contains a string indicating the number
    of comments on a Facebook post.

    Args:
        list_text (List[str]): A list of strings extracted from the post
          metadata.

    Returns:
        Tuple[bool, str]: A tuple where the first element is a boolean (True if
        the number of comments is found, False otherwise), and the second
          element
        is the retrieved number of comments.
    """
    for text in list_text:
        if text.endswith((' comments', ' comment')):
            return True, text
    return False, ''


def get_superlinks(element: WebElement) -> list[str]:
    """
    Extracts all hyperlinks found within a specific HTML element on the
      Facebook post.

    Args:
        element (selenium.webdriver.remote.webelement.WebElement): The HTML
          element to be parsed for links.

    Returns:
        list: A list of URLs extracted from the HTML element.
    """
    links = []
    ele_html = element.get_attribute('outerHTML')
    soup = BeautifulSoup(ele_html, 'html.parser')
    a_links = soup.find_all('a')
    for a_link in a_links:
        link = a_link.get('href')
        links.append(link)
    return links


async def check_post_url(pattern: str, post_url: str) -> re.Match | None:
    """
    Checks if a given post URL matches a specified pattern using regular
      expressions.

    Args:
        pattern (str): The regular expression pattern to match against.
        post_url (str): The post URL to be checked.

    Returns:
        Optional[re.Match]: A match object if the pattern is found in the post
          URL,
        None otherwise.
    """
    if not isinstance(pattern, str):
        raise TypeError('pattern must be a string')

    if not isinstance(post_url, str):
        raise TypeError('post_url must be a string')

    post_hash_match = re.search(pattern, post_url)
    return post_hash_match


async def create_url_with_keys(base_url: str, key_words: list[str]) -> str:
    """
    Creates a URL based on the given base URL and search keys.

    Args:
        base_url (str): The base URL to which search keys will be appended.
        keys (List[str]): A list of search keys.

    Returns:
        str: The generated URL.
    """
    if not isinstance(base_url, str):
        raise TypeError('base_url must be a string')

    if not isinstance(key_words, list):
        raise TypeError('keys must be a list')

    for word in key_words:
        if not isinstance(word, str):
            raise TypeError('Each element in keys must be a string')

        base_url += word + '%20'

    current_url = base_url[:-3]
    return current_url


async def save_to_json(
    jsonfile: str,
    input_dict: dict[str, str | int | float],
) -> None:
    """
    Converts a dictionary to a JSON file asynchronously.

    Parameters:
    - jsonfile (str): The name of the JSON file.
    - input_dict (dict): The dictionary to be converted and added to the JSON
      file.

    Returns:
    None
    """
    try:
        # Read existing data from the JSON file
        async with aio_open(jsonfile, 'r') as file:
            existing_data_list = json.loads(await file.read())
    except FileNotFoundError:
        # If the file doesn't exist, create an empty list
        existing_data_list = []

    # Validate input_dict type
    if not isinstance(input_dict, dict):
        raise TypeError('Input dictionary must be of type dict')

    # Append the new dictionary to the list
    existing_data_list.append(input_dict)

    # Write the updated list of dictionaries back to the file
    async with aio_open(jsonfile, 'w') as file:
        await file.write(json.dumps(existing_data_list, indent=2))


class FacebookScraper:
    """
    A class for scraping data from Facebook based on search keywords.

    Attributes:
        keywords (str): The keywords to search for on Facebook.
        root_dir (Path): The root directory of the project.
        driver (webdriver.Chrome): The Chrome WebDriver instance used for
            interacting with Facebook.
        my_user_name (str): The username for your Facebook account.
        my_password (str): The password for your Facebook account.

    Methods:
        login(url: str) -> None:
            Logs in to Facebook using the stored credentials.

        _load_credentials() -> Dict[str, str]:
            Loads credentials from the 'secret.yaml' file.

        _navigate_to_facebook(url: str) -> None:
            Navigates to the Facebook page.

        _login_with_credentials() -> None:
            Logs in with the stored credentials.

        _wait_for_successful_login() -> None:
            Waits for the successful login confirmation.

        position_the_element(element: WebElement) -> None:
            Scrolls the page to position the given element within the viewport.

    """

    def __init__(self) -> None:
        """
        Initializes the FacebookScraper class.

        """
        self.root_dir = Path(
            os.getcwd(),
        )

        # self.my_user_name = None
        # self.my_password = None
        self.options = Options()
        # self.options.headless = False
        self.options.add_experimental_option('detach', True)
        self.options.add_argument('--disable-infobars')
        self.options.add_argument('start-maximized')
        self.options.add_argument('--disable-extensions')
        self.options.add_experimental_option(
            'prefs',
            {
                'profile.default_content_setting_values.notifications': 1,
            },
        )
        self.driver = webdriver.Chrome(
            service=ChromeService(
                ChromeDriverManager().install(),
            ),
            options=self.options,
        )

    async def login(self, url) -> None:
        """
        Logs in to Facebook using the username and password stored in a YAML
        file.

        Args:
            url (str): The URL of the Facebook login page.

        Raises:
            FileNotFoundError: If the YAML file containing credentials is not
            found.
            yaml.YAMLError: If there is an error parsing the YAML file.

        """

        try:
            # Load credentials from secure source
            await self._load_credentials()
            # self.my_user_name = credentials['username']
            # self.my_password = credentials['password']
        except KeyError as e:
            print(f"Missing credential: {e}")
            return

        # Navigate to Facebook and handle cookies
        await self._navigate_to_facebook(url)

        # Login with user credentials
        await self._login_with_credentials()

        # Wait for successful login
        await self._wait_for_successful_login()

    async def _load_credentials(self):
        """
        Loads credentials from the 'secret.yaml' file.

        Returns:
            Dict[str, str]: A dictionary containing username and password.

        Raises:
            FileNotFoundError: If the YAML file is not found.
            yaml.YAMLError: If there is an error parsing the YAML file.

        """
        try:
            # Load credentials from YAML file
            path = self.root_dir / 'secret.yaml'
            with open(path) as f:
                secret = yaml.load(f, Loader=yaml.FullLoader)
                self.my_user_name = secret['credentials']['username']
                self.my_password = secret['credentials']['password']
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"Error loading YAML confidential file: {e}")
            # return

        # Replace this with your actual implementation
        # return {'username': self.my_user_name, 'password': self.my_password}

    async def _navigate_to_facebook(self, url) -> None:
        """
        Navigates to the Facebook page.

        Args:
            url (str): The URL of the Facebook page.

        """
        self.driver.get(url)
        WebDriverWait(self.driver, 2)
        try:
            cookies_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[text()="Allow all cookies"]'),
                ),
            )
            cookies_button.click()
        except TimeoutException:
            print(
                'Allow all cookies button not found within the specified time.',
            )

    async def _login_with_credentials(self) -> None:
        """
        Logs in to Facebook with stored credentials.

        """
        try:
            email_field = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, 'email')),
            )
            password_field = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, 'pass')),
            )
            email_field.send_keys(self.my_user_name)
            password_field.send_keys(self.my_password)
            login_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.NAME, 'login')),
            )
            login_button.click()
        except NoSuchElementException as e:
            print(f"Login element not found: {e}")
        except Exception as e:
            print(f"Login error: {e}")

    async def _wait_for_successful_login(self) -> None:
        """
        Waits for the successful login confirmation.

        """
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'facebook')),
            )
        except TimeoutException:
            print(
                'Login confirmation timeout! Unable to verify successful login.',
            )

    def position_the_element(
        self,
        element: WebElement,
    ) -> None:
        """
        Scrolls the page to position the given element within the viewport.

        Args:
            element (webdriver.remote.webelement.WebElement): The element to
              be positioned.

        """
        window_height = self.driver.execute_script(
            'return window.innerHeight;',
        )

        # Get the bottom position of the element relative to the viewport
        element_bottom = self.driver.execute_script(
            'return arguments[0].getBoundingClientRect().bottom;',
            element,
        )

        # Calculate the scroll distance needed to align the bottom of the
        # element with the bottom of the screen
        scroll_distance = element_bottom - window_height

        if scroll_distance > 0:
            # Scroll to the calculated distance
            self.driver.execute_script(
                'window.scrollBy(0, arguments[0]);',
                scroll_distance,
            )
            time.sleep(3)

    def find_elements_with_wait(
        self,
        type_of_path: str,
        element_xpath: str,
    ) -> WebElement | None:
        """
        Finds all elements located by the given XPath with WebDriverWait.

        Args:
            type_of_path (str): The type of path, e.g., 'ID', 'XPATH', etc.
            element_xpath (str): The XPath of the elements.

        Returns:
            List[webdriver.remote.webelement.WebElement]: A list of matching elements.

        """
        try:
            elements = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((getattr(By, type_of_path), element_xpath)),
            )
            return elements

        except TimeoutException:
            print(f"Timeout waiting for elements with XPath: {element_xpath}")
            return None

    def find_element_with_wait(
        self,
        type_of_path: str,
        element_xpath: str,
    ) -> WebElement | None:
        """
        Finds the element located by the given XPath with WebDriverWait.

        Args:
            type_of_path (str): The type of path, e.g., 'ID', 'XPATH', etc.
            element_xpath (str): The XPath of the element.

        Returns:
            Union[webdriver.remote.webelement.WebElement, None]: The matching element
            or None if not found within the specified time.

        """
        try:
            element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((getattr(By, type_of_path), element_xpath)),
            )
            return element

        except TimeoutException:
            print(f"Timeout waiting for element with XPath: {element_xpath}")
            return None

    def click_element_with_retry(self, driver: WebDriver, xpath: str) -> None:
        """
        Clicks an element with XPath, retrying in case of an exception.

        Args:
            driver (WebDriver): The WebDriver instance.
            xpath (str): The XPath of the element to be clicked.

        """
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath)),
            )
            element.click()
        except Exception as e:
            time.sleep(3)
            print(f"An error occurred when clicking element with XPath {xpath}: {e}")

    def click_comment_button(self, driver: WebDriver) -> None:
        """
        Clicks on the comment button with text "Top comments" or "Most relevant".

        Args:
            driver (WebDriver): The WebDriver instance.

        """
        try:
            self.click_element_with_retry(
                driver,
                '//span[text()="Top comments" or text()="Most relevant"]',
            )
        except Exception as e:
            print(f"No comment button is visible, will scroll down to find it: {e}")

            # Scroll down by 400 pixels
            scrollbar = self.locate_scrollbar()
            actions = ActionChains(driver)
            actions.click_and_hold(scrollbar).move_by_offset(0, 400).release().perform()

            try:
                # Wait again for the span element after scrolling
                self.click_element_with_retry(
                    driver,
                    '//span[text()="Top comments" or text()="Most relevant"]',
                )
            except Exception as e:
                print(f"Comment selection button not found even after scrolling: {e}")

    def click_all_comments_button(self, driver: WebDriver) -> None:
        """
        Clicks on the "All comments" button.

        Args:
            driver (WebDriver): The WebDriver instance.

        """
        try:
            self.click_element_with_retry(
                driver,
                '//span[text()="All comments" or text()="Oldest"]',
            )
            time.sleep(5)
        except Exception as e:
            print(f"Error clicking on all comments button: {e}")

    def locate_scrollbar(self) -> WebElement:
        """
        Locates and returns the scrollbar element.

        Args:
            driver (WebDriver): The WebDriver instance.

        Returns:
            WebElement: The located scrollbar element.

        """
        try:
            time.sleep(2)
            scrollbar_xpath = (
                '//*[starts-with(@id,'
                ' "mount_0")]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div'
                '/div/div/div/div/div/div[2]/div[5]'
            )
            scrollbar = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, scrollbar_xpath)),
            )
            return scrollbar
        except Exception as e:
            print(f"An error occurred when locating the scroll bar element: {e}")


if __name__ == '__main__':
    scraper = FacebookScraper()
    URL = 'https://www.facebook.com'
    asyncio.run(scraper.login(URL))
    keys = ['fintech', 'company', 'us']
    url = create_url_with_keys(URL, keys)
    scraper.driver.get(url)
    # nth_of_posts = 0
    # parent_element_xpath = (
    #     "//*[@id[starts-with(., 'mount_0_')] and"
    #     " descendant::*[@role='feed']]/div/div/div/div[3]/div/div/div[1]/"
    #     'div[1]/div[2]/div/div/div/div/div/div'
    # )