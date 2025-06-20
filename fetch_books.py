import requests
import sqlite3
import time

def get_db_conn():
    conn = sqlite3.connect('database.db')
    return conn



if __name__ == '__main__':
    fetch_books()
