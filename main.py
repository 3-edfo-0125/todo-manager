import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from datetime import datetime
import sqlite3

class TodoApp:
    def __init__(self, root):
        self.root = root
        root.title("ToDoリスト")
        root.geometry("600x300")
        root.resizable(False, False) # ウィンドウサイズ固定

        self.BASE_DIR = Path(__file__).resolve().parent
        self.tasks_path = self.BASE_DIR / "tasks.db"
        self.category_list = ["Python", "GitHub", "執筆", "Instagram", "就活"]
        self.ascending = True

        self.create_widgets()

        query = "SELECT * FROM tasks ORDER BY ID ASC"
        self.task_read(query)

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(side=tk.TOP, pady=10)

        column = ["ID", "カテゴリ", "内容", "登録日", "締切日"]
        self.table = ttk.Treeview(frame, columns=column, height=6)

        # 列の幅
        self.table.column("#0", width=0, stretch="no")
        self.table.column("ID", anchor="center", width=30)
        self.table.column("カテゴリ", anchor="center", width=100)
        self.table.column("内容", anchor="center", width=170)
        self.table.column("登録日", anchor="center", width=120)
        self.table.column("締切日", anchor="center", width=120)

        # ヘッダーテキスト
        self.table.heading("#0", text="")
        self.table.heading("ID", text="ID", anchor="center", command=lambda: self.task_sort("ID"))
        self.table.heading("カテゴリ", text="カテゴリ", anchor="center", command=lambda: self.task_sort("カテゴリ"))
        self.table.heading("内容", text="内容", anchor="center", command=lambda: self.task_sort("内容"))
        self.table.heading("登録日", text="登録日", anchor="center", command=lambda: self.task_sort("登録日"))
        self.table.heading("締切日", text="締切日", anchor="center", command=lambda: self.task_sort("締切日"))

        self.table.bind("<Double-1>", self.task_edit)
        self.table.pack(side=tk.LEFT)

        self.scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.table.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.configure(yscroll=self.scrollbar.set)

        frame2 = tk.Frame(self.root)
        frame2.pack(side=tk.TOP, fill=tk.X, padx=15)

        done_btn = ttk.Button(frame2, text="完了", command=self.task_done)
        done_btn.grid(row=0, column=0)

        delete_btn = ttk.Button(frame2, text="削除", command=self.task_delete)
        delete_btn.grid(row=0, column=1)

        frame3 = tk.Frame(self.root)
        frame3.pack(side=tk.TOP, fill=tk.X, padx=15, pady=15)

        r_label_cat = tk.Label(frame3, text="カテゴリ：")
        r_label_cat.grid(row=1, column=0, sticky="w")

        r_label_cont = tk.Label(frame3, text="内容：")
        r_label_cont.grid(row=1, column=1, sticky="w")

        r_label_dd = tk.Label(frame3, text=r"締切日(Y/m/d H:M)：")
        r_label_dd.grid(row=1, column=2, sticky="w")

        self.r_form_cat = ttk.Combobox(frame3, width=20, values=self.category_list)
        self.r_form_cat.grid(row=2, column=0, sticky="w", padx=5)

        self.r_form_cont = ttk.Entry(frame3, width=45)
        self.r_form_cont.grid(row=2, column=1, sticky="w")

        self.r_form_dd = ttk.Entry(frame3, width=20)
        self.r_form_dd.grid(row=2, column=2, sticky="w", padx=5)

        form_button = ttk.Button(frame3, text="登録", command=self.task_reg)
        form_button.grid(row=3, column=2, sticky="e", padx=5)

    # データ読み込み
    def task_read(self, query):
        task = []
        with sqlite3.connect(self.tasks_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='tasks'")
            result = cur.fetchone()[0]
            if result == 0:
                print("テーブルが見つかりません。新規に作成します。")
                sql = "CREATE TABLE tasks(ID INTEGER PRIMARY KEY AUTOINCREMENT, カテゴリ TEXT, 内容 TEXT, 登録日 TEXT, 締切日 TEXT, 完了有無 INTEGER, 完了日 TEXT)"
                cur.execute(sql)
                conn.commit()
            cur.execute(query)
        
            for row in cur:
                iid = row[0]
                if row[5]:
                    continue
                else:
                    for i in range(0,5):
                        task.append(row[i])
                    for i in range(3,5):
                        dt = datetime.strptime(task[i], "%Y-%m-%d %H:%M")
                        task[i] = dt.strftime("%Y/%m/%d %H:%M")
                    self.table.insert(parent="", index="end", iid=iid, values=task, tags=iid)
                    dd = datetime.strptime(task[4], "%Y/%m/%d %H:%M")
                    diff = dd - datetime.now()
                    if datetime.now() > dd:
                        self.table.tag_configure(iid, background="red")
                    elif diff.days == 0:
                        self.table.tag_configure(iid, background="yellow")
                    else:
                        self.table.tag_configure(iid, background="white")
                    task = []

    # タスクソート
    def task_sort(self, col_name):
        global ascending
        data = []
        with sqlite3.connect(self.tasks_path) as conn:
            cur = conn.cursor()
            if self.ascending:
                query = f"SELECT * FROM tasks ORDER BY {col_name} ASC"
            else:
                query = f"SELECT * FROM tasks ORDER BY {col_name} DESC"
            cur.execute(query)
            self.ascending = not self.ascending

            # 表のクリア
            for child in self.table.get_children():
                self.table.delete(child)

            # データ読み込み
            task = []
            for row in cur:
                iid = row[0]
                if row[5]:
                    continue
                else:
                    for i in range(0,5):
                        task.append(row[i])
                    for i in range(3,5):
                        dt = datetime.strptime(task[i], "%Y-%m-%d %H:%M")
                        task[i] = dt.strftime("%Y/%m/%d %H:%M")
                    self.table.insert(parent="", index="end", iid=iid, values=task, tags=iid)
                    dd = datetime.strptime(task[4], "%Y/%m/%d %H:%M")
                    diff = dd - datetime.now()
                    if datetime.now() > dd:
                        self.table.tag_configure(iid, background="red")
                    elif diff.days == 0:
                        self.table.tag_configure(iid, background="yellow")
                    else:
                        self.table.tag_configure(iid, background="white")
                    task = []

    # タスク完了
    def task_done(self):
        selected_items = self.table.selection()
        selected_iid = int(self.table.focus())
        if not selected_items:
            print("行が選択されていません")
            return

        comp_dt = datetime.now().strftime("%Y-%m-%d %H:%M")

        with sqlite3.connect(self.tasks_path) as conn:
            cur = conn.cursor()

            for item in selected_items:
                cur.execute("UPDATE tasks SET 完了有無 = 1, 完了日 = ? WHERE ID = ?", (comp_dt, item,))
                conn.commit()
                self.table.delete(item)
            
        
    # タスク削除
    def task_delete(self):
        selected_items = self.table.selection()
        selected_iid = int(self.table.focus())
        if not selected_items:
            print("行が選択されていません")
            return
        
        with sqlite3.connect(self.tasks_path) as conn:
            cur = conn.cursor()
            
            for item in selected_items:
                cur.execute("DELETE FROM tasks WHERE ID = ?", (item,))
                conn.commit()
                self.table.delete(item)

    # タスク登録
    def task_reg(self):
        if self.r_form_cat.get() == "":
           print("カテゴリを入力してください")
           return
        elif self.r_form_cont.get() == "":
            print("内容を入力してください")
            return
        elif self.r_form_dd.get() == "":
            print("締切を設定してください")
            return

        dd = self.r_form_dd.get()
        dd = dd.strip().replace("-", "/")
        if " " in dd:
            dt = datetime.strptime(dd, "%Y/%m/%d %H:%M")
        else:
            dt = datetime.strptime(dd, "%Y/%m/%d")

        display_dd = dt.strftime("%Y/%m/%d %H:%M")

        with sqlite3.connect(self.tasks_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT MAX(ID) FROM tasks")
            max_id = cur.fetchone()[0]
            if max_id is None:
                new_id = 1
            else:
                new_id = max_id + 1
            
            t = (new_id, self.r_form_cat.get(), self.r_form_cont.get(), datetime.now().strftime("%Y-%m-%d %H:%M"), dt.strftime("%Y-%m-%d %H:%M"), False, None)
            cur.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?,?)", t)
            conn.commit()

        reg_data = [new_id, self.r_form_cat.get(), self.r_form_cont.get(), datetime.now().strftime("%Y/%m/%d %H:%M"), display_dd]
        dd = datetime.strptime(reg_data[4], "%Y/%m/%d %H:%M")
        diff = dd - datetime.now()

        self.table.insert(parent="", index="end", iid=new_id, values=reg_data, tags=new_id)
        if datetime.now() > dd:
            self.table.tag_configure(new_id, background="red")
        elif diff.days == 0:
            self.table.tag_configure(new_id, background="yellow")
        else:
            self.table.tag_configure(new_id, background="white")

        self.r_form_cat.delete(0, tk.END)
        self.r_form_cont.delete(0, tk.END)
        self.r_form_dd.delete(0, tk.END)

    # タスク編集
    def task_edit(self, event):
        selected = self.table.selection()
        if not selected:
            return

        task_id = self.table.item(selected[0])["values"][0]
        values = self.table.item(selected[0])["values"]

        TodoEditWindow(self.root, task_id, values, self.update_tasks)

    def update_tasks(self, task_id, data):
        with sqlite3.connect(self.tasks_path) as conn:
            cur = conn.cursor()            
            cur.execute('''
                UPDATE tasks
                SET カテゴリ = ?, 内容 = ?, 締切日 = ?
                WHERE ID = ?
            ''', (data[0], data[1], data[3], task_id))
            conn.commit()

        # 表のクリア
        for child in self.table.get_children():
            self.table.delete(child)

        self.task_read("SELECT * FROM tasks ORDER BY ID ASC")

class TodoEditWindow:
    def __init__(self, parent, todo_id, current_values, callback):
        self.top = tk.Toplevel(parent)
        self.top.title("タスク編集")
        self.top.geometry("600x100")

        self.todo_id = todo_id
        self.callback = callback
        self.BASE_DIR = Path(__file__).resolve().parent

        self.create_widgets(current_values, todo_id)

    def create_widgets(self, values, todo_id):
        frame = tk.Frame(self.top)
        frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=15)

        e_label_cat = tk.Label(frame, text="カテゴリ：")
        e_label_cat.grid(row=1, column=0, sticky="w")

        e_label_cont = tk.Label(frame, text="内容：")
        e_label_cont.grid(row=1, column=1, sticky="w")

        e_label_dd = tk.Label(frame, text=r"締切日(Y/m/d H:M)：")
        e_label_dd.grid(row=1, column=2, sticky="w")

        category_list = ["Python", "GitHub", "執筆", "Instagram", "就活"]
        self.e_form_cat = ttk.Combobox(frame, width=20, values=category_list)
        self.e_form_cat.grid(row=2, column=0, sticky="w", padx=5)
        self.e_form_cat.insert(0, values[1])

        self.e_form_cont = ttk.Entry(frame, width=45)
        self.e_form_cont.grid(row=2, column=1, sticky="w")
        self.e_form_cont.insert(0, values[2])

        self.e_form_dd = ttk.Entry(frame, width=20)
        self.e_form_dd.grid(row=2, column=2, sticky="w", padx=5)
        self.e_form_dd.insert(0, values[4])

        e_button = ttk.Button(frame, text="保存", command=lambda: self.save(values[3], todo_id))
        e_button.grid(row=3, columnspan=2, column=2, sticky="e", padx=5)

    def save(self, reg_date, task_id):
        if self.e_form_cat.get() == "":
           print("カテゴリを入力してください")
           return
        elif self.e_form_cont.get() == "":
            print("内容を入力してください")
            return
        elif self.e_form_dd.get() == "":
            print("締切を設定してください")
            return

        dd = self.e_form_dd.get()
        dd = dd.strip().replace("-", "/")
        if " " in dd:
            dt = datetime.strptime(dd, "%Y/%m/%d %H:%M")
        else:
            dt = datetime.strptime(dd, "%Y/%m/%d")

        edit_data = [self.e_form_cat.get(), self.e_form_cont.get(), reg_date, dt.strftime("%Y-%m-%d %H:%M")]

        self.callback(task_id, edit_data)
        self.top.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
