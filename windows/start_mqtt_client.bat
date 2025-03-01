@echo off
echo Starting MQTT to LINE Bridge...
echo.

:: 切換到批處理檔案所在目錄
cd /d %~dp0

:: 啟動 MQTT 客戶端
echo Starting MQTT client...
python mqtt_client.py

:: 如果程式意外結束，讓視窗保持開啟
if %errorlevel% neq 0 (
  echo.
  echo Program ended with error code: %errorlevel%
  pause
)