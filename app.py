from init_env import create_app
from db_utils import init_db
import os
import sys

app = create_app()

def main():
    # 获取命令行参数或从环境变量获取
    env = os.environ.get('DEFAULT_ENV', 'dev')  # 默认开发环境
    
    # 检查是否有帮助参数或init-db命令
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in ['-h', '--help']:
            print("""
使用方法: python app.py [命令或环境]

可选参数:
  -h, --help     显示帮助信息
  init-db        初始化数据库
  dev            开发环境(开启调试模式和热更新)
  prod           生产环境(关闭调试模式)

示例:
  python app.py init-db     # 初始化数据库
  python app.py dev         # 以开发环境启动
  python app.py prod        # 以生产环境启动
  python app.py             # 默认以开发环境启动
            """)
            sys.exit()
        elif command == 'init-db':
            with app.app_context():
                init_db()
                print("数据库已初始化.")
            sys.exit()
        else:
            env = command

    # 根据环境设置debug模式
    if env == 'dev':
        os.environ['FLASK_ENV'] = 'development'  # 设置Flask环境为开发环境
        app.run(debug=True, host='0.0.0.0')
    else:
        os.environ['FLASK_ENV'] = 'production'  # 设置Flask环境为生产环境
        app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
