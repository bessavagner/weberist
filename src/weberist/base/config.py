"""Configurations for development and maintenance"""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / 'data'
DOCKER_DIR = ROOT_DIR / 'docker'
LOCALSTORAGE = DATA_DIR / 'localstorage'
DOCKER_CHROME_LOCALSTORAGE = ROOT_DIR / 'localstorage'
CHROME_EXTENSIONS = DATA_DIR / 'extensions/chrome'
DOCKER_FILE_BROWSER = DOCKER_DIR / 'Dockerfile'
DOCKER_FILE_CHROME = DOCKER_DIR / 'Dockerfile-chrome'
BROWSER_IMAGE = 'weberist-{browser}_{version}.0'
CHROME_IMAGE = 'weberist-chrome_{version}.0'
DOCKER_COMPOSE = 'docker-compose.yml'
DOCKER_NETWORK = 'weberist'
CONTAINER_SELENOID = 'weberist-selenoid'
CONTAINER_SELENOID_UI = 'weberist-selenoid-ui'
DEFAULT_PROFILE = 'Profile 1'
CHROME_VERSIONS = tuple(str(i) for i in range(48, 128))
FIREFOX_VERSIONS = tuple(str(i) for i in range(4, 125))

BROWSER_DICT = {
    "image": None,
    "port": 4444,
    "tmpfs": {
        "/tmp": "size=512m",
        "/var": "size=128m",
    },
    "path": "/"
}

LOG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "client": {
            "format": (
                "%(levelname)s (%(filename)s at line %(lineno)d): %(message)s"
            )
        },
        "standard": {
            "format": (
                "%(levelname)s (%(funcName)s): %(message)s"
                "\n\t├─file: %(pathname)s"
                "\n\t╰─line: %(lineno)d"
            )
        },
        "debug": {
            "format": (
                "%(asctime)s %(levelname)s (at %(funcName)s "
                "in line %(lineno)d):"
                "\n\t├─file: %(pathname)s"
                "\n\t├─task name: %(taskName)s"
                "\n\t╰─message: %(message)s\n"
            ),
            "datefmt": "%y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "client": {
            "class": "logging.StreamHandler",
            "formatter": "client",
        },
        "standard": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "debug": {
            "class": "logging.StreamHandler",
            "formatter": "debug",
        }
    },
    "loggers": {
        "": {"handlers": ["client"], "level": "DEBUG"},
        "standard": {
            "handlers": ["standard"],
            "level": "DEBUG",
            "propagate": False,
        },
        "debugger": {
            "handlers": ["debug"],
            "level": "DEBUG",
            "propagate": False,
        }
    }
}