"""
This module provides a centralized management system for different web drivers,
including Firefox, Chrome, Safari, and Edge. It allows for easy access to the
web drivers, their options, services, and managers, facilitating the creation
and configuration of web driver instances for automated testing or web scraping
tasks.

The module includes a class `WebDrivers` that encapsulates the web drivers and
their associated components. It provides properties to access each web driver,
its options, services, and managers, as well as a method to retrieve a tuple
containing the web driver, its options, services, and managers for a specified
browser.

This module is part of the weberist project, a web automation and scraping
framework.
"""
import logging
from re import match
from typing import Any, List
from pathlib import Path

from weberist.generic.shortcuts import (
    Firefox,
    Chrome,
    Safari,
    Edge,
    FirefoxOptions,
    ChromeOptions,
    SafariOptions,
    EdgeOptions,
    FirefoxService,
    ChromeService,
    SafariService,
    EdgeService,
    ChromeDriverManager,
    GeckoDriverManager,
    EdgeChromiumDriverManager,
    SeleniumWebDriver,
)

from weberist.generic.types import (
    WebDriver,
    WebDriverOptions,
    WebDriverServices,
    WebDriverManagers
)
from weberist.generic.constants import (
    SUPPORTED_BROWSERS,
    DEFAULT_ARGUMENTS,
    SELENOID_CAPABILITIES,
)
from .data import UserAgent, WindowSize
from .config import DEFAULT_PROFILE

logger = logging.getLogger('standard')

def add_option(option: WebDriverOptions, arguments, browser: str = 'browser'):
    if isinstance(arguments, str):
        arguments = arguments.split(",")
    for argument in arguments:
        try:
            getattr(option, 'add_argument')(argument)
        except AttributeError as err:
            logger.warning(
                "%s: '%s' does'nt support adding options arguments",
                err,
                browser
            )
            return None
    return option


