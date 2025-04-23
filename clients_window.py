# clients_window.py

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_PATH = "rental.db"


def open_clients_window():
    window = tk.Toplevel()
    window.title("Клиенты")

    def load_clients():
        tree.delete(*tree.get_children())
        cur.execute("SELECT * FROM Clients")
        for row in cur.fetchall():
            tree.insert("", tk.END, values=row)

    def add_client():
        def save_new_client():
            name = entry_name.get().strip()
            email = entry_email.get().strip()
            if not name or not email:
                messagebox.showwarning("Ошибка", "Пожалуйста, заполните все поля.")
                return
            try:
                cur.execute("INSERT INTO Clients (name, email) VALUES (?, ?)", (name, email))
                conn.commit()
                top.destroy()
                load_clients()
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Клиент с такими данными уже существует.")

        top = tk.Toplevel(window)
        top.title("Добавить клиента")

        tk.Label(top, text="ФИО").grid(row=0, column=0, padx=5, pady=5)
        entry_name = tk.Entry(top)
        entry_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Email").grid(row=1, column=0, padx=5, pady=5)
        entry_email = tk.Entry(top)
        entry_email.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(top, text="Сохранить", command=save_new_client).grid(row=2, column=0, columnspan=2, pady=10)

    def edit_client():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента для редактирования.")
            return
        item = tree.item(selected)
        client_id, name, email = item['values']

        def save_edited_client():
            new_name = entry_name.get().strip()
            new_email = entry_email.get().strip()
            if not new_name or not new_email:
                messagebox.showwarning("Ошибка", "Пожалуйста, заполните все поля.")
                return
            try:
                cur.execute("UPDATE Clients SET name = ?, email = ? WHERE id = ?", (new_name, new_email, client_id))
                conn.commit()
                top.destroy()
                load_clients()
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Клиент с такими данными уже существует.")

        top = tk.Toplevel(window)
        top.title("Редактировать клиента")

        tk.Label(top, text="ФИО").grid(row=0, column=0, padx=5, pady=5)
        entry_name = tk.Entry(top)
        entry_name.insert(0, name)
        entry_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Email").grid(row=1, column=0, padx=5, pady=5)
        entry_email = tk.Entry(top)
        entry_email.insert(0, email)
        entry_email.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(top, text="Сохранить", command=save_edited_client).grid(row=2, column=0, columnspan=2, pady=10)

    def delete_client():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента для удаления.")
            return
        client_id = tree.item(selected)["values"][0]
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого клиента?"):
            # Расторгаем все активные договоры этого клиента
            cur.execute("UPDATE Rentals SET status = 'расторгнут' WHERE client_id = ? AND status = 'активен'", (client_id,))
            conn.commit()
            # Удаляем клиента
            cur.execute("DELETE FROM Clients WHERE id = ?", (client_id,))
            conn.commit()
            load_clients()

    # Интерфейс
    tree = ttk.Treeview(window, columns=("ID", "Name", "Email"), show="headings")
    for col, text in zip(("ID", "Name", "Email"), ("ID", "ФИО", "Email")):
        tree.heading(col, text=text)
        tree.column(col, width=100)
    tree.pack(fill=tk.BOTH, expand=True)

    btn_frame = tk.Frame(window)
    btn_frame.pack(fill=tk.X, pady=5)

    tk.Button(btn_frame, text="Добавить", command=add_client).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Редактировать", command=edit_client).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Удалить", command=delete_client).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Обновить", command=load_clients).pack(side=tk.RIGHT, padx=5)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    load_clients()
