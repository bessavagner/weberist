import json
from typing import Any
from pathlib import Path
from copy import deepcopy
from itertools import cycle
from datetime import datetime
from random import choice, shuffle

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def copy_list(original_list):
    """
    Returns a deep copy of a list containing dictionaries or strings.

    Args:
    original_list (list): The list to copy.

    Returns:
    list: A deep copy of the original list.
    """
    return deepcopy(original_list)


def delete_from_list(list_of_dicts, dict_item):
    """
    Removes all occurrences of dict_item from list_of_dicts.

    Args:
    list_of_dicts (list): List of dictionaries or strings.
    dict_item (dict or str): Item to remove from the list.

    Returns:
    list: List with dict_item removed.
    """
    return [item for item in list_of_dicts if item != dict_item]


def datetime_to_str(when):

    return when.isoformat()


# https://stackoverflow.com/questions/27522626/hash-function-in-python-3-3-returns-different-results-between-sessions
def hash_string(text: str) -> int:
    """
    Custom hash function for strings.

    Args:
    text (str): Input string.

    Returns:
    int: Hashed integer value.
    """
    hash_value = 0
    for ch in text:
        hash_value = (hash_value * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
    return hash_value


class BaseData:
    def __init__(self):
        self.has_initialized = True
        data = self.get_data()
        self.set_data(data)

    def get_data(self):
        """Abstract method to get data. Should be overridden in subclass."""
        raise NotImplementedError

    @property
    def has_items(self):
        return len(self.data) > 0

    def set_data(self, data):
        self.data = data
        copied_list = copy_list(self.data)
        shuffle(copied_list)
        self.cycled_data = cycle(copied_list)

    def get_random_cycled(self):
        if self.has_items:
            return next(self.cycled_data)

    def get_random(self):
        return choice(self.data)

    def remove_data(self, item):
        self.set_data(delete_from_list(self.data, item))

    def get_hashed(self, value):
        if value is None:
            value = "_"
        hashed_value = hash_string(value)
        return self.data[hashed_value % len(self.data)]

    def get_n(self, n):
        return [self.get_random_cycled() for _ in range(n)]

    def get_hundred(self):
        return self.get_n(100)


import platform


def get_correct_agent(windows, mac, linux):
    """
    Returns the user agent string based on the operating system.

    Args:
    windows (str): User agent string for Windows.
    mac (str): User agent string for Mac.
    linux (str): User agent string for Linux.

    Returns:
    str: User agent string based on the current operating system.
    """
    system = platform.system().lower()
    if system == "windows":
        return windows
    elif system == "darwin":
        return mac
    return linux


class UserAgent(BaseData):
    REAL = "REAL"
    RANDOM = "RANDOM"
    HASHED = "HASHED"

    google_bot = (
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    )

    user_agents = {
        "106": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.37",
        "105": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "104": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36",
        "103": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
        "101": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951 Safari/537.36",
        "100": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896 Safari/537.36",
        "99": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844 Safari/537.36",
        "98": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758 Safari/537.36",
        "97": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692 Safari/537.36",
        "96": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664 Safari/537.36",
        "95": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638 Safari/537.36",
        "94": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606 Safari/537.36",
    }

    versions = {
        "106": 37,
        "105": 42,
        "104": 2,
        "103": 2,
        "101": 1,
        "99": 10,
        "100": 1,
        "98": 1,
        "97": 1,
        "96": 1,
        "95": 1,
        "94": 1,
    }

    def get_data(self):
        result = []
        for version, count in self.versions.items():
            user_agent = get_correct_agent(
                self.user_agents[version],
                self.user_agents[version].replace(
                    "Windows NT 10.0", "Macintosh; Intel Mac OS X 10_15"
                ),
                self.user_agents[version].replace(
                    "Windows NT 10.0", "X11; Linux x86_64"
                ),
            )
            result.extend([user_agent] * count)
        return result


class WindowSize(BaseData):

    RANDOM = "RANDOM"
    HASHED = "HASHED"

    window_size_1920_1080 = [1920, 1080, ]
    window_size_1366_768 =  [1366, 768, ]
    window_size_1536_864 =  [1536, 864, ]
    window_size_1280_720 =  [1280, 720, ]
    window_size_1440_900 =  [1440, 900, ]
    window_size_1600_900 =  [1600, 900, ]

    def get_data(self):

        # Windows
        N_1920_1080 = 35
        N_1366_768 = 26
        N_1536_864 = 16
        N_1280_720 = 9
        N_1440_900 = 9
        N_1600_900 = 5
        _1920_1080 = [self.window_size_1920_1080] * N_1920_1080
        _1366_768 = [self.window_size_1366_768] * N_1366_768
        _1536_864 = [self.window_size_1536_864] * N_1536_864
        _1280_720 = [self.window_size_1280_720] * N_1280_720
        _1440_900 = [self.window_size_1440_900] * N_1440_900
        _1600_900 = [self.window_size_1600_900] * N_1600_900

        result = _1920_1080 + _1366_768 + _1536_864 + _1280_720 + _1440_900 + _1600_900
        return result
    
    def window_size_to_string(window_size):
        width, height = window_size 
        return f'{width},{height}'



class JSONStorageBackend:
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(".")
        self.json_path = self.base_path / "profiles.json"
        self.json_data = {}
        self.refresh()

    def refresh(self):
        if not self.json_path.is_file():
            self.commit_to_disk()

        with self.json_path.open("r") as json_file:
            self.json_data = json.load(json_file)

    def commit_to_disk(self):
        with self.json_path.open("w") as json_file:
            json.dump(self.json_data, json_file, indent=4)

    def get_item(self, key: str, default=None) -> Any:
        return self.json_data.get(key, default)

    def items(self):
        return self.json_data

    def set_item(self, key: str, value: Any) -> None:
        if "created_at" not in value:
            value["created_at"] = datetime_to_str(datetime.now())

        value["updated_at"] = datetime_to_str(datetime.now())

        self.json_data[key] = {"profile_id": key, **value}
        self.commit_to_disk()

    def remove_item(self, key: str) -> None:
        if key in self.json_data:
            self.json_data.pop(key)
            self.commit_to_disk()

    def clear(self) -> None:
        if self.json_path.is_file():
            self.json_path.unlink()
        self.json_data = {}
        self.commit_to_disk()


class ProfileStorageBackend(JSONStorageBackend):
    def __init__(self, base_path: Path = None):
        super().__init__(base_path)

    def get_profile(self, profile_name: str, default=None) -> Any:
        return self.get_item(profile_name, default)

    def set_profile(self, profile_name: str, profile_data: Any) -> None:
        profile_data["updated_at"] = datetime_to_str(datetime.now())
        self.set_item(profile_name, profile_data)

    def remove_profile(self, profile_name: str) -> None:
        self.remove_item(profile_name)

    def clear(self) -> None:
        super().clear()
