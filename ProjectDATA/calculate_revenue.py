import os
import pandas as pd
import sqlite3

# 获取脚本所在目录，确保在不同环境中路径正确
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "merged_data.db")

# 汇率配置：将各币种转换为人民币
RATES = {"USD": 6.9, "EUR": 7.5, "CNY": 1.0, "JPY": 0.05}


def load_data():
    """读取订单和客户数据文件"""
    # BUG: 故意拼写错误文件名，导致文件找不到，workflow 会失败
    orders = pd.read_csv(os.path.join(DATA_DIR, "order_typo.txt"))
    customers = pd.read_csv(os.path.join(DATA_DIR, "customer.txt"))
    return orders, customers


def clean_data(orders, customers):
    """清洗数据：去除重复记录"""
    orders_clean = orders.drop_duplicates()
    customers_clean = customers.drop_duplicates()
    return orders_clean, customers_clean


def convert_to_cny(orders):
    """将所有金额转换为人民币，新增 amount_cny 列"""
    orders["amount_cny"] = orders["amount"] * orders["currency"].map(RATES)
    return orders


def calculate_total_revenue(orders):
    """计算整体营业额（人民币）"""
    total = orders["amount_cny"].sum()
    return total


def merge_data(orders, customers):
    """根据 customer_id 合并订单和客户数据"""
    merged = pd.merge(orders, customers, on="customer_id")
    return merged


def save_to_database(merged, total_revenue):
    """将合并后的数据和总营业额保存到 SQLite 数据库"""
    conn = sqlite3.connect(DB_PATH)
    
    # 保存合并后的订单数据
    merged.to_sql("merged_orders", conn, if_exists="replace", index=False)
    
    # 保存按地区汇总的平均金额
    summary = merged.groupby("region")["amount_cny"].mean().reset_index()
    summary.columns = ["region", "avg_amount_cny"]
    summary.to_sql("region_summary", conn, if_exists="replace", index=False)
    
    # 保存总营业额
    revenue_df = pd.DataFrame({"total_revenue_cny": [total_revenue]})
    revenue_df.to_sql("total_revenue", conn, if_exists="replace", index=False)
    
    conn.close()


def main():
    """主流程：加载数据 -> 清洗 -> 转换 -> 计算总营业额 -> 合并 -> 保存"""
    print("Step 1: Loading data...")
    orders, customers = load_data()
    
    print("Step 2: Cleaning data...")
    orders, customers = clean_data(orders, customers)
    
    print("Step 3: Converting amounts to CNY...")
    orders = convert_to_cny(orders)
    
    print("Step 4: Calculating total revenue...")
    total_revenue = calculate_total_revenue(orders)
    print(f"Total Revenue (CNY): {total_revenue:.2f}")
    
    print("Step 5: Merging data...")
    merged = merge_data(orders, customers)
    
    print("Step 6: Saving to database...")
    save_to_database(merged, total_revenue)
    
    print("Done! Database updated successfully.")
    return total_revenue


if __name__ == "__main__":
    main()
