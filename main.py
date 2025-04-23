import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

from clients_window import open_clients_window
from spaces_window import open_spaces_window
from rentals_window import open_rentals_window

DB_NAME = "rental.db"

def calculate_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    today = datetime.now().date()

    # 1. Суммарная занятая площадь
    cursor.execute("""
        SELECT SUM(area) FROM Spaces 
        WHERE status = 'занято'
    """)
    total_occupied_area = cursor.fetchone()[0] or 0

    # 2. Суммарная прибыль
    cursor.execute("""
        SELECT SUM(monthly_price) FROM Rentals 
        WHERE status = 'активен'
    """)
    total_income = cursor.fetchone()[0] or 0

    # 3. Количество свободных комнат
    cursor.execute("""
        SELECT COUNT(*) FROM Spaces 
        WHERE status = 'свободно'
    """)
    free_rooms = cursor.fetchone()[0]

    # 4. Количество уникальных клиентов
    cursor.execute("SELECT COUNT(*) FROM Clients")
    unique_clients = cursor.fetchone()[0]

    # 5. Кол-во договоров по статусам
    cursor.execute("SELECT COUNT(*) FROM Rentals WHERE status = 'активен'")
    active = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Rentals WHERE status = 'завершён'")
    completed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Rentals WHERE status = 'расторгнут'")
    terminated = cursor.fetchone()[0]

    # 6. Прибыль: макс/мин/средняя/сумма (по завершённым договорам)
    cursor.execute("""
        SELECT MAX(monthly_price), MIN(monthly_price), AVG(monthly_price), SUM(monthly_price)
        FROM Rentals
        WHERE status = 'завершён'
    """)
    max_income, min_income, avg_income, sum_income = cursor.fetchone()

    # 7. Площадь макс/мин/средняя/сумма по активным договорам
    cursor.execute("""
        SELECT MAX(Spaces.area), MIN(Spaces.area), AVG(Spaces.area), SUM(Spaces.area)
        FROM Rentals
        JOIN Spaces ON Rentals.space_id = Spaces.id
        WHERE Rentals.status = 'активен'
    """)
    max_area_rented, min_area_rented, avg_area_rented, sum_area_rented = cursor.fetchone()

    # 8. Площадь макс/мин/средняя/сумма всех помещений
    cursor.execute("SELECT MAX(area), MIN(area), AVG(area), SUM(area) FROM Spaces")
    max_area, min_area, avg_area, sum_area = cursor.fetchone()

    conn.close()

    # Обновление меток
    stats = {
        "Число уникальных клиентов": str(unique_clients),
        "Договоры": f"Активны: {active}, Завершены: {completed}, Расторгнуты: {terminated}",
        "Свободные помещения": str(free_rooms),
        "Текущая занятая площадь": f"{total_occupied_area:.2f} м²",
        "Текущая суммарная прибыль": f"{total_income:.2f} руб.",
        "Прибыль (макс/мин/средн/сумм)": f"{max_income or 0:.2f} / {min_income or 0:.2f} / {avg_income or 0:.2f} / {sum_income or 0:.2f} руб.",
        "Занятая площадь (макс/мин/средн/сумм)": f"{max_area_rented or 0:.2f} / {min_area_rented or 0:.2f} / {avg_area_rented or 0:.2f} / {sum_area_rented or 0:.2f} м²",
        "Общая площадь (макс/мин/средн/сумм)": f"{max_area or 0:.2f} / {min_area or 0:.2f} / {avg_area or 0:.2f} / {sum_area or 0:.2f} м²",
    }

    for key, value in stats.items():
        if key in stats_labels:
            stats_labels[key].config(text=value)


# --- Главное окно ---
root = tk.Tk()
root.title("Учет аренды помещений")
root.geometry("700x500")

title_label = tk.Label(root, text="Статистика аренды", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

stats_labels = {}

for key in [
    "Число уникальных клиентов",
    "Договоры",
    "Свободные помещения",
    "Текущая занятая площадь",
    "Текущая суммарная прибыль",
    "Прибыль (макс/мин/средн/сумм)",
    "Занятая площадь (макс/мин/средн/сумм)",
    "Общая площадь (макс/мин/средн/сумм)"
]:
    row = tk.Frame(frame)
    row.pack(fill=tk.X, pady=2)
    label_name = tk.Label(row, text=key + ":", width=35, anchor="w")
    label_name.pack(side=tk.LEFT)
    label_value = tk.Label(row, text="", anchor="w")
    label_value.pack(side=tk.LEFT)
    stats_labels[key] = label_value

# Кнопки
btn_frame = tk.Frame(root)
btn_frame.pack(pady=15)

tk.Button(btn_frame, text="Клиенты", width=15, command=open_clients_window).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Помещения", width=15, command=open_spaces_window).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Договоры аренды", width=15, command=open_rentals_window).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Обновить", width=15, command=calculate_stats).pack(side=tk.RIGHT, padx=5)

# Стартовая загрузка
calculate_stats()

root.mainloop()
