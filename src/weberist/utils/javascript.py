"""
    shelob.core.adapters



    This module should provide adapter functions for Crawlers objects.
    # TODO:
        - add more javascript adapters;
        - complete documentation;
"""

import logging

from weberist.generic.types import WebElement
from weberist.generic.constants import DISPLAY_VALUES


logger = logging.getLogger('standard')


DISPATCH_ENTER = """var ke = new KeyboardEvent('keydown', {
    bubbles: true, cancelable: true, keyCode: 13
});
arguments[0].dispatchEvent(ke);
"""
DISPATCH_ENTER_SELECTOR = (
    "var ke = new KeyboardEvent('keydown', {{"
    "   bubbles: true, cancelable: true, keyCode: 13"
    "}});"
    "{}.dispatchEvent(ke);"
)




def selector(value, by) -> dict[str, str]:
    return {
        "value": value,
        "by": by
    }

def document_query_selector(selector_str: str) -> str:
    """String to parse javascript code."""
    return f"return document.querySelector('{selector_str}');"


def document_query_selector_all(selector_str: str) -> str:
    """String to parse javascript code."""
    return f"return document.querySelectorAll('{selector_str}');"


def document_query_selector_click(selector_str: str) -> str:
    """String to parse javascript code."""
    element = document_query_selector(selector_str=selector_str)
    return (
        f"const element = {element};"
        "element.click();"
        "return element;"
    )

def is_display(
        value: str, element: WebElement = None
) -> str | tuple[str, WebElement]:
    if value not in DISPLAY_VALUES:
        raise ValueError(
            f'Invalid display value "{value}". Valid are {DISPLAY_VALUES}.'
        )
    script = f"return arguments[0].style.display == '{value}';"
    if WebElement is None:
        return script
    return script, element
