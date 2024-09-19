import gc
import logging
import traceback
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Dict
from pathlib import Path

from bs4 import BeautifulSoup
from lxml import etree


from weberist.generic.shortcuts import WebDriverWait
from weberist.generic.shortcuts import expected_conditions as EC
from weberist.generic.utils import extract_base_url
from weberist.generic.constants import ATTR_SELECTOR
from weberist.generic.types import (
    WebDriver,
    WebElement,
    WebElements,
    WebDriverServices,
)
from weberist.utils.helpers import Key
from weberist.utils.javascript import (
    document_query_selector,
    document_query_selector_all,
    is_display,
    DISPATCH_ENTER,
    DISPATCH_ENTER_SELECTOR,
)
from .data import ProfileStorageBackend
from .managers import WebDriverFactory
from .exceptions import (
    EXCEPTIONS,
    WebDriverException,
    NoSuchWindowException,
    NoSuchElementException,
    InvalidSessionIdException,
)


logger = logging.getLogger('base.drivers')
logger.setLevel(logging.DEBUG)


class BaseDriver(WebDriverFactory):
    
    def __new__(cls,
                *args,
                browser: str = 'chrome',
                option_arguments: List[str] = None,
                services_kwargs: dict[str, Any] = None,
                keep_alive: bool = True,
                extensions: List[str | Path] = None,
                capabilities: Dict = None,
                quit_on_failure: bool = False,
                timeout: int = 20,
                profile: str = None,
                localstorage: str = None,
                **kwargs,) -> WebDriver:
        
        kwargs['profile'] = profile
        kwargs['localstorage'] = localstorage
        
        instance: WebDriver = super().__new__(
            cls,
            *args,
            browser=browser,
            option_arguments=option_arguments,
            services_kwargs=services_kwargs,
            keep_alive=keep_alive,
            extensions=extensions,
            capabilities=capabilities,
            **kwargs,
        )
        
        profile = kwargs['profile'] = kwargs.get('profile', None)
        localstorage = kwargs['localstorage'] = kwargs.get('localstorage', None)
        cls.__init__(
            instance,
            quit_on_failure=quit_on_failure,
            timeout=timeout,
            profile=profile,
            localstorage=localstorage,
        )
        return instance


    def __init__(self: WebDriver,
                 quit_on_failure: bool = False,
                 timeout: int = 20,
                 profile: str = None,
                 localstorage: str = None) -> None:
        
        self._quit_on_failure = quit_on_failure
        self.timeout = timeout
        self.target_path = Path('.')
        self.soup = None
        self.dom = None
        
        if profile and localstorage:
            self.target_path = Path(localstorage)
            self.profile_backend = ProfileStorageBackend(self.target_path)

    def __enter__(self):
        self._quit_on_failure = False
        return self

    def __exit__(self, exc_type, exc_value, traceback_):
        if exc_type or exc_value or traceback_:
            logger.error("Exception occurred: %s", exc_value)
        self.quit_driver()
    
    @property
    def quit_on_failure(self,):
        return self._quit_on_failure

    @staticmethod
    def quitonfailure(method: Callable) -> Callable:
        """
        A decorator that ensures the web driver is safely quit to avoid memory
        leakages in case of exceptions. This method is designed to be used as a
        decorator for methods that may raise exceptions during web automation
        tasks.

        Parameters
        ----------
        method : Callable
            The method to be decorated. This method should be a callable that
            takes an instance of the `BaseCrawler` class as its first argument.

        Returns
        -------
        Callable
            The decorated method, which will now include additional error
            handling to quit the
            web driver if an exception is raised.

        Notes
        -----
        This method is a static method and should be used as a decorator.
        """
        # pylint: disable=W0613
        def inner(self, *args, **kwargs) -> Callable:
            try:
                # pylint: disable=not-callable
                return method(self, *args, **kwargs)
            except EXCEPTIONS as err:
                logger.error(err)
                logger.error(traceback.format_exc())
                if self.quit_on_failure:
                    logger.warning("Closing window and quitting driver.")
                    self.quit_driver()
                    logger.warning("Driver quit.")
                raise err

        return inner

    def quit_driver(self):
        try:
            self.quit()
        except EXCEPTIONS as err:
            logger.error("Error while quitting driver: %s", err)
        finally:
            logger.info("Driver quit successfully.")
            self._cleanup()

    def _cleanup(self):
        if hasattr(self, 'service') and self.service:
            try:
                self.service.stop()
            except EXCEPTIONS as err:
                logger.error("Error while stopping service: %s", err)
        gc.collect()

    def is_running(self,) -> bool:
        """
        Checks if the web driver is currently running.

        This method attempts to assert that the web driver's service process
        is still running. It returns True if the process is running, and False
        otherwise.

        Returns
        -------
        bool
            True if the web driver's service process is running, False
            otherwise.
        """
        try:
            return isinstance(self.current_url, str)
        except (WebDriverException, InvalidSessionIdException):
            return False

    @quitonfailure
    def base_url(self,):
        return extract_base_url(self.current_url)

    @quitonfailure
    def tab_handle(self):
        """
        Retrieves the handle of the current window (tab) of the web driver.

        Returns
        -------
        str
            The handle of the current window (tab) of the web driver.
        """
        return self.current_window_handle

    @quitonfailure
    def tabs(self):
        """
        Retrieves a list of handles for all open windows (tabs) of the web
        driver.

        Returns
        -------
        List[str]
            A list of handles for all open windows (tabs) of the web driver.
        """
        return self.window_handles

    @quitonfailure
    def switch_to_tab(self, index: int):
        """
        Switches the web driver's focus to the tab at the specified index.

        Parameters
        ----------
        index : int
            The index of the tab to switch to.

        Raises
        ------
        IndexError
            If the index is out of range of the available tabs.
        """
        tabs = self.tabs()
        if len(tabs) <= index:
            logger.warning(
                "Trying to switch to tab nº %d, but there are only %d tabs",
                index,
                len(tabs),
            )
        else:
            self.switch_to.window(tabs[index])

    def wait(
        self,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException, )
    ):
        """
        Returns a WebDriverWait object that can be used to wait for a condition
        to be met.

        Parameters
        ----------
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebDriverWait
            A WebDriverWait object configured with the specified parameters.
        """
        if timeout is None:
            timeout = self.timeout
        return WebDriverWait(
            self, timeout, poll_frequency, ignored_exceptions
        )

    @quitonfailure
    def close_tab(self):
        """
        Attempts to close the current tab of the web driver. If the current
        tab cannot be closed, it switches to the first tab and closes it.

        Raises
        ------
        NoSuchWindowException
            If the current tab cannot be closed.
        """
        try:
            self.close()
        except NoSuchWindowException:
            tab_index = 0
            current_tab = self.tab_handle()
            for index, tab in enumerate(self.tabs()):
                if tab == current_tab:
                    tab_index = index
            logger.warning(
                "Tab %d no longer exists. Switching to tab 0", tab_index
            )
            self.switch_to_tab(0)

    def close_driver(self, quit_driver=True):
        """
        Attempts to close the current window of the web driver. If the current
        window cannot be closed, it switches to the first tab and closes it.
        If `quit_driver` is True, it also quits the web driver.

        Parameters
        ----------
        quit_driver : bool, optional
            Whether to quit the web driver after closing the current window.
            Default is True.
        """
        try:
            self.close()
        except NoSuchWindowException:
            self.switch_to_tab(0)
            self.close()
        except WebDriverException:
            pass
        if quit_driver:
            self.quit()
    
    @quitonfailure
    def goto(self, url: str) -> None:
        """
        Navigates the web driver to the specified URL.

        Parameters
        ----------
        url : str
            The URL to navigate to.
        """
        self.get(url)

    @quitonfailure
    def select(
        self,
        value: str,
        by: str = "id",
        expected_condition=EC.presence_of_element_located,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ) -> WebElement:
        """
        Finds an element on the web page using the specified locator strategy
        and waits until the element is present.

        Parameters
        ----------
        value : str
            The value to search for, such as the ID, name, or XPath of the
            element.
        by : str, default "id"
            The locator strategy to use, such as "id", "name", "xpath", etc.
        expected_condition : Callable, default EC.presence_of_element_located
            The expected condition to wait for, such as the presence of the
            element.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElement
            The first matching element found.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        if timeout is None:
            timeout = self.timeout
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        result = wait.until(expected_condition((ATTR_SELECTOR[by], value)))
        return result

    @quitonfailure
    def select_elements(
        self,
        value: str,
        by: str = "id",
        expected_condition=EC.presence_of_all_elements_located,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ) -> WebElements:
        """
        Finds all elements on the web page that match the specified locator
        strategy and waits until at least one element is present.


        Parameters
        ----------
        value : str
            The value to search for, such as the ID, name, or XPath of the
            elements.
        by : str, default "id"
            The locator strategy to use, such as "id", "name", "xpath", etc.
        expected_condition : Callable, default
        EC.presence_of_all_elements_located
            The expected condition to wait for, such as the presence of the
            elements.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElements
            A list of all matching elements found.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        return self.select(
            value,
            by,
            expected_condition,
            timeout,
            poll_frequency,
            ignored_exceptions
        )

    @quitonfailure
    def xpath(
        self,
        value: str,
        expected_condition=EC.presence_of_all_elements_located,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ) -> WebElements:
        """
        Finds all elements on the web page that match the specified XPath and
        waits until at least one element is present.


        Parameters
        ----------
        value : str
            The XPath expression to search for.
        expected_condition : Callable, default EC.presence_of_all_elements_located  # noqa E501
            The expected condition to wait for, such as the presence of the
            elements.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElements
            A list of all matching elements found.
        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        return self.select_elements(
            value,
            "xpath",
            expected_condition,
            timeout,
            poll_frequency,
            ignored_exceptions
        )

    @quitonfailure
    def find_text(self,
                    value: str,
                    tag: str = None,
                    expected_condition=EC.presence_of_all_elements_located,
                    timeout=None,
                    poll_frequency=0.5,
                    ignored_exceptions=(NoSuchElementException,)):
        if tag is None:
            tag = "*"
        xpath = f"//{tag}[text()='{value}']"
        result = self.xpath(
            value=xpath,
            expected_condition=expected_condition,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
        )
        if result and len(result) > 0:
            return result
        return None

    @quitonfailure
    def find_contains_text(self,
                           value: str,
                           tag: str = None,
                           expected_condition=EC.presence_of_all_elements_located,
                           timeout=None,
                           poll_frequency=0.5,
                           ignored_exceptions=(NoSuchElementException,)):
        if tag is None:
            tag = "*"
        xpath = f"//{tag}[contains(text(), '{value}')]"
        result = self.xpath(
            value=xpath,
            expected_condition=expected_condition,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
        )
        if result and len(result) > 0:
            return result
        return None
    
    @quitonfailure
    def send_to(
        self,
        element: WebElement,
        key: str | Key,
        expected_condition=EC.element_to_be_clickable,
        enter=False,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Sends a key to the specified web element and optionally presses the
        Enter key.


        Parameters
        ----------
        element : WebElement
            The web element to send the key to.
        key : str | Key
            The key or text to send to the element.
        expected_condition : Callable, default EC.element_to_be_clickable
            The expected condition to wait for before sending the key.
        enter : bool, default False
            Whether to press the Enter key after sending the key.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElement
            The element to which the key was sent.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element)).send_keys(key)
        if enter:
            element.send_keys(Key.enter)

    @quitonfailure
    def send(
        self,
        value: str,
        key: str | Key,
        by="id",
        expected_condition_element=EC.presence_of_element_located,
        expected_condition_send=EC.element_to_be_clickable,
        enter=False,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        element = self.select(
            value=value,
            by=by,
            expected_condition=expected_condition_element,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )
        self.send_to(
            element,
            key,
            expected_condition=expected_condition_send,
            enter=enter,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    @quitonfailure
    def child(
        self,
        element: WebElement,
        value: str,
        by="id",
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Finds a child element of the specified web element using the specified
        locator strategy and waits until the element is visible.

        Parameters
        ----------
        element : WebElement
            The parent web element to find the child element within.
        value : str
            The value to search for, such as the ID, name, or XPath of the
            child element.
        by : str, default "id"
            The locator strategy to use, such as "id", "name", "xpath", etc.
        expected_condition : Callable, default EC.visibility_of
            The expected condition to wait for, such as the visibility of the
            child element.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElement
            The first matching child element found.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        descendant = wait.until(
            lambda elem: element.find_element(ATTR_SELECTOR[by], value)
        )
        return descendant

    @quitonfailure
    def child_by_class_name(
        self,
        element: WebElement,
        value: str,
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Finds a child element of the specified web element by class name and
        waits until the element is visible.

        Parameters
        ----------
        element : WebElement
            The parent web element to find the child element within.
        value : str
            The class name to search for.
        expected_condition : Callable, default EC.visibility_of
            The expected condition to wait for, such as the visibility of the
            child element.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElement
            The first matching child element found by class name.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        descendant = wait.until(
            lambda elem: element.find_element(
                ATTR_SELECTOR['class name'], value)
        )
        return descendant

    @quitonfailure
    def children(
        self,
        element: WebElement,
        value: str,
        by="id",
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Finds all child elements of the specified web element using the
        specified locator strategy and waits until at least one element is
        visible.

        Parameters
        ----------
        element : WebElement
            The parent web element to find the child elements within.
        value : str
            The value to search for, such as the ID, name, or XPath of the
            child elements.
        by : str, default "id"
            The locator strategy to use, such as "id", "name", "xpath", etc.
        expected_condition : Callable, default EC.visibility_of
            The expected condition to wait for, such as the visibility of the
            child elements.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElements
            A list of all matching child elements found.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        offspring = wait.until(
            lambda elem: element.find_elements(ATTR_SELECTOR[by], value)
        )
        return offspring

    @quitonfailure
    def children_by_class_name(
        self,
        element: WebElement,
        value: str,
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Finds all child elements of the specified web element by class name and
        waits until at least one element is visible.

        Parameters
        ----------
        element : WebElement
            The parent web element to find the child elements within.
        value : str
            The class name to search for.
        expected_condition : Callable, default EC.visibility_of
            The expected condition to wait for, such as the visibility of the
            child elements.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElements
            A list of all matching child elements found by class name.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        offspring = wait.until(
            lambda elem: element.find_elements(
                ATTR_SELECTOR['class name'], value)
        )
        return offspring

    @quitonfailure
    def click_element(
        self,
        element: WebElement,
        expected_condition=EC.element_to_be_clickable,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Clicks on the specified web element after waiting for it to be
        clickable.

        Parameters
        ----------
        element : WebElement
            The web element to click on.
        expected_condition : Callable, default EC.element_to_be_clickable
            The expected condition to wait for before clicking the element.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element)).click()

    @quitonfailure
    def click(
        self,
        value: str,
        by="id",
        expected_condition_element=EC.presence_of_element_located,
        expected_condition_click=EC.element_to_be_clickable,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Finds an element on the web page using the specified locator strategy
        and waits until the element is present, then clicks on it.

        Parameters
        ----------
        value : str
            The value to search for, such as the ID, name, or XPath of the
            element.
        by : str, default "id"
            The locator strategy to use, such as "id", "name", "xpath", etc.
        expected_condition_element : Callable, default EC.presence_of_element_located  #noqa E501
            The expected condition to wait for, such as the presence of the
            element.
        expected_condition_click : Callable, default EC.element_to_be_clickable
            The expected condition to wait for before clicking the element.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        element = self.select(
            value=value,
            by=by,
            expected_condition=expected_condition_element,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )
        self.click_element(
            element,
            expected_condition=expected_condition_click,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    @quitonfailure
    def arrow_down_element(
        self,
        element: WebElement,
        n_times: int = 1,
        enter=False,
        expected_condition=EC.element_to_be_clickable,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Sends the down arrow key to the specified web element the specified
        number of times and optionally presses the Enter key.

        Parameters
        ----------
        element : WebElement
            The web element to send the down arrow key to.
        n_times : int, default 1
            The number of times to send the down arrow key.
        enter : bool, default False
            Whether to press the Enter key after sending the down arrow key.
        expected_condition : Callable, default EC.element_to_be_clickable
            The expected condition to wait for before sending the keys.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        for _ in range(n_times):
            wait.until(expected_condition(element)).send_keys(Key.down)
        if enter:
            wait.until(expected_condition(element)).send_keys(Key.enter)

    @quitonfailure
    def soup_of(
        self,
        element: WebElement,
        parser="html.parser",
        features="lxml",
        outer=True,
        **kwargs
    ):
        """
        Parses the inner or outer HTML of the specified web element using
        BeautifulSoup.

        Parameters
        ----------
        element : WebElement
            The web element to parse.
        parser : str, default "html.parser"
            The parser to use for parsing the HTML.
        features : str, default "lxml"
            The features to use for parsing the HTML.
        outer : bool, default True
            Whether to parse the outer HTML of the element. If False, the inner
            HTML is parsed.
        **kwargs : dict
            Additional keyword arguments to pass to the BeautifulSoup
            constructor.

        Returns
        -------
        BeautifulSoup
            A BeautifulSoup object representing the parsed HTML of the element.
        """
        type_attribute = "innerHTML"
        if outer:
            type_attribute = "outerHTML"

        return BeautifulSoup(
            element.get_attribute(type_attribute),
            parser=parser,
            features=features,
            **kwargs
        )

    @quitonfailure
    def run(self, script, *args):
        """
        Executes the specified JavaScript script on the web page.

        Parameters
        ----------
        script : str
            The JavaScript script to execute.
        *args : tuple
            Arguments to pass to the JavaScript script.

        Returns
        -------
        Any
            The result of the script execution.
        """
        return self.execute_script(script, *args)

    @quitonfailure
    def query_selector(self, selector: str):
        """
        Executes a JavaScript query selector on the web page and returns the
        first matching element.

        Parameters
        ----------
        selector : str
            The CSS selector to use for querying the web page.

        Returns
        -------
        WebElement
            The first matching element found by the query selector.
        """
        script = document_query_selector(selector)
        return self.run(script)

    @quitonfailure
    def query_selector_all(self, selector: str):
        """
        Executes a JavaScript query selector on the web page and returns all
        matching elements.

        Parameters
        ----------
        selector : str
            The CSS selector to use for querying the web page.

        Returns
        -------
        WebElements
            A list of all matching elements found by the query selector.
        """
        script = document_query_selector_all(selector)
        return self.run(script)

    @quitonfailure
    def dispatch_enter(self, element: WebElement):
        """
        Dispatches an 'Enter' key event to the specified web element.

        Parameters
        ----------
        element : WebElement
            The web element to dispatch the 'Enter' key event to.

        Returns
        -------
        Any
            The result of the dispatched event.
        """
        return self.run(DISPATCH_ENTER, element)

    @quitonfailure
    def dispatch_enter_selector(self, selector: str):
        """
        Dispatches an 'Enter' key event to the first element matching the
        specified CSS selector.

        Parameters
        ----------
        selector : str
            The CSS selector to use for querying the web page.

        Returns
        -------
        Any
            The result of the dispatched event.
        """
        return self.run(DISPATCH_ENTER_SELECTOR.format(selector))

    @quitonfailure
    def make_soup(self, parser="html.parser", **kwargs):
        """
        Parses the current page source using BeautifulSoup with the specified
        parser.

        Parameters
        ----------
        parser : str, default "html.parser"
            The parser to use for parsing the HTML.
        **kwargs : dict
            Additional keyword arguments to pass to the BeautifulSoup
            constructor.

        Returns
        -------
        BeautifulSoup
            A BeautifulSoup object representing the parsed HTML of the current
            page.
        """
        return BeautifulSoup(self.page_source(), parser=parser, **kwargs)

    @quitonfailure
    def make_dom(self, soup_parser="html.parser", **kwargs):
        """
        Parses the current page source using lxml with the specified parser and
        returns an ElementTree object.

        Parameters
        ----------
        soup_parser : str, default "html.parser"
            The parser to use for parsing the HTML.
        **kwargs : dict
            Additional keyword arguments to pass to the lxml HTML constructor.

        Returns
        -------
        etree.ElementTree
            An ElementTree object representing the parsed HTML of the current
            page.
        """
        self.soup = self.make_soup(parser=soup_parser)
        self.dom = etree.HTML(str(self.soup), **kwargs)
        return self.dom

    def is_display(self, element: WebElement, value: str):
        """
        Checks if the specified web element is displayed with the given display
        value.

        Parameters
        ----------
        element : WebElement
            The web element to check the display property of.
        value : str
            The display value to check against, such as "block", "none", etc.

        Returns
        -------
        bool
            True if the element is displayed with the given value, False
            otherwise.
        """
        script = is_display(value)
        return self.run(script, element)

    @quitonfailure
    def switch_to_frame(self, value: str, by='id'):
        """
        Switches the web driver's focus to the frame specified by the given
        value and locator strategy.

        Parameters
        ----------
        value : str
            The value to search for, such as the ID, name, or XPath of the frame.  # noqa E501
        by : str, default 'id'
            The locator strategy to use, such as "id", "name", "xpath", etc.

        Raises
        ------
        TimeoutException
            If the frame is not found within the specified timeout.
        """
        self.wait().until(
            EC.frame_to_be_available_and_switch_to_it(
                (by, value)
            )
        )
