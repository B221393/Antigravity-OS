import pyautogui
import time
import os
import ctypes
import sys

# DPI awareness
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

def main():
    # 画像パス（どこから起動しても絶対パスで参照できるようにする）
    base_dir = r"C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES"
    image_path = os.path.join(base_dir, "accept_button.png")
    
    # 画像が無い場合は、作成されるまでひたすら待機（5分に1回確認）
    while not os.path.exists(image_path):
        time.sleep(300)

    pyautogui.FAILSAFE = False

    while True:
        try:
            # 5秒に1回、青いボタンがあるかスキャン
            button_loc = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
            
            if button_loc is not None:
                # ボタンの誤爆（Rejectのクリック等）を防ぐため、物理座標の移動を廃止。
                # よりシンプルで確実な「引き算」として、純粋なキーボードショートカット（Alt+Enter）を1回だけ送信する。
                pyautogui.hotkey('alt', 'enter')

                # 連打防止のため10秒休む
                time.sleep(10)
            else:
                time.sleep(5)
                
        except Exception:
            # エラー時も落ちずに5秒待機して再開
            time.sleep(5)

if __name__ == "__main__":
    main()
