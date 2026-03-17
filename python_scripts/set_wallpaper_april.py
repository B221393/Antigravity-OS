import ctypes
import os

def set_wallpaper(image_path):
    # Ensure absolute path
    abs_path = os.path.abspath(image_path)
    if not os.path.exists(abs_path):
        print(f"Error: {abs_path} not found.")
        return

    print(f"Setting desktop wallpaper to: {abs_path}")
    # SPI_SETDESKWALLPAPER = 20
    # 3 = SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
    ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
    print("Wallpaper update command sent successfully.")

if __name__ == "__main__":
    target_image = r"c:\Users\Yuto\Desktop\app\dashboard\background_april.png"
    set_wallpaper(target_image)
