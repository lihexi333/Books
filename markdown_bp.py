from flask import Blueprint, render_template, request, session, g, abort, send_file, redirect, url_for
from db_utils import get_markdown_by_user_id, save_markdown
import markdown as md
import io

markdown_bp = Blueprint('markdown', __name__, url_prefix='/markdown')

@markdown_bp.route('/', methods=['GET', 'POST'])
def edit_markdown():
    if 'user_id' not in session:
        abort(401)
    
    user_id = session['user_id']

    if request.method == 'POST':
        content = request.form['content']
        save_markdown(user_id, content)
        return redirect(url_for('markdown.view_markdown'))

    # GET请求，加载已保存的内容
    user_md = get_markdown_by_user_id(user_id)
    content = user_md['content'] if user_md else ''
    return render_template('edit_markdown.html', content=content)

@markdown_bp.route('/view')
def view_markdown():
    if 'user_id' not in session:
        abort(401)
    
    user_id = session['user_id']
    user_md = get_markdown_by_user_id(user_id)
    
    content = user_md['content'] if user_md else ''
    html_content = md.markdown(content, extensions=['fenced_code', 'tables', 'codehilite'])
    
    return render_template('view_markdown.html', html_content=html_content)

@markdown_bp.route('/export')
def export_markdown():
    if 'user_id' not in session:
        abort(401)
    
    user_id = session['user_id']
    user_md = get_markdown_by_user_id(user_id)
    
    if not user_md:
        return "没有可导出的内容", 404
        
    buffer = io.BytesIO(user_md['content'].encode('utf-8'))
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='markdown_export.md',
        mimetype='text/markdown'
    ) 