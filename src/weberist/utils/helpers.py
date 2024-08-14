from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# lower casing
class Key(Keys):  # pylint: disable=too-few-public-methods
    """ "keys to use in send functions"""

    enter = Keys.RETURN
    esc = Keys.ESCAPE
    delete = Keys.DELETE
    down = Keys.ARROW_DOWN
    up = Keys.ARROW_UP
    tab = Keys.TAB
    backspace = Keys.BACK_SPACE
    shift = Keys.SHIFT
    left_shift = Keys.LEFT_SHIFT
    control = Keys.CONTROL
    left_control = Keys.LEFT_CONTROL
    alt = Keys.ALT
    left_alt = Keys.LEFT_ALT
    pause = Keys.PAUSE
    space = Keys.SPACE
    page_up = Keys.PAGE_UP
    page_down = Keys.PAGE_DOWN
    end = Keys.END
    home = Keys.HOME
    left = Keys.LEFT
    right = Keys.RIGHT
    insert = Keys.INSERT
    semicolon = Keys.SEMICOLON
    equals = Keys.EQUALS
    numpad0 = Keys.NUMPAD0
    numpad1 = Keys.NUMPAD1
    numpad2 = Keys.NUMPAD2
    numpad3 = Keys.NUMPAD3
    numpad4 = Keys.NUMPAD4
    numpad5 = Keys.NUMPAD5
    numpad6 = Keys.NUMPAD6
    numpad7 = Keys.NUMPAD7
    numpad8 = Keys.NUMPAD8
    numpad9 = Keys.NUMPAD9
    multiply = Keys.MULTIPLY
    add = Keys.ADD
    separator = Keys.SEPARATOR
    subtract = Keys.SUBTRACT
    decimal = Keys.DECIMAL
    divide = Keys.DIVIDE
    f1 = Keys.F1
    f2 = Keys.F2
    f3 = Keys.F3
    f4 = Keys.F4
    f5 = Keys.F5
    f6 = Keys.F6
    f7 = Keys.F7
    f8 = Keys.F8
    f9 = Keys.F9
    f10 = Keys.F10
    f11 = Keys.F11
    f12 = Keys.F12
    meta = Keys.META
    command = Keys.COMMAND
    zenkaku_hankaku = Keys.ZENKAKU_HANKAKU


class SelectorType(By):
    """Set of supported locator strategies."""

    id = By.ID
    xpath = By.XPATH
    link_text = By.LINK_TEXT
    partial_link_text = By.PARTIAL_LINK_TEXT
    name = By.NAME
    tag_name = By.TAG_NAME
    class_name = By.CLASS_NAME
    css_selector = By.CSS_SELECTOR
