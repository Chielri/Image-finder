@echo off
REM Build script for Windows — packages the app with bundled Poppler.
REM Run from the project root: scripts\build_windows.bat

setlocal enabledelayedexpansion

echo ============================================
echo  Document Image Search — Windows Build
echo ============================================

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+ and add it to PATH.
    exit /b 1
)

REM Step 1: Install Python dependencies
echo.
echo [1/4] Installing Python dependencies...
pip install -r backend\requirements.txt
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    exit /b 1
)

REM Step 2: Download Poppler binaries
echo.
echo [2/4] Downloading Poppler binaries for Windows...
python scripts\download_poppler_windows.py
if errorlevel 1 (
    echo ERROR: Failed to download Poppler.
    exit /b 1
)

REM Step 3: Build frontend (optional — skip if frontend_dist already exists)
if exist backend\frontend_dist (
    echo.
    echo [3/4] Frontend build already exists, skipping...
) else (
    echo.
    echo [3/4] Building frontend...
    if exist frontend\package.json (
        pushd frontend
        call npm install
        call npm run build
        popd
        if exist frontend\dist (
            xcopy /E /I /Y frontend\dist backend\frontend_dist
        ) else (
            echo WARNING: Frontend build did not produce frontend/dist.
        )
    ) else (
        echo WARNING: No frontend/package.json found, skipping frontend build.
    )
)

REM Step 4: Run PyInstaller
echo.
echo [4/4] Building executable with PyInstaller...
pyinstaller --clean --noconfirm pyinstaller.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    exit /b 1
)

echo.
echo ============================================
echo  Build complete!
echo  Output: dist\DocumentImageSearch\
echo  Run:    dist\DocumentImageSearch\DocumentImageSearch.exe
echo ============================================
