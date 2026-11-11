import sqlite3
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

COUNT = 30
category = ["Python", "GitHub", "執筆", "Instagram", "就活"]
contents = ["test1", "test2", "test3", "test4", "test5"]
today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
three_month_before = today - relativedelta(months=3)
date_range = pd.date_range(start=three_month_before, end=today)
date_list = date_range.tolist()

dbname = "dummy_tasks.db"
conn = sqlite3.connect(dbname)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS tasks")

cur.execute(
    "CREATE TABLE tasks(ID INTEGER PRIMARY KEY AUTOINCREMENT, カテゴリ TEXT, 内容 TEXT, 登録日 TEXT, 締切日 TEXT, 完了有無 INTEGER, 完了日 TEXT)")

for i in range(COUNT):
    s_cat = random.choice(category)
    s_cont = random.choice(contents)
    s_rday = random.choice(date_list)
    s_dday = s_rday + timedelta(days=random.randint(3,90))

    s_rday = s_rday.strftime("%Y-%m-%d %H:%M")
    s_dday = s_dday.strftime("%Y-%m-%d %H:%M")

    tf = random.randint(0,1)
    if tf == 1 :
        date_range2 = pd.date_range(start=s_rday, end=today)
        s_eday = random.choice(date_range2.tolist()).strftime("%Y-%m-%d %H:%M")
    else:
        s_eday = None

    sql = "INSERT INTO tasks (カテゴリ, 内容, 登録日, 締切日, 完了有無, 完了日) VALUES(?,?,?,?,?,?)"
    data = (s_cat, s_cont, s_rday, s_dday, tf, s_eday)
    cur.execute(sql, data)
    conn.commit()

conn.close()