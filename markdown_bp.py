from flask import Blueprint, render_template, request, session, g, abort, send_file, redirect, url_for
from .db_utils import get_db_conn
import markdown as md
import io

markdown_bp = Blueprint('markdown', __name__, url_prefix='/markdown')

@markdown_bp.route('/', methods=['GET', 'POST'])
def edit_markdown():
    if 'user_id' not in session:
        abort(401)

    if request.method == 'POST':
        content = request.form['content']
        user_id = session['user_id']
        
        conn = get_db_conn()
        # 检查用户是否已有Markdown内容
        user_md = conn.execute('SELECT * FROM user_markdown WHERE user_id = ?', (user_id,)).fetchone()

        if user_md:
            conn.execute('UPDATE user_markdown SET content = ? WHERE user_id = ?', (content, user_id))
        else:
            conn.execute('INSERT INTO user_markdown (user_id, content) VALUES (?, ?)', (user_id, content))
        
        conn.commit()
        conn.close()
        return redirect(url_for('markdown.view_markdown'))

    # GET请求，加载已保存的内容
    user_id = session['user_id']
    conn = get_db_conn()
    user_md = conn.execute('SELECT content FROM user_markdown WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    
    content = user_md['content'] if user_md else ''
    return render_template('edit_markdown.html', content=content)

@markdown_bp.route('/view')
def view_markdown():
    if 'user_id' not in session:
        abort(401)
    
    user_id = session['user_id']
    conn = get_db_conn()
    user_md = conn.execute('SELECT content FROM user_markdown WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    
    content = user_md['content'] if user_md else ''
    html_content = md.markdown(content)
    
    return render_template('view_markdown.html', html_content=html_content)

@markdown_bp.route('/export')
def export_markdown():
    if 'user_id' not in session:
        abort(401)
    
    user_id = session['user_id']
    conn = get_db_conn()
    user_md = conn.execute('SELECT content FROM user_markdown WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    
    if not user_md:
        return "没有可导出的内容", 404
        
    buffer = io.BytesIO(user_md['content'].encode('utf-8'))
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='markdown_export.md',
        mimetype='text/markdown'
    ) 