from urllib3.exceptions import MaxRetryError
from requests.adapters import ReadTimeout
from requests.adapters import ConnectionError as RequestConnectionError
from selenium.webdriver.remote.errorhandler import NoSuchWindowException
from selenium.webdriver.remote.errorhandler import NoSuchElementException
from selenium.webdriver.remote.errorhandler import InvalidSessionIdException
from selenium.webdriver.remote.errorhandler import StaleElementReferenceException  # noqa E501
from selenium.webdriver.remote.errorhandler import ElementNotInteractableException  # noqa E501
from selenium.webdriver.remote.errorhandler import ElementClickInterceptedException  # noqa E501
from selenium.common.exceptions import WebDriverException

# exceptions for quit_on_failure
EXCEPTIONS = (
    ReadTimeout,
    WebDriverException,
    NoSuchWindowException,
    RequestConnectionError,
    NoSuchElementException,
    NoSuchElementException,
    InvalidSessionIdException,
    StaleElementReferenceException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
    Exception,
)

__all__ = (
    "MaxRetryError",
    "ReadTimeout",
    "RequestConnectionError",
    "NoSuchWindowException",
    "NoSuchElementException",
    "StaleElementReferenceException",
    "ElementNotInteractableException",
    "ElementClickInterceptedException",
    "WebDriverException",
)
