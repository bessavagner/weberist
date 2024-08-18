import logging
from logging import NullHandler
from logging.config import dictConfig

from .base.config import LOG
from .core.drivers import ChromeDriver

dictConfig(LOG)
logging.root.setLevel(logging.INFO)
# Set default logging handler to avoid \"No handler found\" warnings.
logging.getLogger(__name__).addHandler(NullHandler())

__all__ = [
    "ChromeDriver",
]
