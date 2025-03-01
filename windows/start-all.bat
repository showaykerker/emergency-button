@echo off
echo Starting Sikuli-MQTT Bridge System

echo.
echo Step 1: Starting Sikuli Server...
start "Sikuli Server" cmd /c run-sikuli-server.bat

echo.
echo Waiting for server to start...
timeout /t 5

echo.
echo Step 2: Starting MQTT Bridge...
start "MQTT Bridge" cmd /c python mqtt_to_sikuli_bridge.py

echo.
echo All services started!
echo Closing this window will not stop the started services
echo.