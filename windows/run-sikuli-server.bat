@echo off
echo Compiling and running Sikuli Server...

set SIKULI_JAR=.\sikulixapi-2.0.5-win.jar
set PORT=5000
set SCRIPT_FOLDER=.\execution.sikuli
set THREADS=2

if not exist %SIKULI_JAR% (
    echo Error: Sikuli JAR file not found: %SIKULI_JAR%
    exit /b 1
)

if not exist %SCRIPT_FOLDER% (
    echo Error: Script folder not found: %SCRIPT_FOLDER%
    exit /b 1
)

echo.
echo Compiling SikuliServer.java...
javac -Xlint:deprecation -cp %SIKULI_JAR% SikuliServer.java

if %ERRORLEVEL% neq 0 (
    echo Compilation failed!
    exit /b 1
)

echo.
echo Compiled successfully!
echo Starting Sikuli Server with:
echo - Port: %PORT%
echo - Script folder: %SCRIPT_FOLDER%
echo - Thread pool size: %THREADS%
echo.

java -cp .;%SIKULI_JAR% SikuliServer %PORT% %SCRIPT_FOLDER% %THREADS%

echo Server stopped