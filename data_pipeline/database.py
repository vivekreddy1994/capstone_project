import sqlite3

class Database:
    def __init__(self, db_name='books.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                star_rating TEXT NOT NULL,
                availability TEXT NOT NULL,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        self.connection.commit()

    def close(self):
        self.connection.close()


def create_database(db_name='books.db'):
    database = Database(db_name)
    database.close()


def insert_books(db_name, books):
    database = Database(db_name)
    try:
        for book in books:
            database.cursor.execute(
                'INSERT OR IGNORE INTO categories (name) VALUES (?)',
                (book['category'],),
            )
            database.cursor.execute(
                'SELECT id FROM categories WHERE name = ?',
                (book['category'],),
            )
            category_id = database.cursor.fetchone()[0]
            database.cursor.execute(
                '''INSERT INTO books
                   (title, price, star_rating, availability, category_id)
                   VALUES (?, ?, ?, ?, ?)''',
                (
                    book['title'],
                    book['price'],
                    book['star_rating'],
                    book['availability'],
                    category_id,
                ),
            )
        database.connection.commit()
    finally:
        database.close()


def load_books_to_db(books, db_name='books.db'):
    insert_books(db_name, books)