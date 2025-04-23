import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_PATH = "rental.db"

def open_rentals_window():
    window = tk.Toplevel()
    window.title("Договоры аренды")

    def load_rentals():
        tree.delete(*tree.get_children())

        # Обновление статусов по дате
        today = datetime.now().date()
        cur.execute("UPDATE Rentals SET status = 'завершён' WHERE status = 'активен' AND end_date < ?", (today,))
        conn.commit()

        # Освобождение помещений
        cur.execute(""" 
            SELECT space_id FROM Rentals
            WHERE status IN ('завершён', 'расторгнут')
        """)
        freed_spaces = {row[0] for row in cur.fetchall()}
        for space_id in freed_spaces:
            cur.execute("SELECT COUNT(*) FROM Rentals WHERE space_id = ? AND status = 'активен'", (space_id,))
            if cur.fetchone()[0] == 0:
                cur.execute("UPDATE Spaces SET status = 'свободно' WHERE id = ?", (space_id,))
        conn.commit()

        cur.execute("SELECT * FROM Rentals")
        for row in cur.fetchall():
            tree.insert("", tk.END, values=row)

    def get_client_ids():
        cur.execute("SELECT id, name FROM Clients")
        return [(row[0], row[1]) for row in cur.fetchall()]

    def get_space_ids():
        cur.execute("SELECT id, room_number FROM Spaces WHERE status = 'свободно'")
        return [(row[0], f"Room {row[1]}") for row in cur.fetchall()]

    def add_rental():
        def save_new():
            try:
                cid = client_combobox.get().split(" ")[0]
                sid = space_combobox.get().split(" ")[0]
                start = entry_start.get()
                end = entry_end.get()
                price = float(entry_price.get())
                status = status_var.get()

                # Проверка на существование клиента и помещения
                cur.execute("SELECT 1 FROM Clients WHERE id = ?", (cid,))
                if not cur.fetchone():
                    messagebox.showerror("Ошибка", "Клиент не найден.")
                    return

                cur.execute("SELECT 1 FROM Spaces WHERE id = ?", (sid,))
                if not cur.fetchone():
                    messagebox.showerror("Ошибка", "Помещение не найдено.")
                    return

                if price < 0:
                    messagebox.showerror("Ошибка", "Цена не может быть отрицательной.")
                    return

                # Проверка формата дат
                start_date = datetime.strptime(start, "%Y-%m-%d").date()
                end_date = datetime.strptime(end, "%Y-%m-%d").date()
                if end_date <= start_date:
                    messagebox.showerror("Ошибка", "Дата окончания должна быть позже даты начала.")
                    return

                cur.execute("""
                    INSERT INTO Rentals (client_id, space_id, start_date, end_date, monthly_price, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (cid, sid, start, end, price, status))
                conn.commit()

                # Занять помещение
                if status == "активен":
                    cur.execute("UPDATE Spaces SET status = 'занято' WHERE id = ?", (sid,))
                    conn.commit()

                top.destroy()
                load_rentals()

            except ValueError:
                messagebox.showerror("Ошибка", "Проверьте правильность ввода.")

        top = tk.Toplevel(window)
        top.title("Добавить договор")

        labels = ["Клиент", "Помещение", "Дата начала (ГГГГ-ММ-ДД)", "Дата окончания", "Цена", "Статус"]
        entries = []

        # Выбор клиента из списка
        tk.Label(top, text=labels[0]).grid(row=0, column=0, padx=5, pady=5)
        client_combobox = ttk.Combobox(top, values=[f"{client[0]} {client[1]}" for client in get_client_ids()], state="readonly")
        client_combobox.grid(row=0, column=1, padx=5, pady=5)
        entries.append(client_combobox)

        # Выбор помещения из списка
        tk.Label(top, text=labels[1]).grid(row=1, column=0, padx=5, pady=5)
        space_combobox = ttk.Combobox(top, values=[f"{space[0]} {space[1]}" for space in get_space_ids()], state="readonly")
        space_combobox.grid(row=1, column=1, padx=5, pady=5)
        entries.append(space_combobox)

        # Дата начала
        tk.Label(top, text=labels[2]).grid(row=2, column=0, padx=5, pady=5)
        entry_start = tk.Entry(top)
        entry_start.grid(row=2, column=1, padx=5, pady=5)
        entries.append(entry_start)

        # Дата окончания
        tk.Label(top, text=labels[3]).grid(row=3, column=0, padx=5, pady=5)
        entry_end = tk.Entry(top)
        entry_end.grid(row=3, column=1, padx=5, pady=5)
        entries.append(entry_end)

        # Цена
        tk.Label(top, text=labels[4]).grid(row=4, column=0, padx=5, pady=5)
        entry_price = tk.Entry(top)
        entry_price.grid(row=4, column=1, padx=5, pady=5)
        entries.append(entry_price)

        # Выбор статуса
        tk.Label(top, text=labels[5]).grid(row=5, column=0, padx=5, pady=5)
        status_var = tk.StringVar(value="активен")
        status_menu = ttk.Combobox(top, textvariable=status_var, values=["активен", "завершён", "расторгнут"], state="readonly")
        status_menu.grid(row=5, column=1, padx=5, pady=5)

        tk.Button(top, text="Сохранить", command=save_new).grid(row=6, column=0, columnspan=2, pady=10)

    def edit_rental():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите договор для редактирования.")
            return
        item = tree.item(selected)
        rid, cid, sid, start, end, price, status = item["values"]

        if status != "активен":
            messagebox.showerror("Ошибка", "Редактировать можно только активные договоры.")
            return

        def save_edit():
            try:
                new_status = status_var.get()
                cur.execute("UPDATE Rentals SET status = ? WHERE id = ?", (new_status, rid))
                conn.commit()

                if new_status in ("завершён", "расторгнут"):
                    cur.execute("SELECT COUNT(*) FROM Rentals WHERE space_id = ? AND status = 'активен'", (sid,))
                    if cur.fetchone()[0] == 0:
                        cur.execute("UPDATE Spaces SET status = 'свободно' WHERE id = ?", (sid,))
                        conn.commit()

                top.destroy()
                load_rentals()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        top = tk.Toplevel(window)
        top.title("Редактировать договор")

        tk.Label(top, text="Изменить статус").grid(row=0, column=0, padx=5, pady=5)
        status_var = tk.StringVar(value=status)
        status_menu = ttk.Combobox(top, textvariable=status_var, values=["активен", "завершён", "расторгнут"], state="readonly")
        status_menu.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(top, text="Сохранить", command=save_edit).grid(row=1, column=0, columnspan=2, pady=10)

    def delete_rental():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите договор для удаления.")
            return
        item = tree.item(selected)
        rid, sid, status = item["values"][0], item["values"][2], item["values"][6]

        if status == "активен":
            messagebox.showerror("Ошибка", "Удалить можно только завершённые или расторгнутые договоры.")
            return

        if messagebox.askyesno("Подтверждение", "Удалить договор?"):
            cur.execute("DELETE FROM Rentals WHERE id = ?", (rid,))
            conn.commit()

            # Освобождаем помещение, если больше нет активных договоров
            cur.execute("SELECT COUNT(*) FROM Rentals WHERE space_id = ? AND status = 'активен'", (sid,))
            if cur.fetchone()[0] == 0:
                cur.execute("UPDATE Spaces SET status = 'свободно' WHERE id = ?", (sid,))
                conn.commit()

            load_rentals()

    tree = ttk.Treeview(window, columns=("ID", "ClientID", "SpaceID", "Start", "End", "Price", "Status"), show="headings")
    headers = ["ID", "Клиент", "Помещение", "Начало", "Окончание", "Цена", "Статус"]
    for col, text in zip(tree["columns"], headers):
        tree.heading(col, text=text)
        tree.column(col, width=100)
    tree.pack(fill=tk.BOTH, expand=True)


    btn_frame = tk.Frame(window)
    btn_frame.pack(fill=tk.X, pady=5)

    tk.Button(btn_frame, text="Добавить", command=add_rental).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Редактировать", command=edit_rental).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Удалить", command=delete_rental).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Обновить", command=load_rentals).pack(side=tk.RIGHT, padx=5)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    load_rentals()
