import pandas as pd

from .scraper import Scraper
from .cleaner import preprocess_data
from .loader import DataLoader

class DataPipeline:
    def __init__(self, source_url, db_name):
        self.source_url = source_url
        self.db_name = db_name
        self.scraper = Scraper(source_url)
        self.loader = DataLoader(db_name)

    def run(self):
        raw_data = self.scraper.scrape()
        cleaned_data = preprocess_data(pd.DataFrame(raw_data))
        self.loader.save_to_csv(cleaned_data, self.db_name)

if __name__ == "__main__":
    pipeline = DataPipeline(source_url='http://example.com/data', db_name='data.db')
    pipeline.run()