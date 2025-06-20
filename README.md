# 图书管理与博客系统

这是一个基于Flask的模块化图书管理与博客系统。用户可以记录和分享读书笔记、管理个人图书收藏，并通过Google Books API查询图书信息。项目采用蓝图（Blueprints）进行结构化设计，实现了功能解耦。

## 功能特点

- **用户认证**：提供注册、登录、登出、密码重置等功能。
- **博客文章**：支持创建、编辑、查看、删除和导出个人博客文章。
- **图书管理**：浏览个人收藏的图书，并支持多种排序方式。
- **图书查询**：通过Google Books API实时查询图书信息。
- **Markdown编辑器**：提供一个独立的Markdown编辑器，支持内容的实时预览和导出。

## 技术栈

- **后端**：Flask (Python)
- **数据库**：SQLite
- **前端**：HTML, CSS, JavaScript, Bootstrap
- **API集成**：Google Books API

## 项目结构

项目采用模块化的蓝图结构，核心逻辑分布在不同的模块中：

```
Books/
├── app.py                   # 应用启动入口
├── init_env.py              # 组装和配置Flask应用
├── auth.py                  # 用户认证蓝图
├── posts.py                 # 博客文章蓝图
├── books_bp.py              # 图书管理蓝图
├── markdown_bp.py           # Markdown编辑器蓝图
├── db_utils.py              # 数据库连接和操作工具
├── errors.py                # 统一错误处理
├── utils.py                 # 通用工具函数（如邮件发送）
├── db.sql                   # 数据库表结构定义
├── requirements.txt         # 项目依赖
├── static/                  # 静态文件 (CSS, JS, Images)
└── templates/               # Jinja2 HTML模板
```

## 安装与运行

1.  **克隆仓库**
    ```bash
    git clone <仓库地址>
    cd Books
    ```

2.  **创建虚拟环境并安装依赖**
    建议使用虚拟环境：
    ```bash
    python -m venv venv
    source venv/bin/activate  # on Windows use `venv\Scripts\activate`
    ```
    安装依赖包：
    ```bash
    pip install -r requirements.txt
    ```

3.  **配置环境变量**
    复制 `.env.example` (如果提供) 或手动创建一个 `.env` 文件，并填入必要的环境变量，如 `SECRET_KEY` 和邮件服务器配置。

4.  **初始化数据库（可跳过，已提供`database.db`初始数据库）**
    运行以下命令来创建数据库表：
    ```bash
    python init_db.py
    ```

5.  **运行应用**
    ```bash
    # 开发模式
    python app.py dev

    # 生产模式
    python app.py prod
    ```
    默认不带参数运行时，将以开发模式启动。

6.  **访问应用**
    在浏览器中打开 `http://127.0.0.1:5000` 即可访问。

## 数据库

系统使用SQLite数据库，包含以下核心表：
- `users`: 存储用户信息和凭证。
- `posts`: 存储博客文章。
- `books`: 存储用户收藏的图书信息。
- `user_markdown`: 存储用户的Markdown内容。

## API使用

系统集成了Google Books API用于查询图书信息。您可以通过ISBN码查询图书的详细信息，包括书名、作者、出版社、封面等。

## 测试账号

提供的`database.db`初始数据库中有测试账号：
- 用户名：test
- 密码：test