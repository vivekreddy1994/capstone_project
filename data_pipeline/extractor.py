import requests
from bs4 import BeautifulSoup
try:
    from .config import BASE_URL, MAX_PAGES, TIMEOUT
except ImportError:
    from config import BASE_URL, MAX_PAGES, TIMEOUT

def scrape_books(url):
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()  # Raise an error for bad responses
    soup = BeautifulSoup(response.text, 'html.parser')
    
    books = []
    for book in soup.select('.product_pod'):
        title = book.h3.a['title']
        price = book.select_one('.price_color').text[1:]  # Remove the currency symbol
        star_rating = book.p['class'][1]  # e.g., 'star-rating Three'
        availability = book.select_one('.instock.availability').text.strip()
        category = soup.select_one('ul.breadcrumb li:nth-of-type(3) a').text  # Extract category from breadcrumb
        
        books.append({
            'title': title,
            'price': float(price),
            'star_rating': star_rating,
            'availability': availability,
            'category': category
        })
    
    return books

def scrape_all_books(base_url, pages=1):
    all_books = []
    for page in range(1, pages + 1):
        url = f"{base_url}/catalogue/page-{page}.html"
        all_books.extend(scrape_books(url))
    return all_books


def extract_books(base_url=BASE_URL, pages=MAX_PAGES):
    return scrape_all_books(base_url, pages)