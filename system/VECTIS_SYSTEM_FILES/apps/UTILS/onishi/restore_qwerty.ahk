; ==============================================================================
; QWERTY復元スクリプト
; 大西配列 (Onishi o24) を停止してQWERTY配列に戻す
; ==============================================================================
; 使い方: このファイルをダブルクリックして実行

#NoEnv
#SingleInstance Force
SendMode Input

; AutoHotkeyプロセスを全て停止（大西配列含む）
Process, Close, AutoHotkeyU64.exe
Process, Close, AutoHotkey.exe

; 通知表示
TrayTip, QWERTY復元完了, 大西配列を停止しました。`nキーボードは通常のQWERTY配列に戻りました。, 3, 1

; このスクリプト自身も終了
Sleep, 2000
ExitApp
