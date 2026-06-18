@echo off
title CAI DAT HE THONG RAG
cls

:: Ep Windows dung dung thu muc chua file .bat
cd /d "%~dp0"

echo ============================================================
echo   BUOC 1: KHOI TAO MOI TRUONG VA CAI DAT (1 LAN DUY NHAT)
echo ============================================================
echo.

:: 1. Kiem tra Python xem co ton tai khong
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python tren may tinh! 
    echo Vui long cai dat Python 3.10 tro len va tich chon "Add Python to PATH".
    echo.
    pause
    exit /b
)

:: 2. Khoi tao moi truong ao .venv
echo [*] Dang khoi tao moi truong ao Python (.venv)...
python -m venv .venv
echo [OK] Da khoi tao xong thu muc .venv.
echo.

:: 3. Kich hoat moi truong ao
echo [*] Dang kich hoat moi truong ao...
call .venv\Scripts\activate.bat
echo.

:: 4. Nhap API Key va tao file .env (DA CAP NHAT THEM HF_TOKEN)
echo ------------------------------------------------------------
echo [CAU HINH] Thiet lap tai khoan cho lan dau su dung:
set /p api_key="👉 Vui long nhap hoac dan GROQ_API_KEY cua ban: "
set /p hf_token="👉 Vui long nhap hoac dan HF_TOKEN (Hugging Face Token) cua ban: "

:: Ghi ca 2 gia tri vao file .env một cach sach se
echo GROQ_API_KEY=%api_key%>.env
echo HF_TOKEN=%hf_token%>>.env

echo.
echo [OK] Da luu cau hinh GROQ_API_KEY va HF_TOKEN vao file .env!
echo ------------------------------------------------------------
echo.

:: 5. Ep buoc cai dat requirements (Dung pip cua chính venv)
echo [*] Dang tien hanh cai dat cac thu vien (Buoc nay se chay hoi lau)...
echo [*] Cac thong tin cai dat dang duoc tai ve...
echo ------------------------------------------------------------

.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt --no-cache-dir -v

echo ------------------------------------------------------------
echo.
echo ============================================================
echo [THANH CONG] Da setup va cai dat xong toan bo thu vien!
echo Gio ban co the tat file nay, nhap dup file "run.bat" de chay app chatbot.
echo ============================================================
echo.
pause
