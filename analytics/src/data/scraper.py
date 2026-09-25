import requests
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_page(self, endpoint):
        response = requests.get(f"{self.base_url}{endpoint}")
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to fetch page: {response.status_code}")

    def parse_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # Example parsing logic (to be customized based on the target website)
        data = []
        for item in soup.select('.product_pod'):
            title = item.h3.a['title']
            price = float(item.select_one('.price_color').get_text(strip=True)[1:])
            data.append({'title': title, 'price': price})
        return data

    def scrape(self, endpoint=''):
        html = self.fetch_page(endpoint)
        return self.parse_data(html)