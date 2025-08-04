import csv
import os
import django
from datetime import datetime

# 1. 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zr.settings')
django.setup()

from polls.models import Stock  # 替换为你的 app 和模型名

# 2. 读取 CSV 并写入数据库
with open("dataset.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        date = datetime.strptime(row['Date'], "%Y-%m-%d").date()
        Stock.objects.update_or_create(
            date=date,
            defaults={
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "last": float(row['Last']),
                "close": float(row['Close']),
                "total_trade_quantity": int(row['Total Trade Quantity'].replace(",", "")),
                "turnover_lacs": float(row['Turnover (Lacs)']),
            }
        )
print("导入完成！")
