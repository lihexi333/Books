from urllib import request
import requests
import smtplib
from email.mime.text import MIMEText
import random
import time

from flask import Flask, render_template, request, url_for, flash, redirect, session, g, send_file, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import markdown as md
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# QQ邮箱配置
MAIL_HOST = "smtp.qq.com"
MAIL_USER = "2425109268@qq.com"
MAIL_PASS = "cmgbmtzqfjtfdifh"
MAIL_PORT = 465

def get_db_conn():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# 根据post_id从数据库中获取post
def get_post(post_id):
    conn = get_db_conn()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    return post

def get_user_by_username(username):
    conn = get_db_conn()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_conn()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_user_by_id(user_id)

@app.route('/')
def index():
    if g.user is None:
        flash('请先登录')
        return redirect(url_for('login'))
    conn = get_db_conn()
    posts = conn.execute('SELECT * FROM posts WHERE user_id = ?', (g.user['id'],)).fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/posts/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        flash('文章不存在')
        return redirect(url_for('index'))
    return render_template('full_text.html', post=post)


@app.route('/posts/new', methods=('GET', 'POST'))
def new():
    if g.user is None:
        flash('请先登录')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('标题不能为空!')
        elif not content:
            flash('内容不能为空')
        else:
            conn = get_db_conn()
            conn.execute(
                'INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)',
                (title, content, g.user['id'])
            )
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('new.html')


