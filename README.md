# 电商助手项目

基于 Python 的数据分析工具，用于订单数据处理、报告生成和可视化展示。

## 功能特性

- 📊 **报告生成服务**：接收 HTML 内容并生成可访问的报告文件
- 📁 **数据管理**：支持 SQLite 和 MySQL 数据库
- 🌐 **Web 服务**：基于 Flask 的 RESTful API
- 🔄 **跨域支持**：内置 CORS，支持前端调用

## 项目结构

```
dianshang/
├── app.py              # Flask 报告生成服务
├── create_sqlite_db.py # SQLite 数据库创建脚本
├── migrate_to_mysql.py # MySQL 数据迁移脚本
├── .gitignore          # Git 忽略配置
├── data/               # 生成的报告文件目录
└── README.md           # 项目说明
```

## 环境要求

- Python 3.8+
- Flask
- Flask-CORS
- pandas
- openpyxl (Excel 读取)
- pymysql (MySQL 连接)
- sqlalchemy (数据库迁移)

## 安装依赖

```bash
pip install flask flask-cors pandas openpyxl pymysql sqlalchemy
```

## 快速开始

### 1. 启动报告生成服务

```bash
python app.py
```

服务将在以下地址启动：
- 本地访问: `http://127.0.0.1:5000`
- 局域网访问: `http://你的IP:5000`

### 2. 创建 SQLite 数据库

```bash
python create_sqlite_db.py
```

该脚本会读取 `order2019.xlsx` 并导入到 SQLite 数据库。

### 3. 迁移到 MySQL

```bash
python migrate_to_mysql.py
```

确保已安装 MySQL 并配置正确的连接信息。

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页，显示报告列表 |
| `/generate` | POST | 生成 HTML 报告 |
| `/view/<filename>` | GET | 查看指定报告 |
| `/list` | GET | 获取报告列表（JSON） |
| `/ping` | GET | 健康检查 |
| `/debug` | GET | 调试信息 |

### 生成报告示例

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"html_content": "<html><body>Hello World</body></html>"}'
```

## Dify 集成

在 Dify 中使用时，设置环境变量：

```
PUBLIC_HOST = host.docker.internal
```

## 配置说明

### `.gitignore` 忽略内容

- `.idea/` - IDE 配置
- `data/*.html` - 生成的报告文件
- `__pycache__/` - Python 缓存
- `*.pyc`, `*.pyo` - 编译文件
- `.DS_Store` - macOS 系统文件

## License

MIT