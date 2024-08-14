
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.remote.webdriver import WebDriver as SeleniumWebDriver
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
from selenium.webdriver import Safari
from selenium.webdriver import Edge

from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.edge.service import Service as EdgeService

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from weberist.generic.constants import OPERATING_SYSTEM

if 'win' in OPERATING_SYSTEM:
    from selenium.webdriver import FirefoxOptions  # noqa F811

__all__ = (
    "Firefox",
    "Chrome",
    "Safari",
    "Edge",
    "FirefoxOptions",
    "ChromeOptions",
    "SafariOptions",
    "EdgeOptions",
    "FirefoxService",
    "ChromeService",
    "SafariService",
    "EdgeService",
    "WebElement",
    "expected_conditions",
    "WebDriverWait",
    "ChromeDriverManager",
    "GeckoDriverManager",
    "EdgeChromiumDriverManager",
    "SeleniumWebDriver",
)
