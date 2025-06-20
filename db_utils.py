import sqlite3
import os
from flask import current_app, g
from werkzeug.security import generate_password_hash

def get_db_conn():
    if 'db' not in g:
        # 确保我们使用的是实例文件夹中的数据库路径
        db_path = current_app.config['DATABASE']
        # 确保数据库所在的目录存在
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db_conn()


    with current_app.open_resource('db.sql') as f:
        db.executescript(f.read().decode('utf8'))
    
    # 插入管理员账号（用户名：管理员，密码：111，邮箱：admin@example.com，is_admin=1）
    db.execute(
        "INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)",
        ('管理员', generate_password_hash('111'), 'admin@example.com', 1)
    )

    # 先插入一个测试用户
    db.execute(
        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
        ('testuser', generate_password_hash('111'), 'testuser@example.com')
    )

    # 再插入两条博客，user_id=1
    db.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", ('学习Flask1', '第一条实例', 1))
    db.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", ('学习Flask2', '第二条示例', 1))

    # 可选：插入一条测试书籍
    db.execute("INSERT INTO books (title, authors, publisher, publishedDate, description, thumbnail, infoLink) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ('测试书籍', '测试作者', '测试出版社', '2024-01-01', '这是一本测试书籍', '', ''))


    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)

def get_post(post_id):
    conn = get_db_conn()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    return post

def get_user_by_username(username):
    conn = get_db_conn()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    return user

def get_user_by_id(user_id):
    db = get_db_conn()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    return user

def get_markdown_by_user_id(user_id):
    """根据用户ID获取其Markdown内容"""
    db = get_db_conn()
    markdown = db.execute(
        'SELECT content FROM user_markdown WHERE user_id = ?', (user_id,)
    ).fetchone()
    return markdown

def save_markdown(user_id, content):
    """为用户保存（插入或更新）Markdown内容"""
    db = get_db_conn()
    user_md = db.execute(
        'SELECT id FROM user_markdown WHERE user_id = ?', (user_id,)
    ).fetchone()

    if user_md:
        db.execute(
            'UPDATE user_markdown SET content = ? WHERE user_id = ?', (content, user_id)
        )
    else:
        db.execute(
            'INSERT INTO user_markdown (user_id, content) VALUES (?, ?)',
            (user_id, content)
        )
    db.commit()

def save_book_to_db(book):
    """将单本图书信息保存到数据库，如果标题已存在则忽略"""
    conn = get_db_conn()
    
    # 检查标题是否已存在
    existing = conn.execute('SELECT id FROM books WHERE title = ?', (book.get('title'),)).fetchone()
    if existing:
        return

    conn.execute('''
        INSERT INTO books (title, authors, publisher, publishedDate, description, thumbnail, infoLink)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        book.get('title'),
        ', '.join(book.get('authors', [])) if book.get('authors') else None,
        book.get('publisher'),
        book.get('publishedDate'),
        book.get('description'),
        book.get('imageLinks', {}).get('thumbnail'),
        book.get('infoLink')
    ))
    conn.commit()

def fetch_books_from_api():
    """从Google Books API获取图书并存入数据库"""
    import requests
    import time

    keywords = ['python', 'java', 'flask', 'django', 'javascript', 'html', 'css', 'sql', 'docker', 'linux']
    books_collected = 0
    
    conn = get_db_conn()
    existing_titles_rows = conn.execute('SELECT title FROM books').fetchall()
    seen_titles = {row['title'] for row in existing_titles_rows}
    
    print("开始从Google Books API获取图书...")

    for kw in keywords:
        if books_collected >= 100:
            break
        for start in range(0, 40, 10):
            if books_collected >= 100:
                break
            
            url = f'https://www.googleapis.com/books/v1/volumes?q={kw}&startIndex={start}&maxResults=10'
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                items = data.get('items', [])
            except requests.exceptions.RequestException as e:
                print(f"请求API时出错: {e}")
                continue
            
            for item in items:
                if books_collected >= 100:
                    break
                info = item.get('volumeInfo', {})
                title = info.get('title')
                
                if not title or title in seen_titles:
                    continue
                
                # 创建一个 book 字典传递给 save_book_to_db
                book_data = {
                    'title': title,
                    'authors': info.get('authors', []),
                    'publisher': info.get('publisher'),
                    'publishedDate': info.get('publishedDate'),
                    'description': info.get('description'),
                    'imageLinks': info.get('imageLinks', {}),
                    'infoLink': info.get('infoLink')
                }
                save_book_to_db(book_data) # 使用 save_book_to_db 函数
                seen_titles.add(title)
                books_collected += 1
                print(f'已收集 {books_collected}/100 本: {title}')

            time.sleep(1)

    print(f"\n图书收集完成, 共收集 {books_collected} 本.")