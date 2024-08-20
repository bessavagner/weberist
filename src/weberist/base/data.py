import json
import platform
from os import name
from pathlib import Path
from copy import deepcopy
from itertools import cycle
from datetime import datetime
from random import choice, shuffle
from typing import Any, List, Optional, Dict

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
        self.data = self.get_data()
        self.set_data(self.data)

    def get_data(self) -> List[Any]:
        """Abstract method to get data. Should be overridden in subclass."""
        raise NotImplementedError

    @property
    def has_items(self) -> bool:
        return bool(self.data)

    def set_data(self, data: List[Any]) -> None:
        """Initialize or reset data and its cycled version."""
        self.data = data
        shuffled_data = list(data)
        shuffle(shuffled_data)
        self.cycled_data = cycle(shuffled_data)

    def get_random_cycled(self) -> Optional[Any]:
        """Get a random item from cycled data."""
        if self.has_items:
            return next(self.cycled_data)
        return None

    def get_random(self) -> Any:
        """Get a random item from data."""
        return choice(self.data)

    def remove_data(self, item: Any) -> None:
        """Remove an item from data and reset the cycled data."""
        self.data = [d for d in self.data if d != item]
        self.set_data(self.data)

    def get_hashed(self, value: Optional[Any]) -> Any:
        """Get a data item based on a hashed value."""
        if value is None:
            value = "_"
        hashed_value = hash(value)
        return self.data[hashed_value % len(self.data)]

    def get_n(self, n: int) -> List[Any]:
        """Get a list of n random cycled items."""
        return [self.get_random_cycled() for _ in range(n)]

    def get_hundred(self) -> List[Any]:
        """Get a list of 100 random cycled items."""
        return self.get_n(100)


def get_correct_agent(windows: str, mac: str, linux: str) -> str:
    """Selects the correct user agent based on the operating system."""
    if name == 'nt':
        return windows
    elif platform == "darwin":
        return mac
    return linux

def generate_user_agents(start_version: int,
                         end_version: int) -> Dict[str, str]:
    """Generates a dictionary of user agents for versions in the specified range."""
    return {
        str(version): get_correct_agent(
            f"Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36",
            f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36",
            f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36",
        )
        for version in range(start_version, end_version + 1)
    }


class UserAgent(BaseData):
    
    REAL = "REAL"
    RANDOM = "RANDOM"
    HASHED = "HASHED"

    GOOGLE_BOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    
    # Use dynamically generated user agents
    USER_AGENTS = generate_user_agents(98, 127)
    FREQUENCIES = {str(version): 1 for version in range(98, 128)}
    FREQUENCIES.update(
        {
            "127": 42,
            "126": 22, "125": 18, "124": 31, "123": 26,
            "122": 22, "121": 18, "120": 31, "119": 26,
            "118": 42, "117": 10, "116": 10, "115": 5,
            "114": 15, "113": 28, "112": 11, "111": 5,
            "110": 28, "109": 42, "108": 22, "107": 12,
            "106": 27, "105": 32, "104": 2, "103": 2,
            "102": 5, "101": 8, "100": 12,
            "99": 3, "98": 2
        }
    )

    def get_data(self) -> List[str]:
        """Returns a list of user agents based on predefined versions and their frequencies."""
        return [
            agent
            for version, count in self.FREQUENCIES.items()
            for agent in [self.USER_AGENTS[version]] * count
        ]


class WindowSize(BaseData):

    RANDOM = "RANDOM"
    HASHED = "HASHED"

    window_size_1920_1080 = [1920, 1080, ]
    window_size_1366_768 = [1366, 768, ]
    window_size_1536_864 = [1536, 864, ]
    window_size_1280_720 = [1280, 720, ]
    window_size_1440_900 = [1440, 900, ]
    window_size_1600_900 = [1600, 900, ]

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
    
    def to_string(self, window_size):
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
