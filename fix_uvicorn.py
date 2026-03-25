"""
fix_uvicorn.py
يُحذف uvicorn القديم المكسور من site-packages مباشرة
"""
import os, shutil, sys

# إيجاد مسار site-packages
site = None
for p in sys.path:
    if 'site-packages' in p and os.path.isdir(p):
        site = p
        break

if not site:
    print("ERROR: لم يتم إيجاد site-packages")
    sys.exit(1)

print(f"    site-packages: {site}")

removed = []

# حذف مجلد uvicorn الرئيسي
uv_dir = os.path.join(site, 'uvicorn')
if os.path.isdir(uv_dir):
    shutil.rmtree(uv_dir)
    removed.append('uvicorn/')

# حذف dist-info أو egg-info المكسور
for name in os.listdir(site):
    if name.lower().startswith('uvicorn') and (
        name.endswith('.dist-info') or
        name.endswith('.egg-info') or
        name.endswith('.egg-link')
    ):
        full = os.path.join(site, name)
        try:
            if os.path.isdir(full):
                shutil.rmtree(full)
            else:
                os.remove(full)
            removed.append(name)
        except Exception as e:
            print(f"    تحذير: تعذر حذف {name}: {e}")

if removed:
    print("    حُذف: " + ", ".join(removed))
else:
    print("    لا يوجد uvicorn قديم للحذف")

sys.exit(0)
