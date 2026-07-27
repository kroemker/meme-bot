import re
import urllib.parse

import requests

URL_PATTERN = re.compile(r"https?://\S+")
TITLE_PATTERN = re.compile(rb"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
FETCH_TIMEOUT = 5
YOUTUBE_DOMAINS = {"youtube.com", "youtu.be", "m.youtube.com"}


class LinkResolver:
    """Replaces URLs in message text with a short human-readable description
    (e.g. a YouTube video's title) so an LLM can understand link-only posts
    instead of seeing an opaque URL. Caches by URL and caps total network
    lookups for one bot run."""

    def __init__(self, max_resolutions: int = 20):
        self._max_resolutions = max_resolutions
        self._cache: dict[str, str] = {}
        self._resolved_count = 0

    def annotate(self, text: str) -> str:
        return URL_PATTERN.sub(self._replace, text)

    def _replace(self, match: re.Match) -> str:
        url = match.group(0).rstrip(").,!?\"'")
        return self._resolve(url)

    def _resolve(self, url: str) -> str:
        if url in self._cache:
            return self._cache[url]

        domain = _domain(url)
        if self._resolved_count >= self._max_resolutions:
            annotation = f"[link: {domain}]"
        else:
            self._resolved_count += 1
            if domain in YOUTUBE_DOMAINS:
                annotation = _resolve_youtube(url, domain)
            else:
                annotation = _resolve_generic(url, domain)

        self._cache[url] = annotation
        return annotation


def _domain(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.removeprefix("www.")
    except ValueError:
        return "link"


def _resolve_youtube(url: str, domain: str) -> str:
    try:
        response = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": url, "format": "json"},
            timeout=FETCH_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        title = data.get("title")
        author = data.get("author_name")
        if title and author:
            return f'[YouTube: "{title}" by {author}]'
        if title:
            return f'[YouTube: "{title}"]'
    except (requests.RequestException, ValueError):
        pass
    return f"[link: {domain}]"


def _resolve_generic(url: str, domain: str) -> str:
    try:
        response = requests.get(
            url,
            timeout=FETCH_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (compatible; meme-bot/1.0)"},
        )
        response.raise_for_status()
        match = TITLE_PATTERN.search(response.content[:65536])
        if match:
            title = match.group(1).decode("utf-8", errors="ignore").strip()
            title = re.sub(r"\s+", " ", title)
            if title:
                return f'[link: "{title}" — {domain}]'
    except requests.RequestException:
        pass
    return f"[link: {domain}]"
