@echo off
cd /d "%~dp0"
chcp 65001 > nul
title Memory Analyzer - Starting...
color 0A

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║        Memory Analyzer - Startup         ║
echo  ╚══════════════════════════════════════════╝
echo.

:: ── 1. التحقق من Python ────────────────────────────────────
echo [1/5] التحقق من Python...
python --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo  ❌ Python غير مثبت او غير موجود في PATH
    echo  الحل: https://python.org
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo     ✅ %%i


:: ── 2. إصلاح uvicorn ثم تثبيت المتطلبات ───────────────────
echo.
echo [2/5] تثبيت المتطلبات...

:: إغلاق أي عمليات uvicorn عالقة قد تمنع التحديث
taskkill /F /IM uvicorn.exe /T >nul 2>&1

:: حذف uvicorn المكسور عبر ملف Python منفصل
echo     جارٍ إصلاح uvicorn...
python fix_uvicorn.py
if errorlevel 1 (
    echo     تحذير: تعذر تنظيف uvicorn القديم
)

:: تثبيت uvicorn نظيف
pip install "uvicorn[standard]" -q --no-warn-script-location
if errorlevel 1 (
    color 0C
    echo.
    echo  ❌ فشل تثبيت uvicorn
    echo.
    pause
    exit /b 1
)

:: تثبيت باقي المتطلبات
pip install fastapi sqlalchemy pydantic python-multipart psutil -q --no-warn-script-location

:: تحقق نهائي
python -c "import fastapi, sqlalchemy, pydantic, uvicorn, multipart" > nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo  ❌ فشل التحقق من المتطلبات
    echo  جرب: pip install fastapi sqlalchemy pydantic uvicorn python-multipart
    echo.
    pause
    exit /b 1
)
echo     ✅ جميع المتطلبات جاهزة


:: ── 3. التحقق من Volatility 3 ─────────────────────────────
echo.
echo [3/5] التحقق من Volatility 3...
python -c "import volatility3" > nul 2>&1
if errorlevel 1 (
    color 0E
    echo  ⚠️  Volatility 3 غير مثبت - جارٍ التثبيت...
    pip install volatility3 -q
    python -c "import volatility3" > nul 2>&1
    if errorlevel 1 (
        echo  ⚠️  تعذر تثبيت Volatility - تحليل RAW لن يعمل
        color 0A
    ) else (
        echo     ✅ تم تثبيت Volatility 3
    )
) else (
    echo     ✅ Volatility 3 مثبت
)


:: ── 4. التحقق من Symbol Tables ────────────────────────────
echo.
echo [4/5] التحقق من Symbol Tables...
python check_symbols.py > %TEMP%\vol_check.txt 2>nul

:: قراءة السطر الأول (الحالة)
set /p SYM_STATUS=<%TEMP%\vol_check.txt

:: قراءة السطر الثاني (المسار) - نبحث عن السطر الذي يبدأ بـ PATH:
for /f "tokens=1,* delims=:" %%a in (%TEMP%\vol_check.txt) do (
    if "%%a"=="PATH" set SYM_PATH=%%b
)

if "%SYM_STATUS%"=="FOUND" (
    echo     ✅ Symbol Tables موجودة - تحليل RAW جاهز
) else if "%SYM_STATUS%"=="VOL_NOT_INSTALLED" (
    echo     ⚠️  Volatility غير مثبت - تم تخطي فحص Symbols
) else (
    color 0E
    echo  ⚠️  Symbol Tables مفقودة
    echo.
    echo     لتفعيل تحليل ملفات RAW/DMP:
    echo     1. حمّل windows.zip من:
    echo        https://downloads.volatilityfoundation.org/volatility3/symbols/windows.zip
    echo.
    echo     2. فك الضغط في:
    echo        %SYM_PATH%
    echo.
    echo     المشروع سيعمل لتحليل ملفات JSON فقط
    echo.
    color 0A
)


:: ── 4.5 التحقق من أدوات الالتقاط (Acquisition Tools) ──────
echo.
echo [4.5/5] التحقق من أدوات الالتقاط...
set "TOOLS_DIR=backend\tools"
set "DUMPIT_EXE=%TOOLS_DIR%\DumpIt.exe"

if not exist "%TOOLS_DIR%" mkdir "%TOOLS_DIR%"

if not exist "%DUMPIT_EXE%" (
    echo     ⚠️  أداة DumpIt غير موجودة
    echo     لتفعيل الوضع الثقيل:
    echo     1. قم بتحميل Magnet DumpIt (مجاني)
    echo     2. ضع الملف باسم DumpIt.exe في: backend\tools\
) else (
    echo     ✅ أداة DumpIt موجودة
)


:: ── 5. تشغيل السيرفر ────────────────────────────────────────
echo.
echo [5/5] تشغيل السيرفر...
echo.
echo  ╔══════════════════════════════════════════╗
echo  ║  ✅ http://127.0.0.1:8000               ║
echo  ║  اضغط Ctrl+C لايقاف السيرفر            ║
echo  ╚══════════════════════════════════════════╝
echo.

:: فتح المتصفح بعد ثانيتين
start /b cmd /c "timeout /t 2 /nobreak > nul && start http://127.0.0.1:8000"

:: تشغيل السيرفر
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

:: نصل هنا فقط إذا توقف السيرفر
echo.
if errorlevel 1 (
    color 0C
    echo  ❌ فشل تشغيل السيرفر
    echo.
    echo  الاسباب المحتملة:
    echo  1. تاكد انك في المجلد الصحيح: D:\project_BY_ME
    echo  2. تاكد من وجود: backend\app\main.py
    echo  3. تاكد من وجود __init__.py في:
    echo     backend\__init__.py
    echo     backend\app\__init__.py
    echo     backend\app\API\__init__.py
    echo.
    echo  تشغيل بدون --reload لرؤية الخطأ الكامل...
    echo.
    python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
)

echo.
echo  اضغط اي مفتاح للاغلاق...
pause > nul