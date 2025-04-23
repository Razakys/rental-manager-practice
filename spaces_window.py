# spaces_window.py

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3

DB_PATH = "rental.db"


def open_spaces_window():
    window = tk.Toplevel()
    window.title("Помещения")

    def load_spaces():
        tree.delete(*tree.get_children())
        cur.execute("SELECT * FROM Spaces")
        for row in cur.fetchall():
            tree.insert("", tk.END, values=row)

    def add_space():
        def save_new_space():
            try:
                number = int(entry_number.get())
                area = float(entry_area.get())
                location = entry_location.get().strip()
                status = status_var.get()

                if number < 0 or area < 0 or not location:
                    messagebox.showwarning("Ошибка", "Проверьте введённые данные.")
                    return

                cur.execute("""
                    INSERT INTO Spaces (room_number, area, location, status)
                    VALUES (?, ?, ?, ?)
                """, (number, area, location, status))
                conn.commit()
                top.destroy()
                load_spaces()
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат чисел.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Помещение с таким номером и локацией уже существует.")

        top = tk.Toplevel(window)
        top.title("Добавить помещение")

        tk.Label(top, text="Номер помещения").grid(row=0, column=0, padx=5, pady=5)
        entry_number = tk.Entry(top)
        entry_number.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Площадь").grid(row=1, column=0, padx=5, pady=5)
        entry_area = tk.Entry(top)
        entry_area.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(top, text="Местоположение").grid(row=2, column=0, padx=5, pady=5)
        entry_location = tk.Entry(top)
        entry_location.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(top, text="Статус").grid(row=3, column=0, padx=5, pady=5)
        status_var = tk.StringVar(value="свободно")
        status_menu = ttk.Combobox(top, textvariable=status_var, values=["свободно", "занято"], state="readonly")
        status_menu.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(top, text="Сохранить", command=save_new_space).grid(row=4, column=0, columnspan=2, pady=10)

    def edit_space():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите помещение для редактирования.")
            return
        item = tree.item(selected)
        space_id, number, area, location, status = item["values"]

        def save_edited_space():
            try:
                new_number = int(entry_number.get())
                new_area = float(entry_area.get())
                new_location = entry_location.get().strip()
                new_status = status_var.get()

                if new_number < 0 or new_area < 0 or not new_location:
                    messagebox.showwarning("Ошибка", "Проверьте введённые данные.")
                    return

                # Проверка: если есть активный договор, нельзя делать помещение "свободным"
                cur.execute("SELECT COUNT(*) FROM Rentals WHERE space_id = ? AND status = 'активен'", (space_id,))
                active_count = cur.fetchone()[0]
                if active_count > 0 and new_status == "свободно":
                    messagebox.showerror("Ошибка", "Нельзя освободить помещение с активным договором.")
                    return

                # Если всё ок — обновляем
                cur.execute("""
                    UPDATE Spaces SET room_number = ?, area = ?, location = ?, status = ?
                    WHERE id = ?
                """, (new_number, new_area, new_location, new_status, space_id))
                conn.commit()
                top.destroy()
                load_spaces()
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат чисел.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Помещение с таким номером и локацией уже существует.")

        top = tk.Toplevel(window)
        top.title("Редактировать помещение")

        tk.Label(top, text="Номер помещения").grid(row=0, column=0, padx=5, pady=5)
        entry_number = tk.Entry(top)
        entry_number.insert(0, number)
        entry_number.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Площадь").grid(row=1, column=0, padx=5, pady=5)
        entry_area = tk.Entry(top)
        entry_area.insert(0, area)
        entry_area.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(top, text="Местоположение").grid(row=2, column=0, padx=5, pady=5)
        entry_location = tk.Entry(top)
        entry_location.insert(0, location)
        entry_location.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(top, text="Статус").grid(row=3, column=0, padx=5, pady=5)
        status_var = tk.StringVar(value=status)
        status_menu = ttk.Combobox(top, textvariable=status_var, values=["свободно", "занято"], state="readonly")
        status_menu.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(top, text="Сохранить", command=save_edited_space).grid(row=4, column=0, columnspan=2, pady=10)

    def delete_space():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите помещение для удаления.")
            return
        space_id = tree.item(selected)["values"][0]
        cur.execute("SELECT COUNT(*) FROM Rentals WHERE space_id = ? AND status = 'активен'", (space_id,))
        if cur.fetchone()[0] > 0:
            messagebox.showerror("Ошибка", "Нельзя удалить помещение, по которому есть договоры.")
            return
        if messagebox.askyesno("Подтверждение", "Удалить выбранное помещение?"):
            cur.execute("DELETE FROM Spaces WHERE id = ?", (space_id,))
            conn.commit()
            load_spaces()

    # Интерфейс
    tree = ttk.Treeview(window, columns=("ID", "Room", "Area", "Location", "Status"), show="headings")
    for col, text in zip(("ID", "Room", "Area", "Location", "Status"), ("ID", "Номер", "Площадь", "Локация", "Статус")):
        tree.heading(col, text=text)
        tree.column(col, width=100)
    tree.pack(fill=tk.BOTH, expand=True)

    btn_frame = tk.Frame(window)
    btn_frame.pack(fill=tk.X, pady=5)

    tk.Button(btn_frame, text="Добавить", command=add_space).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Редактировать", command=edit_space).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Удалить", command=delete_space).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Обновить", command=load_spaces).pack(side=tk.RIGHT, padx=5)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    load_spaces()
