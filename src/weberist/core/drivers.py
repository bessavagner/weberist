import logging
from typing import List, Any, Dict
from pathlib import Path

from weberist.base.drivers import BaseDriver
from weberist.base.config import LOCALSTORAGE
from weberist.generic.types import WebDriver

from weberist.base.data import ProfileStorageBackend

logger = logging.getLogger('client')
logger.setLevel(logging.DEBUG)

class ChromeDriver(BaseDriver):
    
    def __new__(cls,
                *args,
                option_arguments: List[str] = None,
                services_kwargs: dict[str, Any] = None,
                keep_alive: bool = True,
                extensions: List[str | Path] = None,
                capabilities: Dict = None,
                quit_on_failure: bool = False,
                timeout: int = 20,
                remote: bool = False,
                **kwargs,) -> BaseDriver:
        
        browser = 'chrome'
        if remote:
            browser = 'chrome_remote'

        if 'stealth' in kwargs:
            kwargs['profile'] = kwargs.get('profile', 'Profile 1')
            kwargs['localstorage'] = kwargs.get('localstorage', LOCALSTORAGE)
        profile = kwargs.get('profile', None)
        localstorage = kwargs.get('localstorage', None)
        
        instance = super().__new__(
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
        
        super().__init__(
            instance,
            quit_on_failure=quit_on_failure,
            timeout=timeout,
            profile=profile,
            localstorage=localstorage,
        )
        return instance

    def execute_cdp_cmd(self: WebDriver, cmd: str, cmd_args: dict):
        """
        Method copied from selenium.webdriver.chromium.webdriver.ChromiumDriver
        This is necessary in case of remote=True at consctructor, since in this
        case self will be instance of 
        selenium.webdriver.remote.webdriver.WebDriver which does not have it
        implemented.
        
        Execute Chrome Devtools Protocol command and get returned result The
        command and command args should follow chrome devtools protocol
        domains/commands, refer to link
        https://chromedevtools.github.io/devtools-protocol/

        :Args:
         - cmd: A str, command name
         - cmd_args: A dict, command args. empty dict {} if there is no
         command args
        :Usage:
            ::

                driver.execute_cdp_cmd(
                    'Network.getResponseBody', {'requestId': requestId}
                )
        :Returns:
            A dict, empty dict {} if there is no result to return.
            For example to getResponseBody:
            {'base64Encoded': False, 'body': 'response body string'}
        """
        return self.execute("executeCdpCommand", {"cmd": cmd, "params": cmd_args})["value"]

    def change_download_dir(self, path: str | Path):
        params = {
            "behavior": "allow",
            "downloadPath": str(path)
        }
        self.execute_cdp_cmd("Page.setDownloadBehavior", params)
