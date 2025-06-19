from flask import Blueprint, render_template, request, flash, redirect, url_for, g, abort
from db_utils import get_db_conn, get_post
import requests

books_bp = Blueprint('books', __name__, url_prefix="/books")

def get_book_info_by_name(name):
    """通过书名从Google Books API获取图书信息"""
    url = f"https://www.googleapis.com/books/v1/volumes?q={name}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 如果请求失败则抛出HTTPError
        data = response.json()

        if "items" in data and data["items"]:
            # 直接返回包含图书详细信息的volumeInfo列表
            return [item.get('volumeInfo', {}) for item in data["items"]]
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"获取图书信息时发生网络错误: {e}")
        return None
    except Exception as e:
        print(f"处理图书信息时发生未知错误: {e}")
        return None

@books_bp.route('/google', methods=['GET', 'POST'])
def googlebook():
    if g.user is None:
        abort(401)
    books = None
    search_term = ""
    if request.method == 'POST':
        search_term = request.form.get('book_name')
        if search_term:
            books = get_book_info_by_name(search_term)
    return render_template('googlebook.html', books=books, search_term=search_term)

@books_bp.route('/')
def list_books():
    sort = request.args.get('sort', 'date_desc')  # 默认按出版时间降序
    conn = get_db_conn()
    
    order_by_clause = 'ORDER BY publishedDate DESC'
    if sort == 'date_asc':
        order_by_clause = 'ORDER BY publishedDate ASC'
    elif sort == 'title_asc':
        order_by_clause = 'ORDER BY title ASC'
    elif sort == 'title_desc':
        order_by_clause = 'ORDER BY title DESC'
    
    books_data = conn.execute(f'SELECT * FROM books {order_by_clause}').fetchall()
    conn.close()
    
    return render_template('books.html', books=books_data, current_sort=sort) 