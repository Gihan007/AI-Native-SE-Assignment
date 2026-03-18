"""Website scraping and metrics extraction service."""

from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from app.core.config import (
    REQUEST_TIMEOUT,
    DEFAULT_USER_AGENT,
    CTA_KEYWORDS,
    NOISY_ELEMENTS,
    ICON_FONT_CLASSES,
    NAVIGATION_KEYWORDS,
)
from app.utils.html_utils import (
    count_words,
    extract_domain_from_url,
    is_valid_href,
    normalize_domain,
)
from app.schemas.audit_schema import (
    HeadingsSchema,
    LinksSchema,
    ImagesSchema,
    MetaSchema,
    AuditResponse,
)


class ScraperService:
    """Service for scraping websites and extracting metrics."""

    CTA_UI_CONTROL_KEYWORDS = {
        "toggle",
        "menu",
        "close",
        "collapse",
        "expand",
        "pause",
        "play",
        "previous",
        "next",
        "prev",
        "open",
        "dismiss",
    }

    CTA_SOCIAL_KEYWORDS = {
        "facebook",
        "twitter",
        "linkedin",
        "instagram",
        "youtube",
        "tiktok",
        "pinterest",
        "whatsapp",
    }

    CTA_PROTECTED_PHRASES = {
        "let's talk",
        "lets talk",
        "see our work",
        "learn more",
        "learn more about our services",
        "contact us",
        "contact",
        "get started",
        "request demo",
        "take a look",
        "take a look at more of our developments",
        "book a demo",
        "book now",
        "try now",
        "sign up",
        "signup",
        "register",
        "buy now",
        "start now",
        "start free",
        "join now",
        "talk to us",
    }

    CTA_CLASS_HINTS = {
        "btn",
        "button",
        "cta",
        "action",
        "primary",
        "hero",
        "banner",
        "promo",
    }

    CTA_NEGATIVE_TEXT = {
        "home",
        "services",
        "products",
        "work",
        "careers",
        "about us",
        "blogs",
        "news",
        "privacy policy",
        "terms of service",
        "cookie policy",
        "read more",
    }

    @staticmethod
    def extract_metrics(url: str) -> AuditResponse:
        """
        Extract metrics from a website URL.

        Fetches the website, parses HTML, and extracts deterministic metrics.

        Args:
            url: The website URL to audit

        Returns:
            AuditResponse containing all extracted metrics

        Raises:
            ValueError: If URL is invalid or inaccessible
            RuntimeError: If HTML parsing fails
        """
        try:
            html = ScraperService._fetch_html(url)
            if not html:
                raise ValueError("Failed to fetch website content")

            soup = BeautifulSoup(html, "html.parser")

            ScraperService._remove_noisy_elements(soup)

            word_count = ScraperService._extract_word_count(soup)
            headings = ScraperService._extract_headings(soup)
            cta_count = ScraperService._extract_cta_count(soup)
            links = ScraperService._extract_links(soup, url)
            images = ScraperService._extract_images(soup)
            meta = ScraperService._extract_meta(soup)
            content = ScraperService._extract_visible_text(soup)

            return AuditResponse(
                url=url,
                word_count=word_count,
                headings=headings,
                cta_count=cta_count,
                links=links,
                images=images,
                meta=meta,
                content=content,
            )

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error extracting metrics: {str(e)}") from e

    @staticmethod
    def _fetch_html(url: str) -> Optional[str]:
        """
        Fetch HTML content from URL with error handling.

        Args:
            url: The URL to fetch

        Returns:
            HTML content as string

        Raises:
            ValueError: If URL is invalid or unreachable
        """
        try:
            headers = {"User-Agent": DEFAULT_USER_AGENT}
            response = requests.get(
                url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            response.raise_for_status()
            return response.text

        except requests.exceptions.Timeout:
            raise ValueError(f"Request timeout for {url}")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Connection error for {url}")
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"HTTP error {e.response.status_code} for {url}")
        except Exception as e:
            raise ValueError(f"Failed to fetch {url}: {str(e)}")

    @staticmethod
    def _remove_noisy_elements(soup: BeautifulSoup) -> None:
        """
        Remove noisy and decorative elements from HTML.

        Removes:
        - script, style, noscript, svg, canvas, video, source, etc.
        - icon-font elements by configured classes
        - aside elements

        Intentionally does NOT remove <nav> because navigation contains
        real links and possible CTA elements that should still be counted.

        Args:
            soup: BeautifulSoup object
        """
        for element in soup.find_all(NOISY_ELEMENTS):
            element.decompose()

        for class_name in ICON_FONT_CLASSES:
            for element in soup.find_all(class_=class_name):
                element.decompose()

        for element in soup.find_all(["aside"]):
            element.decompose()

    @staticmethod
    def _get_clean_text(soup: BeautifulSoup) -> str:
        """
        Extract and normalize visible text from the page.

        Args:
            soup: Parsed HTML after noisy elements are removed

        Returns:
            Clean normalized text
        """
        text = soup.get_text(separator=" ", strip=True)
        text = " ".join(text.split())
        return text

    @staticmethod
    def _extract_word_count(soup: BeautifulSoup) -> int:
        """
        Extract total word count from cleaned visible text.

        Args:
            soup: Parsed HTML

        Returns:
            Total word count
        """
        text = ScraperService._get_clean_text(soup)
        return count_words(text)

    @staticmethod
    def _extract_headings(soup: BeautifulSoup) -> HeadingsSchema:
        """
        Extract heading counts (H1, H2, H3).

        Args:
            soup: Parsed HTML

        Returns:
            HeadingsSchema with heading counts
        """
        return HeadingsSchema(
            h1=len(soup.find_all("h1")),
            h2=len(soup.find_all("h2")),
            h3=len(soup.find_all("h3")),
        )

    @staticmethod
    def _extract_cta_count(soup: BeautifulSoup) -> int:
        """
        Extract CTA count using a rule-based scoring system.

        Strategy:
        - Collect broad clickable candidates
        - Score each candidate based on structure, text, attributes, and context
        - Count candidates whose score passes the CTA threshold

        Returns:
            Total CTA count
        """
        candidates = ScraperService._collect_cta_candidates(soup)
        seen = set()
        cta_count = 0

        for element in candidates:
            text = ScraperService._get_candidate_text(element)
            href = element.get("href", "").strip().lower() if isinstance(element, Tag) else ""
            key = (
                element.name.lower() if getattr(element, "name", None) else "",
                text,
                href,
            )

            if key in seen:
                continue
            seen.add(key)

            score = ScraperService._score_cta_candidate(element)

            if score >= 5:
                cta_count += 1

        return cta_count

    @staticmethod
    def _collect_cta_candidates(soup: BeautifulSoup) -> list[Tag]:
        """
        Collect broad CTA candidates from the DOM.

        Includes:
        - button
        - a[href]
        - input[type=submit]
        - input[type=button]
        - elements with role=button
        - elements with onclick
        """
        candidates: list[Tag] = []
        seen_ids = set()

        selectors = [
            "button",
            "a[href]",
            'input[type="submit"]',
            'input[type="button"]',
            '[role="button"]',
            "[onclick]",
        ]

        for selector in selectors:
            for element in soup.select(selector):
                element_id = id(element)
                if element_id not in seen_ids:
                    seen_ids.add(element_id)
                    candidates.append(element)

        return candidates

    @staticmethod
    def _score_cta_candidate(element: Tag) -> int:
        """
        Score a clickable element for CTA likelihood.

        Returns:
            Integer CTA likelihood score
        """
        score = 0

        tag_name = (element.name or "").lower()
        text = ScraperService._get_candidate_text(element)
        href = element.get("href", "").strip().lower()
        role = element.get("role", "").strip().lower()
        input_type = element.get("type", "").strip().lower()
        class_blob = ScraperService._get_class_blob(element)
        aria_label = element.get("aria-label", "").strip().lower()
        combined_text = " ".join(part for part in [text, aria_label] if part).strip()

        in_nav = ScraperService._has_ancestor_tag(element, {"nav"})
        in_footer = ScraperService._has_ancestor_tag(element, {"footer"})
        in_form = ScraperService._has_ancestor_tag(element, {"form"})
        in_header = ScraperService._has_ancestor_tag(element, {"header"})
        in_main = ScraperService._has_ancestor_tag(element, {"main", "section"})

        # Positive structure signals
        if tag_name == "button":
            score += 3

        if tag_name == "input" and input_type in {"submit", "button"}:
            score += 3

        if role == "button":
            score += 3

        if element.get("onclick"):
            score += 2

        # Positive semantic signals
        if combined_text:
            if any(keyword in combined_text for keyword in CTA_KEYWORDS):
                score += 4

            if combined_text in ScraperService.CTA_PROTECTED_PHRASES:
                score += 4

            if 1 <= len(combined_text.split()) <= 5:
                score += 1

        # Positive styling/intent signals
        if any(hint in class_blob for hint in ScraperService.CTA_CLASS_HINTS):
            score += 2

        if in_form:
            score += 2

        if in_header or in_main:
            score += 1

        # Negative signals
        if not combined_text:
            score -= 4

        if combined_text in ScraperService.CTA_NEGATIVE_TEXT:
            score -= 4

        if combined_text in NAVIGATION_KEYWORDS and combined_text not in ScraperService.CTA_PROTECTED_PHRASES:
            score -= 4

        if any(keyword in combined_text for keyword in ScraperService.CTA_UI_CONTROL_KEYWORDS):
            score -= 4

        if href.startswith(("mailto:", "tel:", "javascript:")):
            score -= 4

        if any(platform in href for platform in ScraperService.CTA_SOCIAL_KEYWORDS):
            score -= 4

        if in_footer:
            score -= 2

        if in_nav and combined_text not in ScraperService.CTA_PROTECTED_PHRASES:
            score -= 2

        return score

    @staticmethod
    def _get_candidate_text(element: Tag) -> str:
        """
        Extract normalized candidate text from visible text or aria-label.

        Args:
            element: DOM element candidate

        Returns:
            Normalized lowercased text
        """
        text = element.get_text(" ", strip=True).lower()
        if not text:
            text = element.get("value", "").strip().lower()
        if not text:
            text = element.get("aria-label", "").strip().lower()

        return " ".join(text.split())

    @staticmethod
    def _get_class_blob(element: Tag) -> str:
        """
        Convert class/id attributes into a single normalized searchable string.
        """
        classes = element.get("class", [])
        if isinstance(classes, str):
            classes = [classes]

        element_id = element.get("id", "")
        parts = [str(c).lower() for c in classes if c]
        if element_id:
            parts.append(str(element_id).lower())

        return " ".join(parts)

    @staticmethod
    def _has_ancestor_tag(element: Tag, tag_names: set[str]) -> bool:
        """
        Check whether an element is inside one of the given ancestor tags.
        """
        current = element.parent
        while current and isinstance(current, Tag):
            if (current.name or "").lower() in tag_names:
                return True
            current = current.parent
        return False

    @staticmethod
    def _extract_links(soup: BeautifulSoup, page_url: str) -> LinksSchema:
        """
        Extract internal and external link counts.

        Counts all valid <a href> links:
        - same-domain or relative links as internal
        - different-domain links as external

        Args:
            soup: Parsed HTML
            page_url: Page URL for domain comparison

        Returns:
            LinksSchema with internal and external counts
        """
        page_domain = normalize_domain(extract_domain_from_url(page_url))
        internal_count = 0
        external_count = 0

        for link in soup.find_all("a", href=True):
            href = link.get("href", "").strip()

            if not is_valid_href(href):
                continue

            resolved_url = urljoin(page_url, href)
            link_domain = normalize_domain(extract_domain_from_url(resolved_url))

            if not link_domain or link_domain == page_domain:
                internal_count += 1
            else:
                external_count += 1

        return LinksSchema(internal=internal_count, external=external_count)

    @staticmethod
    def _extract_images(soup: BeautifulSoup) -> ImagesSchema:
        """
        Extract image metrics.

        Counts:
        - Total images
        - Images missing alt text
        - Percentage missing alt

        Args:
            soup: Parsed HTML

        Returns:
            ImagesSchema with image metrics
        """
        images = soup.find_all("img")
        total = len(images)

        if total == 0:
            return ImagesSchema(total=0, missing_alt=0, missing_alt_percent=0.0)

        missing_alt = sum(
            1
            for img in images
            if not img.get("alt") or not img.get("alt", "").strip()
        )

        missing_alt_percent = round((missing_alt / total) * 100, 2)

        return ImagesSchema(
            total=total,
            missing_alt=missing_alt,
            missing_alt_percent=missing_alt_percent,
        )

    @staticmethod
    def _extract_meta(soup: BeautifulSoup) -> MetaSchema:
        """
        Extract meta title and description.

        Args:
            soup: Parsed HTML

        Returns:
            MetaSchema with title and description
        """
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag.get("content", "") if description_tag else ""

        return MetaSchema(title=title, description=description)

    @staticmethod
    def _extract_visible_text(soup: BeautifulSoup) -> str:
        """
        Extract first 500 characters of cleaned visible text.

        Args:
            soup: Parsed HTML

        Returns:
            Visible text preview (max 500 chars)
        """
        text = ScraperService._get_clean_text(soup)
        return text[:500] + ("..." if len(text) > 500 else "")

    @staticmethod
    def _extract_headings_details(soup: BeautifulSoup) -> dict:
        """Extract heading details with text content."""
        h1_tags = soup.find_all("h1")
        h2_tags = soup.find_all("h2")
        h3_tags = soup.find_all("h3")
        
        return {
            "h1": [tag.get_text(strip=True) for tag in h1_tags],
            "h2": [tag.get_text(strip=True) for tag in h2_tags],
            "h3": [tag.get_text(strip=True) for tag in h3_tags],
        }

    @staticmethod
    def _extract_cta_details(soup: BeautifulSoup) -> list:
        """Extract CTA details with text and URLs."""
        candidates = ScraperService._collect_cta_candidates(soup)
        seen = set()
        cta_details = []

        for element in candidates:
            text = ScraperService._get_candidate_text(element)
            href = element.get("href", "").strip().lower() if isinstance(element, Tag) else ""
            key = (
                element.name.lower() if getattr(element, "name", None) else "",
                text,
                href,
            )

            if key in seen:
                continue
            seen.add(key)

            score = ScraperService._score_cta_candidate(element)

            if score >= 5:
                cta_details.append({
                    "text": text.title(),
                    "url": element.get("href", "#") if isinstance(element, Tag) else "#"
                })

        return cta_details

    @staticmethod
    def _extract_links_details(soup: BeautifulSoup, page_url: str) -> dict:
        """Extract link details with URLs."""
        page_domain = normalize_domain(extract_domain_from_url(page_url))
        internal_links = []
        external_links = []

        for link in soup.find_all("a", href=True):
            href = link.get("href", "").strip()

            if not is_valid_href(href):
                continue

            resolved_url = urljoin(page_url, href)
            link_domain = normalize_domain(extract_domain_from_url(resolved_url))

            if not link_domain or link_domain == page_domain:
                internal_links.append(resolved_url)
            else:
                external_links.append(resolved_url)

        return {
            "internal": internal_links,
            "external": external_links,
        }

    @staticmethod
    def _extract_images_details(soup: BeautifulSoup) -> dict:
        """Extract image details with URLs and alt text status."""
        images = soup.find_all("img")
        image_details = []

        for img in images:
            src = img.get("src", "")
            alt = img.get("alt", "").strip()
            has_alt = bool(alt)
            
            image_details.append({
                "src": src,
                "alt": alt if alt else "(missing)",
                "has_alt": has_alt
            })

        return {
            "images": image_details
        }