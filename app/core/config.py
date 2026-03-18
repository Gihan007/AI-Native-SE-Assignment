"""Configuration constants for the application."""

import os

# Request configuration
REQUEST_TIMEOUT = 10
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

# Logging configuration
AUDIT_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "audit_logs.jsonl")

# CTA keywords for detection (case-insensitive)
CTA_KEYWORDS = {
    "contact",
    "buy",
    "book",
    "call",
    "start",
    "get started",
    "sign up",
    "signup",
    "register",
    "learn more",
    "request demo",
    "try now",
}

# HTML elements to remove before text extraction
NOISY_ELEMENTS = {
    "script",
    "style",
    "noscript",
    "svg",
    "canvas",
    "video",
    "source",
}

# CSS classes commonly used for icon fonts (to exclude from text)
ICON_FONT_CLASSES = {
    "material-symbols-rounded",
    "material-icons",
    "fas",
    "far",
    "fal",
    "fab",
}

# Navigation anchor text patterns to exclude from CTA counting
NAVIGATION_KEYWORDS = {
    "home",
    "services",
    "about",
    "about us",
    "blog",
    "blogs",
    "careers",
    "team",
    "contact us",
    "faq",
    "privacy",
    "terms",
    "policy",
}
