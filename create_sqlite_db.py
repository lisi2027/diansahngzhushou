import sqlite3
import pandas as pd

# 你的 Excel 文件路径
excel_path = r'C:\Users\1\Desktop\智能体\order2019.xlsx'
# 输出的 SQLite 数据库路径（放在桌面智能体文件夹）
db_path = r'C:\Users\1\Desktop\智能体\order_2019.db'

print("正在读取 order2019.xlsx...")
df = pd.read_excel(excel_path)

print(f"✅ 成功读取 {len(df)} 条订单数据")

# 创建 SQLite 数据库
conn = sqlite3.connect(db_path)

# 导入数据
df.to_sql('orders', conn, if_exists='replace', index=False)

print(f"✅ 数据已导入 SQLite 数据库：{db_path}")

# 验证：按小时统计
cursor = conn.cursor()
cursor.execute("""
    SELECT 
        CAST(STRFTIME('%H', orderTime) AS INTEGER) AS h1,
        COUNT(*) AS num
    FROM orders
    WHERE orderTime LIKE '2019-%'
    GROUP BY h1
    ORDER BY h1
""")

print("\n📊 小时订单分布（用于需求预测）：")
print("时段 | 订单数")
print("-----|------")
for row in cursor.fetchall():
    print(f" {row[0]:2d}点 | {row[1]:6d} 单")

# 额外验证：总订单数
cursor.execute("SELECT COUNT(*) FROM orders")
total = cursor.fetchone()[0]
print(f"\n📋 数据库总订单数：{total} 条")

conn.close()
print("\n✅ 数据库创建成功！可以在 Dify 中使用了。")