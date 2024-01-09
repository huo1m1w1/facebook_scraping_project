from __future__ import annotations

import json
import time
from unittest.mock import AsyncMock
from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webelement import WebElement

from ..src.fb_scraping_project.scraper import check_comments
from ..src.fb_scraping_project.scraper import create_url_with_keys
from ..src.fb_scraping_project.scraper import FacebookScraper
from ..src.fb_scraping_project.scraper import get_superlinks
from ..src.fb_scraping_project.scraper import save_to_json


@pytest.fixture
def scraper():
    # Assuming FacebookScraper is initialized properly in your implementation
    return FacebookScraper()


@pytest.mark.parametrize(
    'list_text, expected_result',
    [
        (['5 comments', 'comment'], (True, '5 comments')),
        (['comment', 'anycomment'], (False, '')),
        (['comment', '5 comments', 'Comment section'], (True, '5 comments')),
    ],
)
def test_check_comments(list_text, expected_result):
    """
    Test case for the check_comments function.

    Parameters:
    - list_text (List[str]): A list of text elements.
    - expected_result (Tuple[bool, str]): The expected result of the function.

    Returns:
    None: The test passes if the actual result matches the expected result.
    """

    assert check_comments(list_text)[0] == expected_result[0]
    assert check_comments(list_text)[1] == expected_result[1]


@pytest.fixture
def _sample_html_element():
    """
    Fixture that returns a sample HTML element for testing the get_superlinks function.

    Returns:
        Tag | NavigableString | None: The sample HTML element.
    """
    html_content = (
        '<div><a href="http://example.com">Link 1'
        '</a><a href="http://example2.com">Link 2</a></div>'
    )
    return BeautifulSoup(html_content, 'html.parser').find('div')


def test_get_superlinks():
    """
    Test case for the get_superlinks function.

    Parameters:
    - sample_html_element: A sample HTML element fixture.

    Returns:
    None: The test passes if the actual result matches the expected result.
    """
    # Mock WebElement for testing
    element = Mock(spec=WebElement)
    element.get_attribute.return_value = (
        '<a href="https://example.com">Link 1</a>'
        '<div><a href="http://example.com">Link 1</a>'
        '<a href="http://example2.com">Link 2</a></div>'
    )
    # Test case for extracting links
    links = get_superlinks(element)
    assert links == ['https://example.com', 'http://example.com', 'http://example2.com']


@pytest.mark.parametrize(
    'base_url, key_words, expected_url',
    [
        (
            'https://example.com/search?q=',
            ['python', 'programming', 'tips'],
            'https://example.com/search?q=python%20programming%20tips',
        ),
        (
            'https://example.com/search?q=',
            ['data', 'science', 'tutorial'],
            'https://example.com/search?q=data%20science%20tutorial',
        ),
        (
            'https://example.com/search?q=',
            ['web', 'development'],
            'https://example.com/search?q=web%20development',
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_url_with_keys(base_url, key_words, expected_url):
    """
    Test case for the create_url_with_keys function.

    Parameters:
    - base_url (str): The base URL.
    - key_words (List[str]): A list of search keys.
    - expected_url (str): The expected generated URL.

    Returns:
    None: The test passes if the actual result matches the expected result.
    """
    result = await create_url_with_keys(base_url, key_words)
    assert result == expected_url


@pytest.mark.asyncio
async def test_save_to_json(tmp_path):
    """
    Test case for the save_to_json function.

    Parameters:
    - tmp_path: Pytest fixture for a temporary directory.

    Returns:
    None: The test passes if the actual result matches the expected result.
    """
    jsonfile = tmp_path / 'test.json'
    input_dict = {'key': 'value', 'number': 42}

    await save_to_json(str(jsonfile), input_dict)

    # Read the content of the written JSON file
    with open(jsonfile) as file:
        data = json.load(file)

    assert data == [input_dict]


time.sleep(3)


@pytest.fixture
def facebook_scraper():
    return FacebookScraper()


time.sleep(3)


@pytest.mark.asyncio
async def test_login_success(facebook_scraper):
    # Mocking the necessary functions for a successful login
    with patch.object(
        FacebookScraper,
        '_load_credentials',
        new_callable=AsyncMock,
    ) as mock_load_credentials, patch.object(
        FacebookScraper,
        '_navigate_to_facebook',
        new_callable=AsyncMock,
    ) as mock_navigate, patch.object(
        FacebookScraper,
        '_login_with_credentials',
        new_callable=AsyncMock,
    ) as mock_login, patch.object(
        FacebookScraper,
        '_wait_for_successful_login',
        new_callable=AsyncMock,
    ) as mock_wait:
        # Call the login method
        await facebook_scraper.login('https://facebook.com')

        # Assert that the necessary functions were called
        mock_load_credentials.assert_called_once()
        mock_navigate.assert_called_once_with('https://facebook.com')
        mock_login.assert_called_once()
        mock_wait.assert_called_once()


time.sleep(3)


@pytest.mark.asyncio
async def test_login_missing_credentials(facebook_scraper, capsys):
    # Mocking the _load_credentials function to raise a KeyError
    with patch.object(
        FacebookScraper, '_load_credentials', side_effect=KeyError('Missing credential'),
    ):
        # Call the login method
        await facebook_scraper.login('https://facebook.com')

        # Capture and check the printed output
        captured = capsys.readouterr()
        assert 'Missing credential' in captured.out


time.sleep(3)


@pytest.mark.asyncio
async def test_is_scroll_at_end(facebook_scraper):
    # Mocking necessary properties and methods for is_scroll_at_end
    with patch.object(facebook_scraper.driver, 'execute_script') as mock_execute_script:
        # Mock the return values for execute_script
        mock_execute_script.side_effect = [100, 1000, 800]

        # Call is_scroll_at_end
        await facebook_scraper.is_scroll_at_end()

        # Assert that the execute_script was called with the correct arguments
        expected_calls = [
            call('return window.scrollY;'),
            # Add more expected calls as needed
        ]
        mock_execute_script.assert_has_calls(expected_calls, any_order=True)
