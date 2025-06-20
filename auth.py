from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g, abort
from werkzeug.security import generate_password_hash, check_password_hash
from db_utils import get_db_conn, get_user_by_username, get_user_by_id
from utils import send_email
import time
import random

auth_bp = Blueprint('auth', __name__, url_prefix='/')

@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = get_db_conn()
        error = None

        if not username:
            error = '用户名是必填的'
        elif not password:
            error = '密码是必填的'
        elif not email:
            error = '邮箱是必填的'
        elif get_user_by_username(username) is not None:
            error = f"用户 {username} 已被注册"

        if error is None:
            conn.execute(
                'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                (username, generate_password_hash(password), email)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('auth.login'))
        
        flash(error)
        conn.close()

    return render_template('register.html')

@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']  # 记录是否管理员
            flash('登录成功')
            return redirect(url_for('posts.index'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

@auth_bp.route('/admin/books/add', methods=['GET', 'POST'])
def admin_add_book():
    if not session.get('is_admin'):
        abort(403)
    if request.method == 'POST':
        title = request.form['title']
        authors = request.form['authors']
        publisher = request.form['publisher']
        publishedDate = request.form['publishedDate']
        description = request.form['description']
        thumbnail = request.form['thumbnail']
        infoLink = request.form['infoLink']
        conn = get_db_conn()
        conn.execute('INSERT INTO books (title, authors, publisher, publishedDate, description, thumbnail, infoLink) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (title, authors, publisher, publishedDate, description, thumbnail, infoLink))
        conn.commit()
        conn.close()
        flash('图书添加成功')
        return redirect(url_for('books.list_books'))
    return render_template('admin_add_book.html')

@auth_bp.route('/admin/books/<int:book_id>/delete', methods=['POST'])
def admin_delete_book(book_id):
    if not session.get('is_admin'):
        abort(403)
    conn = get_db_conn()
    conn.execute('DELETE FROM books WHERE id=?', (book_id,))
    conn.commit()
    conn.close()
    flash('图书删除成功')
    return redirect(url_for('books.list_books'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_conn()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user:
            token = ''.join(random.choices('0123456789', k=6))
            session['reset_token'] = {'token': token, 'email': email, 'time': time.time()}
            
            send_email(email, '密码重置请求', f'你的验证码是: {token}')
            flash('验证码已发送到您的邮箱')
            return redirect(url_for('auth.reset_password'))
        else:
            flash('邮箱不存在')

    return render_template('forgot_password.html')

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_token' not in session:
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        token = request.form['code']
        new_password = request.form['new_password']
        
        reset_info = session.get('reset_token')
        
        # 检查token是否过期（5分钟）
        if not reset_info or time.time() - reset_info.get('time', 0) > 300:
            flash('验证码已过期')
            session.pop('reset_token', None)
            return redirect(url_for('auth.forgot_password'))
            
        if token == reset_info['token']:
            conn = get_db_conn()
            conn.execute(
                'UPDATE users SET password = ? WHERE email = ?',
                (generate_password_hash(new_password), reset_info['email'])
            )
            conn.commit()
            
            session.pop('reset_token', None)
            flash('密码重置成功')
            return redirect(url_for('auth.login'))
        else:
            flash('验证码错误')

    return render_template('reset_password.html')


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_user_by_id(user_id) 