@app.route('/posts/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    if post is None or post['user_id'] != g.user['id']:
        flash('无权删除')
        return redirect(url_for('index'))
    conn = get_db_conn()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" 删除成功!'.format(post['title']))
    return redirect(url_for('index'))


# 编辑文章
@app.route('/posts/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_conn()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if not username or not password or not email:
            flash('用户名、密码、邮箱不能为空')
        elif get_user_by_username(username):
            flash('用户名已存在')
        else:
            conn = get_db_conn()
            # 检查邮箱唯一性
            if conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone():
                flash('邮箱已被注册')
                conn.close()
            else:
                try:
                    conn.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, generate_password_hash(password), email))
                    conn.commit()
                    conn.close()
                    flash('注册成功，请登录')
                    return redirect(url_for('login'))
                except sqlite3.IntegrityError:
                    flash('用户名或邮箱已存在')
                    conn.close()
    return render_template('register.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            flash('登录成功')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('已退出登录')
    return redirect(url_for('login'))


def get_book_info_by_isbn(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('totalItems', 0) > 0:
            book = data['items'][0]['volumeInfo']
            # 你可以把需要的字段都放到一个 dict 里返回
            return {
                'title': book.get('title'),
                'authors': ', '.join(book.get('authors', [])),
                'publisher': book.get('publisher'),
                'publishedDate': book.get('publishedDate'),
                'description': book.get('description'),
                'thumbnail': book.get('imageLinks', {}).get('thumbnail'),
                'infoLink': book.get('infoLink'),
                'previewLink': book.get('previewLink'),
                'canonicalVolumeLink': book.get('canonicalVolumeLink')
            }
        else:
            return {'error': '未找到该ISBN的图书信息'}
    else:
        return {'error': f'请求失败，状态码：{response.status_code}'}

@app.route('/googlebook', methods=['GET', 'POST'])
def googlebook():
    book = None
    if request.method == 'POST':
        isbn = request.form['isbn'] #从前端提交的表单数据中获取名为 isbn 的字段的值。
        book = get_book_info_by_isbn(isbn)
    return render_template('googlebook.html', book=book)

@app.route('/books')
def books():
    sort = request.args.get('sort', 'date_desc')  # 默认按出版时间降序
    conn = get_db_conn()
    books = conn.execute('SELECT * FROM books LIMIT 100').fetchall()
    conn.close()

    if sort == 'date_asc':
        books.sort(key=lambda x: x['publishedDate'] or '') #按照出版时间升序
    elif sort == 'date_desc':
        books.sort(key=lambda x: x['publishedDate'] or '', reverse=True) #按照出版时间降序
    elif sort == 'alpha_asc':
        books.sort(key=lambda x: (x['title'][0].upper() if x['title'] else '')) #按照首字母升序
    elif sort == 'alpha_desc':
        books.sort(key=lambda x: (x['title'][0].upper() if x['title'] else ''), reverse=True) #按照首字母降序

    return render_template('books.html', books=books, sort=sort)

@app.route('/markdown', methods=['GET', 'POST'])
def edit_markdown():
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_conn()
    if request.method == 'POST':
        content = request.form['content']
        # 判断是否已有记录
        row = conn.execute('SELECT * FROM user_markdown WHERE user_id=?', (user_id,)).fetchone()
        if row:
            conn.execute('UPDATE user_markdown SET content=?, updated=CURRENT_TIMESTAMP WHERE user_id=?', (content, user_id))
        else:
            conn.execute('INSERT INTO user_markdown (user_id, content) VALUES (?, ?)', (user_id, content))
        conn.commit()
        flash('保存成功')
        return redirect(url_for('view_markdown'))
    else:
        row = conn.execute('SELECT content FROM user_markdown WHERE user_id=?', (user_id,)).fetchone()
        content = row['content'] if row else ''
        return render_template('edit_markdown.html', content=content)

@app.route('/markdown/view')
def view_markdown():
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_conn()
    row = conn.execute('SELECT content FROM user_markdown WHERE user_id=?', (user_id,)).fetchone()
    content = row['content'] if row else ''
    html = md.markdown(content or '')
    return render_template('view_markdown.html', html=html)

@app.route('/markdown/export')
def export_markdown():
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_conn()
    row = conn.execute('SELECT content FROM user_markdown WHERE user_id=?', (user_id,)).fetchone()
    content = row['content'] if row else ''
    conn.close()
    # 生成文件名
    filename = f'user_{user_id}_markdown.md'
    # 用 BytesIO 生成文件流
    file_stream = io.BytesIO(content.encode('utf-8'))
    # 返回文件下载响应
    return send_file(
        file_stream,
        as_attachment=True,
        download_name=filename,
        mimetype='text/markdown'
    )

@app.route('/posts/<int:post_id>/export')
def export_post(post_id):
    # 检查用户是否登录（可选）
    # if 'user_id' not in session:
    #     flash('请先登录')
    #     return redirect(url_for('login'))

    conn = get_db_conn()
    post = conn.execute('SELECT * FROM posts WHERE id=?', (post_id,)).fetchone()
    conn.close()
    if not post:
        abort(404)

    # 组织导出内容
    content = f"标题：{post['title']}\n"
    content += f"内容：\n{post['content']}\n"
    content += f"发布时间：{post['created']}\n"

    filename = f"post_{post_id}.txt"
    file_stream = io.BytesIO(content.encode('utf-8'))
    return send_file(
        file_stream,
        as_attachment=True,
        download_name=filename,
        mimetype='text/plain'
    )

def send_email(to_email, subject, content):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = MAIL_USER
    msg['To'] = to_email

    try:
        smtp = smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT)
        smtp.login(MAIL_USER, MAIL_PASS)
        smtp.sendmail(MAIL_USER, [to_email], msg.as_string())
        smtp.quit()
        return True
    except Exception as e:
        print("邮件发送失败：", e)
        return False

# 忘记密码 - 邮箱验证码
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_conn()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if not user:
            flash('该邮箱未注册')
        else:
            code = str(random.randint(100000, 999999))
            session['reset_email'] = email
            session['reset_code'] = code
            session['reset_code_time'] = int(time.time())
            send_email(email, '找回密码验证码', f'您的验证码是：{code}，5分钟内有效。')
            flash('验证码已发送到邮箱，请查收')
            return redirect(url_for('reset_password'))
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        code = request.form['code']
        new_password = request.form['new_password']
        email = session.get('reset_email')
        real_code = session.get('reset_code')
        code_time = session.get('reset_code_time')
        if not (email and real_code and code_time):
            flash('请先获取验证码')
            return redirect(url_for('forgot_password'))
        if int(time.time()) - code_time > 300:
            flash('验证码已过期，请重新获取')
            return redirect(url_for('forgot_password'))
        if code != real_code:
            flash('验证码错误')
        else:
            conn = get_db_conn()
            conn.execute('UPDATE users SET password = ? WHERE email = ?', (generate_password_hash(new_password), email))
            conn.commit()
            conn.close()
            session.pop('reset_email', None)
            session.pop('reset_code', None)
            session.pop('reset_code_time', None)
            flash('密码重置成功，请登录')
            return redirect(url_for('login'))
    return render_template('reset_password.html')

if __name__ == '__main__':
    app.run()
