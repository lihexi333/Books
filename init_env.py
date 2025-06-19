import os
import sys
from flask import Flask
from dotenv import load_dotenv

def create_app():
    # 加载.env文件中的环境变量
    load_dotenv()

    # 获取当前文件的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # `template_dir`和`static_dir`的路径是相对于当前文件的
    # 当`init_env.py`在`Books`目录下时，这两个路径是正确的
    template_dir = os.path.join(current_dir, 'templates')
    static_dir = os.path.join(current_dir, 'static')

    app = Flask(__name__, 
                instance_relative_config=True,
                template_folder=template_dir,
                static_folder=static_dir)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'database.db'),
    )

    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 初始化数据库
    from db_utils import init_app as init_db_app
    init_db_app(app)

    # 注册错误处理器
    from errors import register_error_handlers
    register_error_handlers(app)

    # 注册蓝图
    from auth import auth_bp
    app.register_blueprint(auth_bp)

    from posts import posts_bp
    app.register_blueprint(posts_bp)
    
    from books_bp import books_bp
    app.register_blueprint(books_bp)

    from markdown_bp import markdown_bp
    app.register_blueprint(markdown_bp)

    # 将index设置为posts.index, 这样访问/时会调用posts蓝图的index视图
    app.add_url_rule('/', endpoint='posts.index')
    
    return app 