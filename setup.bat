@echo off
setlocal enabledelayedexpansion

:: Colors for output
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set NC=[0m

echo %GREEN%PDF Comparison Tool - Setup Script%NC%
echo ==============================

:: Check Python version
echo.
echo %YELLOW%Checking Python version...%NC%
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %RED%Python is not installed. Please install Python 3.8 or higher.%NC%
    exit /b 1
)

python -c "import sys; assert sys.version_info >= (3,8)" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %RED%Python 3.8 or higher is required.%NC%
    exit /b 1
)

for /f "tokens=*" %%i in ('python -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"') do (
    echo Found Python version: %%i
)

:: Create virtual environment
echo.
echo %YELLOW%Creating virtual environment...%NC%
if exist venv (
    echo Virtual environment already exists.
) else (
    python -m venv venv
    if %ERRORLEVEL% equ 0 (
        echo %GREEN%Virtual environment created successfully.%NC%
    ) else (
        echo %RED%Failed to create virtual environment.%NC%
        exit /b 1
    )
)

:: Activate virtual environment
echo.
echo %YELLOW%Activating virtual environment...%NC%
call venv\Scripts\activate
if %ERRORLEVEL% equ 0 (
    echo %GREEN%Virtual environment activated.%NC%
) else (
    echo %RED%Failed to activate virtual environment.%NC%
    exit /b 1
)

:: Upgrade pip
echo.
echo %YELLOW%Upgrading pip...%NC%
python -m pip install --upgrade pip

:: Install dependencies
echo.
echo %YELLOW%Installing dependencies...%NC%
pip install -r requirements.txt
if %ERRORLEVEL% equ 0 (
    echo %GREEN%Dependencies installed successfully.%NC%
) else (
    echo %RED%Failed to install dependencies.%NC%
    exit /b 1
)

:: Create necessary directories
echo.
echo %YELLOW%Creating necessary directories...%NC%
if not exist data mkdir data
if not exist logs mkdir logs
echo Created necessary directories.

:: Create configuration file
echo.
echo %YELLOW%Setting up configuration...%NC%
if not exist config\settings.yaml (
    copy config\settings.yaml.example config\settings.yaml
    echo %GREEN%Created configuration file from example.%NC%
    echo %YELLOW%Please edit config\settings.yaml with your settings.%NC%
) else (
    echo Configuration file already exists.
)

:: Run setup verification
echo.
echo %YELLOW%Running setup verification...%NC%
python test_setup.py
if %ERRORLEVEL% equ 0 (
    echo.
    echo %GREEN%Setup completed successfully!%NC%
    echo.
    echo To start using the PDF Comparison Tool:
    echo 1. Edit config\settings.yaml with your settings
    echo 2. Activate the virtual environment:
    echo    venv\Scripts\activate
    echo 3. Run the application:
    echo    python src\main.py
) else (
    echo.
    echo %RED%Setup verification failed. Please check the output above for details.%NC%
    exit /b 1
)

:: Create .gitignore
echo.
echo %YELLOW%Creating .gitignore...%NC%
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo venv/
echo ENV/
echo.
echo # Distribution / packaging
echo dist/
echo build/
echo *.egg-info/
echo.
echo # Unit test / coverage reports
echo htmlcov/
echo .tox/
echo .coverage
echo .coverage.*
echo .cache
echo coverage.xml
echo *.cover
echo .pytest_cache/
echo.
echo # Logs
echo logs/
echo *.log
echo.
echo # Database
echo *.db
echo *.sqlite3
echo.
echo # Configuration
echo config/settings.yaml
echo.
echo # IDE
echo .idea/
echo .vscode/
echo *.swp
echo *.swo
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
) > .gitignore

echo %GREEN%Created .gitignore file%NC%

echo.
echo %GREEN%Setup complete!%NC%
echo ==============================
echo Next steps:
echo 1. Edit config\settings.yaml with your settings
echo 2. Set up your Slack webhook URL for notifications
echo 3. Configure your offer and invoice folder paths
echo.
echo To start the application:
echo venv\Scripts\activate
echo python src\main.py

:: Pause to keep the window open
pause

endlocal
