import mysql.connector
import os
from dotenv import load_dotenv
import getpass

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME", "find_jobs")

if not DB_USER:
    print("Error: DB_USER not found in .env file. Please configure it.")
    exit(1)

# 数据库列表
databases_to_create = [
    DB_NAME,  # 主应用数据库
    f"{DB_NAME}_test",  # 模型单元测试数据库
    f"{DB_NAME}_test_scraper"  # 爬虫集成测试数据库
]

print(f"Attempting to initialize databases for user '{DB_USER}' on host '{DB_HOST}'...")

# 获取 MySQL 管理员密码
admin_user = input("Enter MySQL admin username (e.g., root): ")
admin_password = getpass.getpass(f"Enter MySQL password for '{admin_user}': ")

try:
    # 连接到 MySQL 服务器 (作为管理员)
    cnx = mysql.connector.connect(
        host=DB_HOST,
        user=admin_user,
        password=admin_password
    )
    cursor = cnx.cursor()

    # 创建数据库
    for db_name in databases_to_create:
        print(f"Creating database '{db_name}' if it doesn't exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")

    # 创建用户并设置密码
    print(f"Creating user '{DB_USER}'@'{DB_HOST}' if it doesn't exist...")
    try:
        cursor.execute(f"CREATE USER '{DB_USER}'@'{DB_HOST}' IDENTIFIED BY 'findjobs1229'")
    except mysql.connector.Error as err:
        if "already exists" in str(err):
            print(f"User '{DB_USER}'@'{DB_HOST}' already exists. Skipping creation.")
        else:
            raise err

    # 授予权限
    print(f"Granting privileges to user '{DB_USER}' on host '{DB_HOST}'...")
    # 注意：这里假设 DB_USER 可以在 DB_HOST 上连接。如果 DB_USER 只能从特定IP连接，需要调整 'localhost' 部分
    for db_name in databases_to_create:
        cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{DB_USER}'@'{DB_HOST}'")

    cursor.execute("FLUSH PRIVILEGES")
    print("Privileges flushed.")
    print("Database initialization complete!")

except mysql.connector.Error as err:
    print(f"Error: {err}")
    print("Please ensure MySQL server is running and admin credentials are correct.")
    print("Also, check if the DB_USER in your .env file is correctly configured.")
finally:
    if 'cnx' in locals() and cnx.is_connected():
        cursor.close()
        cnx.close()

# --- 创建数据库表 ---
print("\nStarting table creation process...")
try:
    from app.db.session import engine
    from app.db.base_class import Base
    from sqlalchemy import text
    import app.models # 确保模型被注册

    print("Connecting to the database and creating tables...")
    # Base.metadata.create_all 会安全地创建所有不存在的表
    # 它不会修改或删除任何现有的表
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
except Exception as e:
    print(f"An error occurred during table creation: {e}")

