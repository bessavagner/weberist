import sys

from weberist.utils.helpers import SelectorType
from weberist.base.config import CHROME_VERSIONS, FIREFOX_VERSIONS

OPERATING_SYSTEM = sys.platform

DISPLAY_VALUES = (
    'none',
    'inline',
    'block',
    'inline-block'
)

# used in arguments of WeElement selectors
ATTR_SELECTOR = {
    "id": SelectorType.ID,
    "name": SelectorType.NAME,
    "xpath": SelectorType.XPATH,
    "tag name": SelectorType.TAG_NAME,
    "link text": SelectorType.LINK_TEXT,
    "class name": SelectorType.CLASS_NAME,
    "css selector": SelectorType.CSS_SELECTOR,
    "partial link text": SelectorType.PARTIAL_LINK_TEXT,
}

SUPPORTED_BROWSERS: tuple[str] = (
    "chrome",
    "firefox",
    "safari",
    "edge"
)

BROWSERS_VERSIONS = {
    SUPPORTED_BROWSERS[0]: CHROME_VERSIONS,
    SUPPORTED_BROWSERS[1]: FIREFOX_VERSIONS,
}

SELENOID_CAPABILITIES = {
    "browserName": "chrome",
    "browserVersion": f"chrome_{CHROME_VERSIONS[-1]}.0",
    "selenoid:options": {
        "enableVideo": False,
        "enableVNC": True,
    }
}

DEFAULT_ARGUMENTS = {
    SUPPORTED_BROWSERS[0]: (
        "--start-maximized",
        "--no-first-run",
        "--disable-site-isolation-trials",
        "--disable-blink-features=AutomationControlled",
        "--disable-backgrounding-occluded-windows",
        "--disable-hang-monitor",
        "--metrics-recording-only",
        "--disable-sync",
        "--disable-background-timer-throttling",
        "--disable-prompt-on-repost",
        "--disable-background-networking",
        "--disable-infobars",
        "--remote-allow-origins=*",
        "--homepage=about:blank",
        "--no-service-autorun",
        "--disable-ipc-flooding-protection",
        "--disable-session-crashed-bubble",
        "--force-fieldtrials=*BackgroundTracing/default/",
        "--disable-breakpad",
        "--password-store=basic",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-features=PrivacySandboxSettings4",
        "--disable-client-side-phishing-detection",
        "--use-mock-keychain",
        "--no-pings",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-popup-blocking",
        "--disable-renderer-backgrounding",
        "--disable-component-update",
        "--disable-dev-shm-usage",
        "--disable-default-apps",
        "--disable-domain-reliability",
        "--no-default-browser-check",
    ),
}

LANGUAGES = {
    'en': ["en-US", "en"],
    'pt': ["pt-BR", "pt"],
}
