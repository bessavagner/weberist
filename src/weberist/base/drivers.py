import os
import logging
import traceback
from abc import ABC, abstractmethod
from typing import Any, Callable, List
from pathlib import Path

from weberist.generic.types import WebDriver
from .managers import WebDriverFactory


class BaseDriver(WebDriverFactory):

    def __init__(self,
                 *args,
                 browser: str = 'chrome',
                 options_arguments: List[str] = None,
                 extensions: List[str | Path] = None,
                 services_kwargs: dict[str, Any] = None,
                 keep_alive: bool = True,
                 quit_on_failure: bool = False,
                 timeout: int = 20,
                 **kwargs) -> None:
        super().__init__(
                *args,
                browser=browser,
                options_arguments=options_arguments,
                extensions=extensions,
                services_kwargs=services_kwargs,
                keep_alive=keep_alive,
                **kwargs
        )
        self._quit_on_failure = quit_on_failure
        self.timeout = timeout

    def __new__(cls,
                *args,
                browser: str = 'chrome',
                options_arguments: List[str] = None,
                extensions: List[str | Path] = None,
                services_kwargs: dict[str, Any] = None,
                keep_alive: bool = True,
                **kwargs) -> WebDriver:
        return super().__new__(
            cls,
            *args,
            browser=browser,
            options_arguments=options_arguments,
            extensions=extensions,
            services_kwargs=services_kwargs,
            keep_alive=keep_alive,
            **kwargs
        )