class WebDrivers:
    """
    A class that encapsulates the management of web drivers for different
    browsers, including Firefox, Chrome, Safari, and Edge. It provides
    properties to access each web driver, its options, services, and managers.
    This class is designed to simplify the process of configuring and
    retrieving web driver instances for automated testing or web scraping
    tasks.

    Attributes
    ----------
    firefox : Firefox
        An instance of the Firefox web driver.
    chrome : Chrome
        An instance of the Chrome web driver.
    safari : Safari
        An instance of the Safari web driver.
    edge : Edge
        An instance of the Edge web driver.
    firefox_options : FirefoxOptions
        Options for the Firefox web driver.
    chrome_options : ChromeOptions
        Options for the Chrome web driver.
    safari_options : SafariOptions
        Options for the Safari web driver.
    edge_options : EdgeOptions
        Options for the Edge web driver.
    firefox_service : FirefoxService
        Service for the Firefox web driver.
    chrome_service : ChromeService
        Service for the Chrome web driver.
    safari_service : SafariService
        Service for the Safari web driver.
    edge_service : EdgeService
        Service for the Edge web driver.
    firefox_manager : GeckoDriverManager
        Manager for the Firefox web driver.
    chrome_manager : ChromeDriverManager
        Manager for the Chrome web driver.
    safari_manager : None
        Manager for the Safari web driver.
    edge_manager : EdgeChromiumDriverManager
        Manager for the Edge web driver.
    supported : tuple[str]
        A tuple of supported browser names.
    """
    __firefox: Firefox = Firefox
    __chrome: Chrome = Chrome
    __safari: Safari = Safari
    __edge: Edge = Edge
    __chrome_remote: SeleniumWebDriver = SeleniumWebDriver
    __firefox_options: FirefoxOptions = FirefoxOptions
    __chrome_options: ChromeOptions = ChromeOptions
    __safari_options: SafariOptions = SafariOptions
    __edge_options: EdgeOptions = EdgeOptions
    __firefox_service: FirefoxService = FirefoxService
    __chrome_service: ChromeService = ChromeService
    __safari_service: SafariService = SafariService
    __edge_service: EdgeService = EdgeService
    __firefox_manager: GeckoDriverManager = GeckoDriverManager
    __chrome_manager: ChromeDriverManager = ChromeDriverManager
    __safari_manager = None
    __edge_manager: EdgeChromiumDriverManager = EdgeChromiumDriverManager
    supported: tuple[str] = SUPPORTED_BROWSERS

    @property
    def firefox(self,) -> Firefox:
        return self.__firefox

    @property
    def chrome(self,) -> Chrome:
        return self.__chrome

    @property
    def safari(self,) -> Safari:
        return self.__safari

    @property
    def edge(self,) -> Edge:
        return self.__edge

    @property
    def chrome_remote(self,) -> SeleniumWebDriver:
        return self.__chrome_remote

    @property
    def firefox_options(self,) -> FirefoxOptions:
        return self.__firefox_options

    @property
    def chrome_options(self,) -> ChromeOptions:
        return self.__chrome_options

    @property
    def safari_options(self,) -> SafariOptions:
        return self.__safari_options

    @property
    def edge_options(self,) -> EdgeOptions:
        return self.__edge_options

    @property
    def firefox_service(self,) -> FirefoxService:
        return self.__firefox_service

    @property
    def chrome_service(self,) -> ChromeService:
        return self.__chrome_service

    @property
    def safari_service(self,) -> SafariService:
        return self.__safari_service

    @property
    def edge_service(self,) -> EdgeService:
        return self.__edge_service

    @property
    def firefox_manager(self,) -> GeckoDriverManager:
        return self.__firefox_manager

    @property
    def chrome_manager(self,) -> ChromeDriverManager:
        return self.__chrome_manager

    @property
    def safari_manager(self,) -> None:
        return self.__safari_manager

    @property
    def edge_manager(self,) -> EdgeChromiumDriverManager:
        return self.__edge_manager

    def get(self, browser: str) -> tuple[
        WebDriver, WebDriverOptions, WebDriverServices, WebDriverManagers
    ]:
        """
        Retrieves a tuple containing the web driver, its options, services,
        and managers for the specified browser.

        This method dynamically accesses the appropriate attributes based on
        the browser name provided. It raises an AttributeError if the specified
        browser is not supported.

        Parameters
        ----------
        browser : str
            The name of the browser for which to retrieve the web driver, its
            options, services, and managers. Supported browsers include
            "firefox", "chrome", "safari" and "edge".

        Returns
        -------
        tuple[WebDriver, WebDriverOptions, WebDriverServices, WebDriverManagers]  # noqa E501
            A tuple containing the web driver, its options, services, and
            managers for the specified browser.

        Raises
        ------
        AttributeError
            If the specified browser is not supported.
        """
        if not hasattr(self, browser):
            raise AttributeError(
                f'WebDrivers does not implement driver for {browser}'
            )
            
        driver = getattr(self, browser)
        if 'remote' in browser:
            browser = browser.split('_')[0]
        option = getattr(self, f"{browser}_options")
        service = getattr(self, f"{browser}_service")
        manager = getattr(self, f"{browser}_manager")
        return driver, option, service, manager


