import sqlite3
import pandas as pd


class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        return pd.read_csv(self.file_path)

    def save_to_database(self, data, db_connection):
        data.to_sql('analytics_data', db_connection, if_exists='replace', index=False)

    def save_to_csv(self, data, output_path):
        data.to_csv(output_path, index=False)