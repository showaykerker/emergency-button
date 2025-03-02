@echo off

:: Set UTF-8 code page
chcp 65001 > nul

echo 檢查 Ubuntu VM 是否啟動中...

:: Set the IP address of your Ubuntu VM
set VM_IP=192.168.108.128
set VM_USER=user
set VM_PASS=0

:: Check if the VM is responding to ping
ping -n 1 -w 1000 %VM_IP% >nul
if %errorlevel% neq 0 (
    echo 找不到 Ubuntu VM，請開啟 VMware 並開啟 Ubuntu
    pause
    exit /b 1
)

echo 找到 Ubuntu VM，現在檢查MQTT Port是否有被開啟

:: Use PowerShell to check if port 1883 is open (typical MQTT port)
PowerShell -Command "if(Test-NetConnection %VM_IP% -Port 1883 -WarningAction SilentlyContinue -InformationLevel Quiet){exit 0}else{exit 1}"

if %errorlevel% neq 0 (
    echo 沒辦法存取 MQTT Port，請確認Ubuntu VM 有被開啟。如果已經開啟，請Player → Power → Restart Guest。
    pause
    exit /b 1
)

echo 確認 MQTT Port 可以存取

:: Try a simpler approach to check if LINE is running
echo 檢查 LINE 是否已經開啟...
wmic process where "name='LINE.exe'" get name 2>nul | find "LINE.exe" >nul
if %errorlevel% neq 0 (
    echo LINE 尚未開啟。請先開啟 LINE 再繼續。
    pause
    exit /b 1
) else (
    echo LINE 已經開啟
)

echo 檢查完成。
echo.

:: Change to the batch file's directory
cd /d %~dp0

:: Start main.py
echo 開啟主程式
python main.py

:: If the program exits unexpectedly, keep the window open
if %errorlevel% neq 0 (
  echo.
  echo Program ended with error code: %errorlevel%
  pause
)