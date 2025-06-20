from flask import render_template
import sqlite3

def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', 
                              code=404, 
                              message="页面未找到", 
                              description="您请求的页面不存在或已被移除"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', 
                              code=403, 
                              message="禁止访问", 
                              description="您没有权限访问此页面"), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', 
                              code=500, 
                              message="服务器错误", 
                              description="服务器发生内部错误，请稍后再试"), 500

    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('error.html', 
                              code=401, 
                              message="未授权访问", 
                              description="请先登录后再访问此页面"), 401

    @app.errorhandler(429)
    def too_many_requests(e):
        return render_template('error.html', 
                              code=429, 
                              message="请求过于频繁", 
                              description="请求过于频繁，请稍后再试"), 429

    @app.errorhandler(sqlite3.Error)
    def handle_database_error(e):
        app.logger.error(f"数据库错误: {str(e)}")
        return render_template('error.html', 
                              code=500, 
                              message="数据库错误",
                              description="数据库操作出现问题，请稍后再试"), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        code = 500
        if hasattr(e, 'code'):
            code = e.code
        
        if code == 400:
            message = "错误请求"
            description = "服务器无法处理您的请求，请检查输入"
        elif code == 405:
            message = "方法不允许"
            description = "不允许使用此HTTP方法"
        elif code == 408:
            message = "请求超时"
            description = "服务器等待请求时超时"
        elif code == 502:
            message = "网关错误"
            description = "服务器作为网关无法获取响应"
        else:
            message = "服务器错误"
            description = "发生了意外错误，请稍后再试"
        
        if code != 404:
            app.logger.error(f"应用错误 ({code}): {str(e)}")
        
        return render_template('error.html',
                              code=code,
                              message=message,
                              description=description), code 