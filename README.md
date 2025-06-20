# 图书管理与博客系统

这是一个基于 Flask 的 Web 应用程序，集成了图书管理、博客写作和 Markdown 编辑功能。系统采用模块化设计，使用 Blueprint 进行功能划分，支持用户认证、密码重置等功能。

## 功能特性

### 1. 用户管理
- 用户注册与登录
- 基于邮箱的密码重置
- 会话管理和认证

### 2. 图书管理
- Google Books API 集成
- 图书搜索与展示
- 支持按时间和标题排序
- 毛玻璃风格的界面设计
- 响应式卡片布局

### 3. 博客系统
- 博客文章的创建、编辑、删除
- Markdown 格式支持
- 文章导出功能
- 个人文章管理

### 4. Markdown 编辑器
- 在线 Markdown 编辑
- 实时预览
- 文件导出功能

## 技术栈
- 后端：Flask
- 数据库：SQLite3
- 前端：
  - Tailwind CSS
  - Bootstrap
  - jQuery
- 第三方服务：
  - Google Books API
  - SMTP 邮件服务

## 项目结构
```
Books/
├── app.py              # 应用入口
├── auth.py            # 用户认证模块
├── books_bp.py        # 图书管理模块
├── db_utils.py        # 数据库工具
├── errors.py          # 错误处理
├── markdown_bp.py     # Markdown编辑器模块
├── posts.py           # 博客文章模块
└── templates/         # 模板文件
    ├── base.html
    ├── books.html
    ├── googlebook.html
    └── ...
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