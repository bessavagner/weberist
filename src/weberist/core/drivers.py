import logging
from typing import List, Any
from pathlib import Path

from weberist.base.drivers import BaseDriver
from weberist.generic.types import Chrome

from weberist.base.data import ProfileStorageBackend

logger = logging.getLogger('client')
logger.setLevel(logging.DEBUG)

class ChromeDriver(BaseDriver):
    
    def __init__(self,
                 *args,
                 options_arguments: List[str] = None,
                 extensions: List[str | Path] = None,
                 services_kwargs: dict[str, Any] = None,
                 keep_alive: bool = True,
                 quit_on_failure: bool = False,
                 timeout: int = 20,
                 remote: bool = False,
                 **kwargs) -> None:
        browser = 'chrome'
        if remote:
            browser = 'chrome_remote'
        super().__init__(
            browser=browser,
            options_arguments=options_arguments,
            extensions=extensions,
            services_kwargs=services_kwargs,
            keep_alive=keep_alive,
            quit_on_failure=quit_on_failure,
            timeout=timeout,
            **kwargs
        )
