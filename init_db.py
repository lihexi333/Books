import sqlite3

conn = sqlite3.connect('database.db')       #若没有，默认创建；然后再用conn连接上数据库，之后数据库操作都由conn来完成
cur = conn.cursor()

with open("db.sql", encoding="utf-8") as f:
    #执行脚本
    conn.executescript(f.read())

    #先插入一个测试用户
    cur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", ('testuser', 'testpass', 'testuser@example.com'))

    #再插入两条博客，user_id=1
    cur.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", ('学习Flask1', '第一条实例', 1))
    cur.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", ('学习Flask2', '第二条示例', 1))

    # 可选：插入一条测试书籍
    cur.execute("INSERT INTO books (title, authors, publisher, publishedDate, description, thumbnail, infoLink) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ('测试书籍', '测试作者', '测试出版社', '2024-01-01', '这是一本测试书籍', '', ''))

    conn.commit()
    conn.close()
    print("数据库初始化完成！")
