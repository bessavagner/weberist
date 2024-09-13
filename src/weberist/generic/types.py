from typing import Union, List, Dict, TypedDict, Any

from weberist.generic.shortcuts import (
    Firefox,
    Chrome,
    Safari,
    Edge,
    SeleniumWebDriver,
    FirefoxOptions,
    ChromeOptions,
    SafariOptions,
    EdgeOptions,
    FirefoxService,
    ChromeService,
    SafariService,
    EdgeService,
    WebElement,
    ChromeDriverManager,
    GeckoDriverManager,
    EdgeChromiumDriverManager
)

WebDriver = Union[Firefox, Chrome, Safari, Edge, SeleniumWebDriver]
WebDriverOptions = Union[
    FirefoxOptions,
    ChromeOptions,
    SafariOptions,
    EdgeOptions,
]
WebDriverServices = Union[
    FirefoxService,
    ChromeService,
    SafariService,
    EdgeService,
]
WebElements = List[WebElement]

WebDriverManagers = Union[
    ChromeDriverManager,
    GeckoDriverManager,
    EdgeChromiumDriverManager
]

class TypeBrowser(TypedDict):
    versions: List[int]
    default: int
    kwargs: Dict[str, Any]
