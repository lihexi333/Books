DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS user_markdown;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,         -- 用户唯一编号
    username VARCHAR(20) UNIQUE NOT NULL,         -- 用户名
    password TEXT NOT NULL,                       -- 密码（加密存储）
    email VARCHAR(50) UNIQUE NOT NULL             -- 邮箱
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,         -- 文章唯一编号
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    title TEXT NOT NULL,                          -- 文章标题
    content TEXT NOT NULL,                        -- 文章内容
    user_id VARCHAR(20) NOT NULL,                 -- 作者用户id（关联users表）
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,         -- 图书唯一编号
    title TEXT,                                   -- 书名
    authors TEXT,                                 -- 作者
    publisher TEXT,                               -- 出版社
    publishedDate TEXT,                           -- 出版日期
    description TEXT,                             -- 简介
    thumbnail TEXT,                               -- 封面图片链接
    infoLink TEXT                                 -- 详情页链接
);

CREATE TABLE user_markdown (
    id INTEGER PRIMARY KEY AUTOINCREMENT,         -- 唯一编号
    user_id INTEGER NOT NULL UNIQUE,              -- 用户id（关联users表，每用户一份）
    content TEXT,                                 -- Markdown内容
    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
    FOREIGN KEY (user_id) REFERENCES users (id)
);