class WebDriverFactory(SeleniumWebDriver):

    def __init__(self, *args, **kwargs):
        self.service: WebDriverServices = None
        super().__init__(*args, **kwargs)

    def __new__(cls,
                *args,
                browser: str = 'chrome',
                options_arguments: List[str] = None,
                services_kwargs: dict[str, Any] = None,
                keep_alive: bool = True,
                extensions: List[str | Path] = None,
                **kwargs,) -> WebDriver:
        
        cls_properties = {
            name: getattr(cls, name)
            for name in dir(cls) if not match("__.*__", name)
        }
        driver, options_class, service, manager = WebDrivers().get(browser)
        options_obj: WebDriverOptions = options_class()
        
        if browser in DEFAULT_ARGUMENTS:
            if options_arguments is None:
                options_arguments = []
            options_arguments.extend(list(DEFAULT_ARGUMENTS[browser]))
       
        user_agent = None
        windows_size = None
        user_agent_string = None
        windows_size_ = None
        profile_name = None
        if options_arguments:
            if not isinstance(options_arguments, list):
                raise TypeError("'options_arguments' must be a list")
            if not all(isinstance(item, str) for item in options_arguments):
                raise TypeError("'options_arguments' must be a list of str")
            for argument in options_arguments:
                if user_agent_string is None and 'user-agent' in argument:
                    user_agent_string = argument.split("=")[-1]
                    continue
                if windows_size_ is None and 'windows-size' in argument:
                    windows_size_ = argument.split("=")[-1]
                    continue
                if profile_name is None and 'profile-directory' in argument:
                    profile_name = argument.split("=")[-1]
                options_obj = add_option(options_obj, argument, browser)
                if options_obj is None:
                    options_obj: WebDriverOptions = options_class()
                    break
            
        if 'chrome' in browser and 'experimental_options' in kwargs:
            for name, value in kwargs['experimental_options'].items():
                options_obj.add_experimental_option(name, value)
            kwargs.pop('experimental_options')
        
        if extensions:
            if not isinstance(extensions, list):
                raise TypeError("'extensions' must be a list")
            if not all(isinstance(item, (str, Path))for item in extensions):
                raise TypeError("'extensions' must be a list of str")
            if all(isinstance(item, Path)for item in extensions):
                argument = '--load-extension=' + ','.join(
                    [str(path) for path in extensions]
                )
            else:
                for argument in extensions:
                    try:
                        getattr(options_obj, 'add_extension')(argument)
                    except AttributeError as err:
                        logger.warning(
                            "%s: '%s' doesn't support adding extensions",
                            err,
                            browser
                        )
                        break
        
        executable_path = None
        user_agent = UserAgent()
        windows_size = WindowSize()
        
        if 'remote' in browser:
            capabilities = SELENOID_CAPABILITIES
            for option in options_obj.arguments:
                if '--user-data-dir' in option:
                    capabilities['selenoid:options']['env'] = (
                        [f'BROWSER_PROFILE_DIR={option.split("=")[-1]}']
                    )
                    if profile_name is None:
                        profile_name = DEFAULT_PROFILE
                    break
            if 'capabilities' in kwargs:
                capabilities.update(kwargs['capabilities'])
            for name, value in capabilities.items():
                options_obj.set_capability(name, value)
            if 'command_executor' not in kwargs:
                kwargs['command_executor'] = "http://0.0.0.0:4444/wd/hub"
        
        if profile_name is not None:
            user_agent_string = user_agent.get_hashed(profile_name)
            windows_size_ = windows_size.get_hashed(profile_name)
        if user_agent_string is None:
            user_agent_string = user_agent.get_random()
        if windows_size_ is None:
            windows_size_ = windows_size.get_random()
        windows_size_string = windows_size_
        if not isinstance(windows_size_, str):
            windows_size_string = windows_size.to_string(windows_size_)
        arguments = [
            f"--user-agent={user_agent_string}",
            f"--window-size={windows_size_string}"
        ]
        options_obj = add_option(options_obj, arguments, browser)
        if options_obj is None:
            options_obj: WebDriverOptions = options_class()

        if 'command_executor' not in kwargs:  # other wise it is remote conn
            if hasattr(manager, 'install'):
                executable_path = manager().install()
            if services_kwargs:
                service = service(executable_path, **services_kwargs)
            else:
                service = service(executable_path)
            kwargs['service'] = service

        return type(cls.__name__, (driver,), cls_properties)(
            *args,
            options=options_obj,
            keep_alive=keep_alive,
            **kwargs
        )

    @classmethod
    def option_method(cls, method: str, value: Any) -> None:
        # TODO
        pass
