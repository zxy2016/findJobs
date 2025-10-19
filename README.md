# FindJobs AI 助手

一个AI驱动的求职助手，旨在帮助您找到最合适的工作。本项目通过爬取招聘网站的岗位信息，使用大语言模型（LLM）分析您的简历和偏好，并为您提供个性化的工作推荐。

##核心功能

- **自动化岗位爬取**: 定期从多个招聘网站自动抓取最新的职位数据。
- **AI驱动的简历分析**: 利用大语言模型（LLM）深入分析用户的简历和对话内容，创建一个详尽的个人与专业能力画像。
- **智能岗位匹配**: 基于用户的个人画像和爬取到的岗位数据，提供智能、上下文感知的岗位推荐。

## 技术栈

- **后端**: Python, FastAPI
- **Web爬虫**: Playwright
- **数据库**: MySQL with SQLAlchemy
- **配置管理**: Pydantic & .env 文件
- **AI集成**: 设计上兼容多种大语言模型服务商（例如 Gemini）。

## 项目结构

```
/
├── app/                  # 主应用源码目录
│   ├── core/             # 配置与核心设置
│   ├── db/               # 数据库会话管理
│   ├── models/           # SQLAlchemy 数据库模型
│   ├── scraper/          # 网络爬虫逻辑
│   └── main.py           # FastAPI 应用入口文件
├── .env.example          # 环境变量示例文件
├── requirements.txt      # Python 依赖包
├── DESIGN.md             # 技术设计文档
└── README.md             # 本文件
```

## 安装与启动

1.  **克隆仓库**
    ```bash
    git clone <your-repository-url>
    cd findJobs
    ```

2.  **创建并激活虚拟环境**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

4.  **安装 Playwright 浏览器驱动**
    ```bash
    playwright install
    ```

5.  **设置环境变量**
    -   复制环境变量示例文件：
        ```bash
        cp .env.example .env
        ```
    -   编辑 `.env` 文件，填入您的数据库和 LLM API 的访问凭证。

## 运行应用

1.  **启动 FastAPI 服务**
    ```bash
    uvicorn app.main:app --reload
    ```
2.  应用将在 `http://127.0.0.1:8000` 上可用。

## 开发路线图

- [ ] **第一阶段：爬虫与数据库**
  - [ ] 实现海尔招聘网的爬虫。
  - [ ] 定义岗位的数据库模型。
  - [ ] 将爬取的数据存入 MySQL。
- [ ] **第二阶段：个人分析**
  - [ ] 构建用于简历上传和文本分析的 API 端点。
  - [ ] 集成 LLM 进行个人画像提取。
- [ ] **第三阶段：匹配与推荐**
  - [ ] 开发核心的匹配算法。
  - [ ] 创建 API 端点以提供推荐结果。
  - [ ] 构建一个简单的前端页面来展示结果。