import sqlite3
import pandas as pd
from sqlalchemy import create_engine

print("正在从 SQLite 读取数据...")
sqlite_conn = sqlite3.connect(r'C:\Users\1\Desktop\智能体\order_2019.db')
df = pd.read_sql_query("SELECT * FROM orders", sqlite_conn)
print(f"✅ 读取 {len(df)} 条订单数据")

print("正在连接到 MySQL...")
# 使用 SQLAlchemy 创建连接引擎（修复兼容性问题）
engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3307/order_db')

print("正在导入数据...")
df.to_sql('orders', engine, if_exists='replace', index=False)

print(f"✅ 成功导入 {len(df)} 条订单数据到 MySQL")

sqlite_conn.close()
print("✅ 迁移完成！")