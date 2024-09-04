import logging
from typing import List, Any, Dict
from pathlib import Path

from weberist.base.drivers import BaseDriver
from weberist.generic.types import Chrome

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
                **kwargs,):
        
        browser = 'chrome'
        if remote:
            browser = 'chrome_remote'
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
