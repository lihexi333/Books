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

    with current_app.open_resource('db.sql', mode='r', encoding='utf-8') as f:
        db.executescript(f.read())
    
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