import sys

from weberist.utils.helpers import SelectorType

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
    "firefox",
    "chrome",
    "safari",
    "edge"
)

DEFAULT_ARGUMENTS = {
    SUPPORTED_BROWSERS[1]: (
        "--start-maximized",
        "--no-first-run",
        # "--disable-site-isolation-trials",
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
        "--disable-client-side-phishing-detection",
        "--use-mock-keychain",
        "--no-pings",
        "--disable-renderer-backgrounding",
        "--disable-component-update",
        "--disable-dev-shm-usage",
        "--disable-default-apps",
        "--disable-domain-reliability",
        "--no-default-browser-check",
        "--disable-features=PrivacySandboxSettings4"
    ),
}
