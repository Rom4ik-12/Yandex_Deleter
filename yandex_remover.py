import os
import shutil
import subprocess
import winreg
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import ctypes

# Проверка прав администратора
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Функция для обнаружения Яндекс.Браузера
def detect_yandex_browser(custom_path=None):
    # Если пользователь указал путь, проверяем его
    if custom_path and os.path.exists(custom_path):
        return True

    # Проверка наличия папок по умолчанию
    paths = [
        os.path.expandvars("%ProgramFiles%\\Yandex\\YandexBrowser"),
        os.path.expandvars("%LocalAppData%\\Yandex\\YandexBrowser")
    ]
    for path in paths:
        if os.path.exists(path):
            return True

    # Проверка наличия записей в реестре
    reg_paths = [
        "SOFTWARE\\Yandex\\YandexBrowser",
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\YandexBrowser"
    ]
    for path in reg_paths:
        try:
            winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            return True
        except FileNotFoundError:
            pass
        try:
            winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
            return True
        except FileNotFoundError:
            pass

    return False

# Функция для остановки процессов Яндекс.Браузера
def kill_processes():
    try:
        # Проверяем, существует ли процесс browser.exe
        result = subprocess.run(["tasklist", "/fi", "imagename eq browser.exe"], capture_output=True, text=True)
        if "browser.exe" in result.stdout:
            subprocess.run(["taskkill", "/f", "/im", "browser.exe"], check=True)
            return True
        else:
            return True  # Процесс не найден, пропускаем
    except subprocess.CalledProcessError:
        return False

# Функция для удаления папок
def remove_folders(custom_path=None):
    paths = []
    if custom_path:
        paths.append(custom_path)
    else:
        paths.extend([
            os.path.expandvars("%ProgramFiles%\\Yandex\\YandexBrowser"),
            os.path.expandvars("%LocalAppData%\\Yandex\\YandexBrowser")
        ])
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)

# Функция для удаления записей реестра
def remove_registry_entries():
    reg_paths = [
        "SOFTWARE\\Yandex\\YandexBrowser",
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\YandexBrowser"
    ]
    for path in reg_paths:
        try:
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, path)
        except FileNotFoundError:
            pass
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
        except FileNotFoundError:
            pass

# Функция для удаления ярлыков
def remove_shortcuts():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    start_menu = os.path.join(os.path.expandvars("%ProgramData%"), "Microsoft\\Windows\\Start Menu\\Programs")
    for folder in [desktop, start_menu]:
        shortcut = os.path.join(folder, "Yandex Browser.lnk")
        if os.path.exists(shortcut):
            os.remove(shortcut)

# Плавное заполнение прогресс-бара
def animate_progress_bar(target_value, current_value=0, step=1):
    if current_value < target_value:
        progress_bar.set(current_value / 100)
        root.after(20, animate_progress_bar, target_value, current_value + step)
    else:
        progress_bar.set(target_value / 100)

# Плавное изменение текста
def fade_text(label, new_text, opacity=0):
    if opacity < 1:
        opacity += 0.1
        label.configure(text=new_text, text_color=("#000000", "#FFFFFF")[int(opacity >= 0.5)])  # Изменение цвета текста
        root.after(50, fade_text, label, new_text, opacity)
    else:
        label.configure(text=new_text)

