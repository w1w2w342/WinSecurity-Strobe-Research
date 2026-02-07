import ctypes
import os
import sys
import time
import threading


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def start_crazy_wallpapers():
    # Список путей к картинкам
    # Важно: используй контрастные картинки (белая, черная, красная)
    images = [
        os.path.abspath(resource_path("img1.png")),
        os.path.abspath(resource_path("img2.png")),
        os.path.abspath(resource_path("img3.png")),
        os.path.abspath(resource_path("img4.png")),
        os.path.abspath(resource_path("img5.png")),
        os.path.abspath(resource_path("img6.png")),
        os.path.abspath(resource_path("img7.png")),
        os.path.abspath(resource_path("img9.png")),
        os.path.abspath(resource_path("img10.png")),
        os.path.abspath(resource_path("img11.png")),
        os.path.abspath(resource_path("img12.png")),
        os.path.abspath(resource_path("img13.png")),
    ]

    # Кэшируем вызов функции для скорости
    set_wallpaper = ctypes.windll.user32.SystemParametersInfoW

    i = 0
    while True:
        # Меняем обои без лишних проверок
        # 20 = SPI_SETDESKWALLPAPER
        # Последний параметр 0 (вместо 3) ускоряет работу, так как не ждет записи в реестр
        set_wallpaper(20, 0, images[i % len(images)], 0)

        i += 1
        # Задержка 0.05 сек — это 20 смен обоев в секунду
        time.sleep(0.05)


def run_in_background():
    thread = threading.Thread(target=start_crazy_wallpapers, daemon=True)
    thread.start()