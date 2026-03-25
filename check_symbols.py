"""
check_symbols.py
يتحقق من وجود Volatility Symbol Tables ويطبع المسار
"""
import os, sys

try:
    import volatility3
    sym_path = os.path.join(os.path.dirname(volatility3.__file__), 'symbols')

    if not os.path.exists(sym_path):
        print("MISSING_DIR")
        print("PATH:" + sym_path)
        sys.exit(0)

    files = os.listdir(sym_path)
    has_syms = any(
        f.startswith('windows') or f.endswith('.json.xz') or f.endswith('.zip')
        for f in files
    )

    if has_syms:
        print("FOUND")
    else:
        print("MISSING_FILES")

    print("PATH:" + sym_path)

except ImportError:
    print("VOL_NOT_INSTALLED")
except Exception as e:
    print("ERROR:" + str(e))
