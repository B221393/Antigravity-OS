@echo off
title VECTIS Cleanup - node_modules削除
color 0c
echo ========================================================
echo   🧹 VECTIS CLEANUP: node_modules削除
echo ========================================================
echo.
echo 警告: これにより全てのnode_modulesフォルダが削除されます。
echo アプリを再度使用する際は npm install が必要です。
echo.
pause

echo.
echo 削除中...
for /d /r "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps" %%d in (node_modules) do (
    if exist "%%d" (
        echo 削除: %%d
        rmdir /s /q "%%d"
    )
)

echo.
echo ========================================================
echo   ✅ 完了！node_modulesを全て削除しました。
echo ========================================================
pause
