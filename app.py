from init_env import create_app
import os
import sys

app = create_app()

def main():
    # 获取命令行参数或从环境变量获取
    env = os.environ.get('DEFAULT_ENV', 'dev')  # 默认开发环境
    # 检查是否有帮助参数
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
使用方法: python blog.py [环境]

可选参数:
  -h, --help     显示帮助信息
  dev    开发环境(开启调试模式和热更新)
  prod     生产环境(关闭调试模式)

示例:
  python blog.py dev  # 以开发环境启动
  python blog.py prod   # 以生产环境启动
  python blog.py             # 默认以开发环境启动
        """)
        sys.exit()
    
    # 获取环境参数
    if len(sys.argv) > 1:
        env = sys.argv[1]
    
    # 根据环境设置debug模式
    if env == 'dev':
        os.environ['FLASK_ENV'] = 'development'  # 设置Flask环境为开发环境
        app.run(debug=True, host='0.0.0.0')
    else:
        os.environ['FLASK_ENV'] = 'production'  # 设置Flask环境为生产环境
        app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()
