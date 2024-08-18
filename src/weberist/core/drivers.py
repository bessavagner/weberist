from typing import List, Any
from pathlib import Path

from weberist.base.drivers import BaseDriver
from weberist.generic.types import Chrome

from weberist.base.data import ProfileStorageBackend


class ChromeDriver(BaseDriver):
    
    def __init__(self,
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
        if 'profile' in kwargs:
            target_path = Path('.')
            if 'localstorage' in kwargs:
                target_path = Path(kwargs['localstorage'])
            self.profile_backend = ProfileStorageBackend(target_path)
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

    def __new__(cls,
                *args,
                options_arguments: List[str] = None,
                extensions: List[str | Path] = None,
                services_kwargs: dict[str, Any] = None,
                keep_alive: bool = True,
                remote: bool = False,
                **kwargs) -> Chrome:
        browser = 'chrome'
        if remote:
            browser = 'chrome_remote'
        experimental_options = {
            "excludeSwitches": ["enable-automation"],
            "useAutomationExtension": False
        }
        kwargs.update({"experimental_options": experimental_options})
        if 'profile' in kwargs:
            target_path = Path('.')
            if 'localstorage' in kwargs:
                target_path = Path(kwargs['localstorage'])
                if options_arguments is None:
                    options_arguments = []
                kwargs.pop('localstorage')
            options_arguments.append(
                f"--user-data-dir={target_path.absolute()}"
            )
            options_arguments.append(
                f"--profile-directory={kwargs['profile']}"
            )
            kwargs.pop('profile')
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
