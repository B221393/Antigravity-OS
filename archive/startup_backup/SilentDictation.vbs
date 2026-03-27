Set WshShell = CreateObject("WScript.Shell")
' Launch the Python script in the virtual environment without showing a window (0 = hidden)
WshShell.Run "c:\Users\Yuto\Desktop\app\.venv\Scripts\pythonw.exe c:\Users\Yuto\Desktop\app\python_scripts\whisper_type.py", 0, False
MsgBox "Antigravity Voice Assistant (Ghost Mode) が起動しました。Alt キーで録音できます。", 64, "Ghost Mode Started"
