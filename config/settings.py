# config/settings.py

# API 服务配置
BASE_URL = "http://localhost:5000"
USERNAME = "test_user_01"
PASSWORD = "123456"

# MySQL 数据库配置 (根据您的 docker-compose.yml 填写)
DB_HOST = "localhost"       # 数据库地址
DB_PORT = 3306              # 数据库端口
DB_USER = "user"            # 数据库账号
DB_PASSWORD = "password"        # 数据库密码 (请核对您的 yml 文件)
DB_NAME = "task_db"         # 数据库名称 (请核对您的 yml 文件)