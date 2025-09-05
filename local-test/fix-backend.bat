@echo off
echo ========================================
echo Fixing Backend Dependencies
echo ========================================

cd /d "%~dp0\.."
cd backend

echo 🔄 Activating virtual environment...
call venv\Scripts\activate

echo 📦 Upgrading pip...
python -m pip install --upgrade pip

echo 📦 Installing core dependencies first...
pip install pydantic-settings==2.1.0 pypdf==3.17.4 fuzzywuzzy==0.18.0 python-Levenshtein==0.23.0 aiohttp==3.9.1 aiofiles==23.2.1

echo 📦 Installing backend dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Backend installation failed
    echo 🔧 Trying with individual packages...
    pip install fastapi uvicorn pydantic pydantic-settings python-multipart httpx requests pandas openpyxl xlrd pypdf pdfplumber structlog colorama python-dotenv cryptography bcrypt pytest pytest-asyncio pytest-cov black isort flake8 mypy fuzzywuzzy python-Levenshtein aiohttp aiofiles
)

echo ✅ Backend setup complete!
echo 🧪 Testing backend startup...
python -c "from config import settings; print('✅ Config loaded successfully')"
if errorlevel 1 (
    echo ❌ Config test failed
) else (
    echo ✅ Backend is ready!
)
pause