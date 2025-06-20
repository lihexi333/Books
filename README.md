# 图书管理与博客系统

这是一个基于 Flask 的 Web 应用程序，集成了图书管理、博客写作和 Markdown 编辑功能。系统采用模块化设计，使用 Blueprint 进行功能划分，支持用户认证、密码重置等功能。

## 功能特性

### 1. 用户管理
- 用户注册与登录
- 管理员角色与权限控制
- 基于邮箱的密码重置
- 会话管理和认证

### 2. 图书管理
- Google Books API 集成
- 图书搜索与展示
- 管理员后台添加与删除图书
- 支持按时间和标题排序
- 毛玻璃风格的界面设计
- 响应式卡片布局

### 3. 博客系统
- 博客文章的创建、编辑、删除
- Markdown 格式支持
- 文章导出功能
- 个人文章管理

### 4. Markdown 编辑器
- 在线 Markdown 编辑与实时预览
- 支持代码块语法高亮
- 内容本地保存与文件导出功能

## 技术栈
- **后端**: Flask, Pygments
- **数据库**: SQLite3
- **前端**:
  - JavaScript (Marked.js, highlight.js)
  - Tailwind CSS
  - Bootstrap
  - jQuery
- **第三方服务**:
  - Google Books API
  - SMTP 邮件服务

## 项目结构
```
Books/
├── .env                 # 环境变量配置文件 (本地)
├── .env.example         # 环境变量配置文件示例
├── .gitignore           # Git忽略文件配置
├── app.py               # 应用入口和命令行接口
├── auth.py              # 认证蓝图 (登录, 注册, 密码重置, 管理员功能)
├── books_bp.py          # 图书蓝图 (搜索, 列表)
├── book_apitest.py      # Google Books API 测试脚本
├── db.sql               # 数据库表结构定义
├── db_utils.py          # 数据库连接和操作工具
├── errors.py            # Flask错误处理器
├── fetch_books.py       # (弃用) 用于爬取图书信息的脚本
├── init_env.py          # 应用工厂 (create_app)
├── markdown_bp.py       # Markdown编辑器蓝图
├── posts.py             # 博客文章蓝图
├── README.md            # 项目说明文档
├── requirements.txt     # Python依赖包
├── utils.py             # 通用工具函数 (如: 邮件发送)
│
├── instance/            # 实例文件夹，存放数据库等不应提交到版本库的文件
│   └── database.db      # SQLite数据库文件
│
├── photos/              # (设计文档) 存放项目相关的UML图等
│   ├── markdown用例图.svg
│   ├── 关系模式.svg
│   └── ...
│
├── static/              # 静态资源
│   ├── css/
│   │   ├── bootstrap.css
│   │   └── style.css
│   │   └── ...
│   ├── img/
│   │   └── book-placeholder.png
│   └── js/
│       ├── bootstrap.js
│       └── jquery.js
│
└── templates/           # Jinja2 模板文件
    ├── admin_add_book.html
    ├── base.html
    ├── books.html
    ├── edit.html
    ├── edit_markdown.html
    ├── error.html
    ├── forgot_password.html
    ├── full_text.html
    ├── googlebook.html
    ├── index.html
    ├── login.html
    ├── new.html
    ├── register.html
    ├── reset_password.html
    └── view_markdown.html

```

## 安装说明

1. 克隆项目并进入项目目录：
```bash
git clone <repository-url>
cd Books
```

2. 创建并激活虚拟环境：
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 初始化数据库：
```bash
python app.py init-db
```

## 运行说明

1. 开发环境运行：
```bash
python app.py dev
```

2. 生产环境运行：
```bash
python app.py prod
```

## 环境变量配置

项目使用 `.env` 文件管理环境变量，需要配置以下内容：

```env
FLASK_SECRET_KEY=your-secret-key
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password
```

## 使用说明

1. 用户注册/登录
   - 访问首页，点击注册/登录
   - 填写相关信息完成注册
   - 登录后可以使用全部功能
   - 使用 `python app.py init-db` 初始化数据库后，会自动创建管理员账号（用户名：`管理员`，密码：`111`），登录后可管理图书。

2. 图书搜索
   - 在图书搜索页面输入关键词
   - 系统会调用 Google Books API 搜索相关图书
   - 以卡片形式展示搜索结果

3. 博客管理
   - 创建新文章
   - 编辑已有文章
   - 删除文章
   - 导出为 Markdown 文件

4. Markdown 编辑
   - 支持实时预览
   - 可以保存和导出编辑内容

## 数据库设计

系统使用 SQLite 数据库，包含以下核心表：

### 1. `users` - 用户表
存储用户信息和凭证。

| 字段名 | 类型 | 约束 | 描述 |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 用户唯一标识 |
| `username` | TEXT | UNIQUE, NOT NULL | 用户名 |
| `password` | TEXT | NOT NULL | 哈希加密后的密码 |
| `email` | TEXT | UNIQUE, NOT NULL | 用户邮箱 |
| `is_admin` | INTEGER | NOT NULL, DEFAULT 0 | 是否为管理员 (1是, 0否) |

### 2. `posts` - 博客文章表
存储用户发布的博客文章。

| 字段名 | 类型 | 约束 | 描述 |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 文章唯一标识 |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY (users) | 作者的用户ID |
| `title` | TEXT | NOT NULL | 文章标题 |
| `content` | TEXT | NOT NULL | 文章内容 |
| `created` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 3. `books` - 图书表
存储用户收藏的图书信息。

| 字段名 | 类型 | 约束 | 描述 |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 图书唯一标识 |
| `title` | TEXT | NOT NULL | 书名 |
| `authors` | TEXT | | 作者，多个作者以逗号分隔 |
| `publisher` | TEXT | | 出版社 |
| `publishedDate` | TEXT | | 出版日期 |
| `description` | TEXT | | 图书简介 |
| `thumbnail` | TEXT | | 封面图片链接 |
| `infoLink` | TEXT | | Google Books 详情页链接 |

### 4. `user_markdown` - Markdown内容表
存储每个用户的 Markdown 编辑器内容。

| 字段名 | 类型 | 约束 | 描述 |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 记录唯一标识 |
| `user_id` | INTEGER | UNIQUE, NOT NULL, FOREIGN KEY (users) | 关联的用户ID |
| `content` | TEXT | | 用户保存的Markdown内容 |

## 注意事项

- 确保已安装所有依赖包
- 配置正确的邮件服务器信息
- 数据库文件位于 `instance/database.db`
- 建议在虚拟环境中运行项目

## 开发者

如需贡献代码或报告问题，请：
1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 发起 Pull Request

## 许可证

MIT License