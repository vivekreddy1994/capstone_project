from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

try:
    from .config import BASE_URL, MAX_PAGES, TIMEOUT
except ImportError:
    from config import BASE_URL, MAX_PAGES, TIMEOUT

RATING_WORDS = {"One", "Two", "Three", "Four", "Five"}


def _soup(url):
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def _category_for_book(book_url):
    try:
        detail = _soup(book_url)
        category = detail.select("ul.breadcrumb li a")[-1]
        return category.get_text(strip=True)
    except (IndexError, AttributeError, requests.RequestException):
        return "Unknown"


def scrape_books(url):
    soup = _soup(url)
    books = []
    for book in soup.select("article.product_pod"):
        relative_url = book.select_one("h3 a")["href"]
        book_url = urljoin(url, relative_url)
        rating_classes = book.select_one("p.star-rating").get("class", [])
        star_rating = next((value for value in rating_classes if value in RATING_WORDS), "Unknown")
        books.append({
            "title": book.select_one("h3 a").get("title", "").strip(),
            "price": book.select_one(".price_color").get_text(strip=True),
            "star_rating": star_rating,
            "availability": book.select_one(".availability").get_text(" ", strip=True),
            "category": _category_for_book(book_url),
        })
    return books


def scrape_all_books(base_url=BASE_URL, pages=MAX_PAGES):
    all_books = []
    for page in range(1, pages + 1):
        all_books.extend(scrape_books(f"{base_url}/catalogue/page-{page}.html"))
    return all_books


def extract_books(base_url=BASE_URL, pages=MAX_PAGES):
    return scrape_all_books(base_url, pages)
