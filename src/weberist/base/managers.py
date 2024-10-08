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
import gc
import time
import socket
import logging
from re import match
from typing import Any, List, Dict, Tuple
from pathlib import Path

from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver.remote.file_detector import FileDetector
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium_stealth import (
    with_utils,
    chrome_app,
    chrome_runtime,
    iframe_content_window,
    media_codecs,
    navigator_languages,
    navigator_permissions,
    navigator_plugins,
    navigator_vendor,
    navigator_webdriver,
    user_agent_override,
    webgl_vendor_override,
    window_outerdimensions,
    hairline_fix,
)
from selenium_stealth.wrapper import evaluateOnNewDocument

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
    DEFAULT_ARGUMENTS,
    SELENOID_CAPABILITIES,
    SUPPORTED_BROWSERS,
)

from .data import UserAgent, WindowSize
from .config import DEFAULT_PROFILE, ROOT_DIR, LOCALSTORAGE
from .stealth.tools import remove_cdc

logger = logging.getLogger('standard')

def free_port() -> int:
    """Get free port."""
    sock = socket.socket()
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()
    del sock
    gc.collect()
    return port

def add_option(option: WebDriverOptions, arguments, browser: str = 'chrome'):

    proceed_argument = True
    proceed_experimental = True
    for argument in arguments:
        if isinstance(argument, str) and proceed_argument:
            try:
                getattr(option, 'add_argument')(argument)
            except AttributeError:
                logger.warning("'%s' doesn't support adding option", browser)
                proceed_argument = False
                continue
        if isinstance(argument, dict):
            if 'chrome' in browser and proceed_experimental:
                for name, value in argument.items():
                    try:
                        getattr(option, 'add_experimental_option')(name, value)
                    except AttributeError:
                        logger.warning(
                            "'%s' doesn't support adding experimental option",
                            browser
                        )
                        proceed_argument = False
                        break
        if not (proceed_argument or proceed_experimental):
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
    __drivers = {
        "firefox": {
            "driver": Firefox,
            "options": FirefoxOptions,
            "service": FirefoxService,
            "manager": GeckoDriverManager
        },
        "chrome": {
            "driver": Chrome,
            "options": ChromeOptions,
            "service": ChromeService,
            "manager": ChromeDriverManager
        },
        "chrome_remote": {
            "driver": SeleniumWebDriver,
            "options": ChromeOptions,
            "service": None,
            "manager": None
        },
        "safari": {
            "driver": Safari,
            "options": SafariOptions,
            "service": SafariService,
            "manager": None
        },
        "edge": {
            "driver": Edge,
            "options": EdgeOptions,
            "service": EdgeService,
            "manager": EdgeChromiumDriverManager
        }
    }

    supported: Tuple[str] = tuple(__drivers.keys())

    def get(self,
            browser: str,
            option_arguments: List[str] = None,
            extensions: str | List[str] = None,
            capabilities: Dict = None,
            services_kwargs: Dict = None,
            **kwargs) -> tuple[
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
        if browser not in self.supported:
            raise AttributeError(
                f'WebDrivers does not support driver for {browser}'
            )

        driver = self.__drivers[browser]['driver']
        option, service = self._configure(
            browser,
            option_arguments,
            extensions,
            capabilities,
            services_kwargs,
            **kwargs
        )
        if 'remote' in browser:
            browser = browser.split('_')[0]
        return driver, option, service

    def _configure_chrome(self,
                          options: WebDriverOptions,
                          manager: WebDriverManagers,
                          service_class: type[WebDriverServices],
                          option_arguments: List[str],
                          extensions: str | List[str] = None,
                          capabilities: Dict = None,
                          service_kwargs: Dict = None,
                          host: str = None,
                          port: int = None,
                          lang: str = 'en-US',
                          remote: bool = False):

        if extensions:
            if all(isinstance(item, Path) for item in extensions):
                argument = '--load-extension=' + ','.join(
                    [str(path) for path in extensions]
                )
                options.add_argument(argument)
            else:
                for argument in extensions:
                    options.add_extension(argument)

        user_agent_string = None
        windows_size_ = None
        profile_name = None

        for argument in option_arguments:

            if user_agent_string is None and 'user-agent' in argument:
                user_agent_string = argument.split("=")[-1]
                continue
            if windows_size_ is None and 'windows-size' in argument:
                windows_size_ = argument.split("=")[-1]
                continue
            if profile_name is None and 'profile-directory' in argument:
                profile_name = argument.split("=")[-1]

        user_agent = UserAgent()
        windows_size = WindowSize()

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
        option_arguments.extend(
            [
                f"--user-agent={user_agent_string}",
                f"--window-size={windows_size_string}"
            ]
        )

        host = host or "127.0.0.1"
        port = port or free_port()
        option_arguments.append(f"--remote-debugging-host={host}")
        option_arguments.append(f"--remote-debugging-port={port}")
        option_arguments.append(f'--lang={lang}')

        service = None
        if capabilities is None:
            capabilities = {}
        if remote:
            capabilities.update(SELENOID_CAPABILITIES)
            for option in options.arguments:
                if '--user-data-dir' in option:
                    capabilities['selenoid:options']['env'] = (
                        [f'BROWSER_PROFILE_DIR={option.split("=")[-1]}']
                    )
                    if profile_name is None:
                        profile_name = DEFAULT_PROFILE
                    break
        else:
            executable_path = None
            if hasattr(manager, 'install'):
                executable_path = manager().install()
                if service_kwargs:
                    service = service_class(executable_path, **service_kwargs)
                else:
                    service = service_class(executable_path)
                remove_cdc(service.path)

        for name, value in capabilities.items():
            options.set_capability(name, value)

        options = add_option(options, option_arguments, 'chrome')

        return options, service

    def _configure(self,
                   browser: str,
                   option_arguments: List[str],
                   extensions: str | List[str] = None,
                   capabilities: Dict = None,
                   service_kwargs: Dict = None,
                   **kwargs):

        browser_name = browser
        remote = False
        if 'remote' in browser:
            remote = True
            browser_name = browser.split('_')[0]

        options_class = self.__drivers[browser_name]['options']
        service_class = self.__drivers[browser_name]['service']
        manager = self.__drivers[browser_name]['manager']

        options: WebDriverOptions = options_class()
        option_arguments = option_arguments or []

        if browser_name == 'chrome':
            return self._configure_chrome(
                options,
                manager,
                service_class=service_class,
                option_arguments=option_arguments,
                extensions=extensions,
                capabilities=capabilities,
                service_kwargs=service_kwargs,
                remote=remote,
                **kwargs,
            )

        if extensions:
            logger.warning("Extensions only implemented for chrome.")
        if capabilities:
            logger.warning("Capabilities only implemented for chrome.")

        options = add_option(options, option_arguments, browser)
        options = options or options_class()

        service = None
        executable_path = None
        if hasattr(manager, 'install'):
            executable_path = manager().install()
            if service_kwargs:
                service = service_class(executable_path, **service_kwargs)
            else:
                service = service_class(executable_path)

        return options, service


class WebDriverFactory(SeleniumWebDriver):
    
    service: WebDriverServices = None
    
    @classmethod
    def _set_up(cls,
                browser: str,
                arguments: List[str | Dict],
                **kwargs):

        cls_properties = {
            name: getattr(cls, name)
            for name in dir(cls) if not match("__.*__", name)
        }
        if browser.split("_")[0] in DEFAULT_ARGUMENTS:
            arguments = arguments or []
            arguments.extend(list(DEFAULT_ARGUMENTS[browser.split("_")[0]]))

        if 'remote' in browser and 'command_executor' not in kwargs:
            kwargs['command_executor'] = "http://0.0.0.0:4444/wd/hub"

        if 'chrome' in browser:
            experimental_options = kwargs.pop("experimental_options", {})
            if 'profile' in kwargs and kwargs['profile']:
                arguments.append(
                    f"--profile-directory={kwargs['profile']}"
                )
                kwargs.pop('profile')
            if 'localstorage' in kwargs and kwargs['localstorage']:
                arguments.append(
                    f"--user-data-dir={kwargs['localstorage']}"
                )
                kwargs.pop('localstorage')
            experimental_options.update(
                {
                    "excludeSwitches": ["enable-automation"],
                    "useAutomationExtension": False
                }
            )
            arguments.append(experimental_options)

        kwargs.pop('quit_on_failure', None)
        kwargs.pop('timeout', None)

        return browser, cls_properties, arguments, kwargs

    def __new__(cls,
                *args,
                browser: str = 'chrome',
                option_arguments: List[str] = None,
                services_kwargs: dict[str, Any] = None,
                keep_alive: bool = True,
                extensions: List[str | Path] = None,
                capabilities: Dict = None,
                stealth: bool = True,
                **kwargs,) -> WebDriver:

        capabilities = kwargs.get('capabilities', None)
        browser, cls_properties, option_arguments, kwargs = cls._set_up(
            browser, option_arguments, **kwargs
        )

        host = kwargs.pop("host", None)
        port = kwargs.pop("port", None)
        lang = kwargs.pop("lang", 'en')
        # selenium-stealth arguments:
        languages = kwargs.pop("languages", ["en-US", "en"])
        vendor = kwargs.pop("vendor", "Google Inc.")
        webgl_vendor = kwargs.pop("webgl_vendor", "Intel Inc.")
        renderer = kwargs.pop("renderer", "Intel Iris OpenGL Engine")
        run_on_insecure_origins = kwargs.pop("run_on_insecure_origins", False)

        driver, options, service = WebDrivers().get(
            browser,
            option_arguments,
            extensions,
            capabilities,
            services_kwargs,
            host=host,
            port=port,
            lang=lang,
        )

        if service is not None:
            kwargs['service'] = service

        kwargs.pop('profile', None)
        kwargs.pop('localstorage', None)

        instance: WebDriver = type(cls.__name__, (driver, ), cls_properties)(
            *args,
            options=options,
            keep_alive=keep_alive,
            **kwargs
        )

        if stealth:
            if 'chrome' not in browser:
                logger.warning('Stealthiness only supported in chrome')
                return instance
            if lang not in languages:
                languages.append(lang)
            ua_languages = ','.join(languages)

            # Default selenium_stealth functions
            with_utils(instance, **kwargs)
            chrome_app(instance, **kwargs)
            chrome_runtime(instance, run_on_insecure_origins, **kwargs)
            iframe_content_window(instance, **kwargs)
            media_codecs(instance, **kwargs)
            navigator_languages(instance, languages, **kwargs)
            navigator_permissions(instance, **kwargs)
            navigator_plugins(instance, **kwargs)
            navigator_vendor(instance, vendor, **kwargs)
            navigator_webdriver(instance, **kwargs)
            user_agent_override(instance, ua_languages=ua_languages, **kwargs)
            webgl_vendor_override(instance, webgl_vendor, renderer, **kwargs)
            window_outerdimensions(instance, **kwargs)
            hairline_fix(instance, **kwargs)

            # Hide selenium fingerprints
            selenium_fingerprint = Path(
                ROOT_DIR / 'base/stealth/js/selenium.fingerprint.js'
            ).read_text(encoding='utf-8')
            evaluateOnNewDocument(instance, selenium_fingerprint)

            error_stack_override = Path(
                ROOT_DIR / 'base/stealth/js/error.stack.override.js'
            ).read_text(encoding='utf-8')
            evaluateOnNewDocument(instance, error_stack_override)
            webgl_override = Path(
                ROOT_DIR / 'base/stealth/js/webgl.worker.override.js'
            ).read_text(encoding='utf-8')
            evaluateOnNewDocument(
                instance, webgl_override
            )
            #NOTE: add time.sleep
            # time.sleep(0.5)

        return instance
