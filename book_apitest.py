import requests

def get_book_info_by_isbn(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('totalItems', 0) > 0:
            book = data['items'][0]['volumeInfo']
            print("书名：", book.get('title'))
            print("作者：", ', '.join(book.get('authors', [])))
            print("出版社：", book.get('publisher'))
            print("出版日期：", book.get('publishedDate'))
            print("简介：", book.get('description'))
            print("封面：", book.get('imageLinks', {}).get('thumbnail'))
            print("Google图书详情页：", book.get('infoLink'))
            print("Google图书预览页：", book.get('previewLink'))
            print("Google图书标准页：", book.get('canonicalVolumeLink'))
            return book
        else:
            print("未找到该ISBN的图书信息")
            return None
    else:
        print("请求失败，状态码：", response.status_code)
        return None

# 示例调用
isbn = "9781498711395"
get_book_info_by_isbn(isbn)