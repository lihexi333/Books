import requests
import sqlite3
import time

def get_db_conn():
    conn = sqlite3.connect('database.db')
    return conn

def save_book_to_db(book):
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO books (title, authors, publisher, publishedDate, description, thumbnail, infoLink)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        book.get('title'),
        ', '.join(book.get('authors', [])),
        book.get('publisher'),
        book.get('publishedDate'),
        book.get('description'),
        book.get('imageLinks', {}).get('thumbnail'),
        book.get('infoLink')
    ))
    conn.commit()
    conn.close()

def fetch_books():
    keywords = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    books_collected = 0
    seen_titles = set()
    for kw in keywords:
        for start in range(0, 40, 10):  # 每个关键词最多取4页
            url = f'https://www.googleapis.com/books/v1/volumes?q={kw}&startIndex={start}&maxResults=10'
            resp = requests.get(url)
            if resp.status_code != 200:
                continue
            data = resp.json()
            items = data.get('items', [])
            for item in items:
                info = item.get('volumeInfo', {})
                title = info.get('title')
                if not title or title in seen_titles:
                    continue
                save_book_to_db(info)
                seen_titles.add(title)
                books_collected += 1
                print(f'已收集 {books_collected} 本: {title}')
                if books_collected >= 100:
                    return
            time.sleep(0.5)  # 防止被封IP

if __name__ == '__main__':
    fetch_books()
