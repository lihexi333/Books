from flask import Blueprint, render_template, request, flash, redirect, url_for, g, abort, send_file
from .db_utils import get_db_conn, get_post
import io

posts_bp = Blueprint('posts', __name__, url_prefix='/')

@posts_bp.route('/')
def index():
    if g.user is None:
        return redirect(url_for('auth.login'))
    conn = get_db_conn()
    posts = conn.execute('SELECT * FROM posts WHERE user_id = ?', (g.user['id'],)).fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@posts_bp.route('/posts/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        abort(404)
    return render_template('full_text.html', post=post)

@posts_bp.route('/posts/new', methods=('GET', 'POST'))
def new():
    if g.user is None:
        abort(401)
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
            return redirect(url_for('posts.index'))
    return render_template('new.html')

@posts_bp.route('/posts/<int:id>/delete', methods=('POST',))
def delete(id):
    if g.user is None:
        abort(401)
    post = get_post(id)
    if post is None:
        abort(404)
    if post['user_id'] != g.user['id']:
        abort(403)
    conn = get_db_conn()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" 删除成功!'.format(post['title']))
    return redirect(url_for('posts.index'))

@posts_bp.route('/posts/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    if g.user is None:
        abort(401)
    post = get_post(id)
    if post is None:
        abort(404)
    if post['user_id'] != g.user['id']:
        abort(403)
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('标题不能为空!')
        else:
            conn = get_db_conn()
            conn.execute(
                'UPDATE posts SET title = ?, content = ? WHERE id = ?',
                (title, content, id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('posts.index'))

    return render_template('edit.html', post=post)

@posts_bp.route('/posts/<int:post_id>/export')
def export_post(post_id):
    if g.user is None:
        abort(401)
    post = get_post(post_id)
    if not post:
        abort(404)

    if post['user_id'] != g.user['id']:
        abort(403)

    content = f"# {post['title']}\n\n{post['content']}"
    buffer = io.BytesIO(content.encode('utf-8'))
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{post['title']}.md",
        mimetype='text/markdown'
    ) 