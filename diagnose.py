"""
diagnose.py - تشخيص مشكلة python-multipart
شغّل: python diagnose.py
"""
import sys
import subprocess

print("=" * 50)
print("تشخيص مشكلة رفع الملفات")
print("=" * 50)

# 1. تحقق من python-multipart
print("\n[1] python-multipart:")
try:
    import multipart
    print(f"    ✅ مثبت - إصدار: {getattr(multipart, '__version__', 'unknown')}")
except ImportError:
    print("    ❌ غير مثبت")

# تحقق من python_multipart أيضاً (الاسم الجديد)
try:
    import python_multipart
    print(f"    ✅ python_multipart: {getattr(python_multipart, '__version__', 'unknown')}")
except ImportError:
    print("    ⚠️  python_multipart غير موجود (طبيعي)")

# 2. تحقق من FastAPI
print("\n[2] FastAPI:")
try:
    import fastapi
    print(f"    ✅ إصدار: {fastapi.__version__}")
except ImportError:
    print("    ❌ غير مثبت")

# 3. تحقق من starlette
print("\n[3] starlette:")
try:
    import starlette
    print(f"    ✅ إصدار: {starlette.__version__}")
    # starlette تستخدم python-multipart داخلياً
    from starlette.datastructures import UploadFile
    print("    ✅ UploadFile يعمل")
except Exception as e:
    print(f"    ❌ {e}")

# 4. اختبار multipart parsing مباشرة
print("\n[4] اختبار multipart parsing:")
try:
    from starlette.formparsers import MultiPartParser
    print("    ✅ MultiPartParser متاح")
except Exception as e:
    print(f"    ❌ {e}")

# 5. فحص pip list
print("\n[5] الحزم المثبتة المتعلقة:")
result = subprocess.run(
    [sys.executable, "-m", "pip", "show", "python-multipart"],
    capture_output=True, text=True
)
if result.returncode == 0:
    for line in result.stdout.strip().split("\n"):
        print(f"    {line}")
else:
    print("    ❌ python-multipart غير موجود في pip")

print("\n" + "=" * 50)
print("الحل:")
print("  pip install --force-reinstall python-multipart")
print("=" * 50)