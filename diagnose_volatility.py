r"""
diagnose_volatility.py

Runs Volatility plugins one by one to diagnose hangs or crashes.

Usage:
    python diagnose_volatility.py <path_to_memory_file>

Example:
    python diagnose_volatility.py "D:\dumps\memory.raw"
"""
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# --- Minimal copy of VolatilityRunner for standalone execution ---

class VolatilityNotInstalledError(Exception): pass

class VolatilityRunner:
    def __init__(self, memory_path: Path):
        self.memory_path = memory_path
        print(f"[*] Initialized VolatilityRunner for: {self.memory_path}")

    def check_installation(self):
        try:
            import volatility3
            import volatility3.framework
            # The 'version' attribute was removed in newer versions.
            try:
                print(f"[+] Volatility 3 installation found (version {volatility3.framework.constants.VERSION}).")
            except AttributeError:
                print("[+] Volatility 3 installation found (version unknown).")
        except ImportError as e:
            raise VolatilityNotInstalledError(f"Volatility 3 is not installed: {e}")

    def check_symbols(self):
        try:
            import volatility3
            sym_path = Path(volatility3.__file__).parent / "symbols"
            if not sym_path.exists() or not any(sym_path.iterdir()):
                print(f"[-] Warning: Symbols directory at '{sym_path}' is missing or empty.")
            else:
                print("[+] Symbols directory seems to be populated.")
        except Exception as e:
            print(f"[!] Warning: Could not check symbols: {e}")

    def run_plugin(self, plugin_class, plugin_name: str) -> Tuple[List, Optional[str]]:
        try:
            from volatility3.framework import contexts, automagic as vol_automagic
            ctx = contexts.Context()
            file_uri = self.memory_path.resolve().as_uri()
            ctx.config["automagic.LayerStacker.single_location"] = file_uri
            automagic = vol_automagic.choose_automagic(vol_automagic.available(ctx), plugin_class)
            vol_automagic.run(automagic, ctx, plugin_class, "plugins")
            plugin_obj = plugin_class(ctx, f"plugins.{plugin_class.__name__}")
            grid = plugin_obj.run()
            
            rows = []
            def visitor(node, accumulator):
                rows.append(node.values)
                return None
            grid.visit(None, visitor, None)
            return rows, None
        except Exception:
            return [], traceback.format_exc()

def get_plugin_class(module_path: str, class_name: str):
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

# --- Main diagnostic function ---

def diagnose_plugins(memory_file: str):
    print("=" * 80)
    print("Volatility 3 Standalone Diagnostic Script")
    print("=" * 80)

    memory_path = Path(memory_file)
    if not memory_path.exists():
        print(f"\n❌ ERROR: Memory file not found at '{memory_file}'")
        return

    print(f"\n[INFO] Target memory file: {memory_path}")
    print(f"[INFO] File size: {memory_path.stat().st_size / (1024*1024):.2f} MB")
    print("-" * 80)

    try:
        runner = VolatilityRunner(memory_path)
        runner.check_installation()
        runner.check_symbols()
    except Exception as e:
        print(f"\n❌ ERROR: Failed to initialize Volatility: {e}")
        return

    plugins_to_test = [
        ("pslist", "volatility3.plugins.windows.pslist", "PsList"),
        ("dlllist", "volatility3.plugins.windows.dlllist", "DllList"),
        ("cmdline", "volatility3.plugins.windows.cmdline", "CmdLine"),
        ("svcscan", "volatility3.plugins.windows.svcscan", "SvcScan"),
        ("hivelist", "volatility3.plugins.windows.registry.hivelist", "HiveList"),
        ("modules", "volatility3.plugins.windows.modules", "Modules"),
        # Slow plugins - test them last
        ("netscan", "volatility3.plugins.windows.netscan", "NetScan"),
        ("malfind", "volatility3.plugins.windows.malware.malfind", "Malfind"),
        ("ldrmodules", "volatility3.plugins.windows.malware.ldrmodules", "LdrModules"),
    ]

    print("\n[INFO] Starting sequential plugin execution...\n")
    results = {}
    for name, module_path, class_name in plugins_to_test:
        print(f"--- Testing Plugin: {name} ---")
        start_time = time.time()
        try:
            plugin_class = get_plugin_class(module_path, class_name)
            rows, error = runner.run_plugin(plugin_class, name)
            duration = time.time() - start_time
            if error:
                print(f"  🔴 FAILED after {duration:.2f} seconds.")
                print(f"  Error: {error.splitlines()[-1]}")
                results[name] = {"status": "failed", "duration": duration}
            else:
                print(f"  🟢 SUCCEEDED in {duration:.2f} seconds.")
                print(f"  Rows returned: {len(rows)}")
                results[name] = {"status": "success", "duration": duration, "rows": len(rows)}
        except Exception as e:
            duration = time.time() - start_time
            print(f"  🔴 CRASHED after {duration:.2f} seconds.")
            traceback.print_exc()
            results[name] = {"status": "crashed", "duration": duration}
        print("-" * 30 + "\n")

    print("=" * 80)
    print("Diagnostic Summary")
    print("=" * 80)
    for name, result in results.items():
        status = result['status'].upper()
        duration = result['duration']
        if status == "SUCCESS":
            print(f"- {name:<12}: {status:<10} ({result['rows']} rows) in {duration:.2f}s")
        else:
            print(f"- {name:<12}: {status:<10} in {duration:.2f}s")
    print("=" * 80)
    print("\n[ACTION] Review the output. The last plugin that 'FAILED' or 'CRASHED' is the problem.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python diagnose_volatility.py <path_to_memory_file>")
        default_path = r"D:\PROJECT_by_mi_history\project_BY_ME- full analyzer - ai test - Copy (2)\dumps\raw\memory_heavy_20260302_125854.raw"
        print(f"Example: python diagnose_volatility.py \"{default_path}\"")
        sys.exit(1)
    
    diagnose_plugins(sys.argv[1])