# Основная функция удаления
def remove_yandex_browser():
    custom_path = path_entry.get().strip()  # Получаем путь, указанный пользователем
    if custom_path and not os.path.exists(custom_path):
        messagebox.showerror("Ошибка", "Указанный путь не существует.")
        return

    # Делаем кнопку неактивной
    start_button.configure(state="disabled", text="Удаление...", fg_color="gray", hover_color="gray")

    # Шаг 1: Остановка процессов
    fade_text(progress_label, "Остановка процессов Яндекс.Браузера...")
    animate_progress_bar(25)
    if not kill_processes():
        messagebox.showerror("Ошибка", "Не удалось остановить процессы Яндекс.Браузера.")
        start_button.configure(state="normal", text="Начать удаление", fg_color="red", hover_color="darkred")  # Восстанавливаем кнопку
        return
    if not messagebox.askyesno("Подтверждение", "Процессы остановлены. Перейти к следующему шагу?"):
        start_button.configure(state="normal", text="Начать удаление", fg_color="red", hover_color="darkred")  # Восстанавливаем кнопку
        return

    # Шаг 2: Удаление папок
    fade_text(progress_label, "Удаление файлов Яндекс.Браузера...")
    animate_progress_bar(50)
    remove_folders(custom_path)
    if not messagebox.askyesno("Подтверждение", "Файлы удалены. Перейти к следующему шагу?"):
        start_button.configure(state="normal", text="Начать удаление", fg_color="red", hover_color="darkred")  # Восстанавливаем кнопку
        return

    # Шаг 3: Удаление записей реестра
    fade_text(progress_label, "Удаление записей реестра...")
    animate_progress_bar(75)
    remove_registry_entries()
    if not messagebox.askyesno("Подтверждение", "Записи реестра удалены. Перейти к следующему шагу?"):
        start_button.configure(state="normal", text="Начать удаление", fg_color="red", hover_color="darkred")  # Восстанавливаем кнопку
        return

    # Шаг 4: Удаление ярлыков
    fade_text(progress_label, "Удаление ярлыков...")
    animate_progress_bar(100)
    remove_shortcuts()
    messagebox.showinfo("Успех", "Яндекс.Браузер успешно удален.")
    root.quit()

# Функция для выбора папки
def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, folder)

# Функция для запуска процесса удаления
def start_removal():
    custom_path = path_entry.get().strip()
    if detect_yandex_browser(custom_path):
        if messagebox.askyesno("Подтверждение", "Яндекс.Браузер обнаружен. Вы уверены, что хотите удалить его?"):
            remove_yandex_browser()
    else:
        messagebox.showinfo("Информация", "Яндекс.Браузер не обнаружен на вашем компьютере.")
        root.quit()

# Создание GUI
def create_gui():
    global root, progress_bar, progress_label, start_button, path_entry

    # Настройка темы customtkinter
    ctk.set_appearance_mode("System")  # Режим темы (System, Dark, Light)
    ctk.set_default_color_theme("blue")  # Цветовая тема

    root = ctk.CTk()
    root.title("Удаление Яндекс.Браузера")
    root.geometry("500x700")  # Окно выше, чем шире (500x700)

    # Установка иконки окна
    try:
        root.iconbitmap("icon.ico")  # Укажите путь к файлу иконки
    except Exception as e:
        print(f"Ошибка загрузки иконки: {e}")

    # Настройка шрифтов
    title_font = ("Segoe UI", 24, "bold")  # Заголовок
    text_font = ("Segoe UI", 16)  # Основной текст
    button_font = ("Segoe UI", 14, "bold")  # Кнопки

    # Заголовок
    label = ctk.CTkLabel(root, text="Удаление Яндекс.Браузера", font=title_font)
    label.pack(pady=20)

    # Поле для ввода пути
    path_frame = ctk.CTkFrame(root)
    path_frame.pack(pady=10)

    path_entry = ctk.CTkEntry(path_frame, width=350, font=text_font)
    path_entry.pack(side=tk.LEFT, padx=10)

    browse_button = ctk.CTkButton(path_frame, text="Обзор", command=browse_folder, font=button_font)
    browse_button.pack(side=tk.LEFT)

    # Прогресс-бар
    progress_bar = ctk.CTkProgressBar(root, orientation="horizontal", width=400)
    progress_bar.set(0)
    progress_bar.pack(pady=20)

    # Текстовое описание прогресса
    progress_label = ctk.CTkLabel(root, text="Ожидание запуска...", font=text_font)
    progress_label.pack(pady=20)

    # Кнопка "Начать удаление"
    start_button = ctk.CTkButton(root, text="Начать удаление", command=start_removal, fg_color="red", hover_color="darkred", font=button_font)
    start_button.pack(pady=30)

    # Кнопка "Выйти"
    exit_button = ctk.CTkButton(root, text="Выйти", command=root.quit, fg_color="gray", hover_color="darkgray", font=button_font)
    exit_button.pack(pady=20)

    # Проверка прав администратора
    if not is_admin():
        messagebox.showerror("Ошибка", "Программа требует прав администратора. Запустите ее от имени администратора.")
        root.quit()

    root.mainloop()

# Запуск приложения
if __name__ == "__main__":
    create_gui()