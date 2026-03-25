"""
test_volatility.py
شغّله هكذا:
    py test_volatility.py
"""
import sys

def test_volatility(memory_path: str):
    print("=" * 60)
    print(f"اختبار Volatility 3 على: {memory_path}")
    print("=" * 60)

    # ── 1. Import ──────────────────────────────────────────────
    try:
        import volatility3.framework as framework
        from volatility3.framework import contexts, automagic as vol_automagic
        from volatility3.plugins.windows.pslist import PsList
        print(f"✅ Import ناجح | Volatility {framework.version}")
    except Exception as e:
        print(f"❌ Import فشل: {e}")
        return

    # ── 2. Context ─────────────────────────────────────────────
    try:
        framework.require_interface_version(2, 0, 0)
        ctx = contexts.Context()
        from pathlib import Path
        file_uri = Path(memory_path).resolve().as_uri()
        ctx.config["automagic.LayerStacker.single_location"] = file_uri
        print(f"✅ Context جاهز | URI: {file_uri}")
    except Exception as e:
        print(f"❌ Context فشل: {e}")
        return

    # ── 3. Automagic ───────────────────────────────────────────
    try:
        available = vol_automagic.available(ctx)
        automagic = vol_automagic.choose_automagic(available, PsList)
        print(f"✅ Automagic: {[type(a).__name__ for a in automagic]}")
        errors = vol_automagic.run(automagic, ctx, PsList, "plugins")
        print(f"✅ automagic.run ناجح | errors: {errors}")
    except Exception as e:
        import traceback
        print(f"❌ Automagic فشل: {e}")
        traceback.print_exc()
        return

    # ── 4. Layers ──────────────────────────────────────────────
    layers = list(ctx.layers.keys())
    print(f"✅ Layers: {layers}")

    # ── 5. اختبار تشغيل pslist بعدة طرق ──────────────────────

    # طريقة A: plugin_class(ctx, config_path)
    print("\n--- طريقة A: plugin_class(ctx, 'plugins') ---")
    try:
        p = PsList(ctx, "plugins")
        rows = list(p.run().iterate_rows())
        print(f"✅ طريقة A نجحت: {len(rows)} rows")
    except Exception as e:
        print(f"❌ طريقة A فشلت: {e}")

    # طريقة B: config path كامل
    print("\n--- طريقة B: plugin_class(ctx, 'plugins.PsList') ---")
    try:
        p = PsList(ctx, "plugins.PsList")
        rows = list(p.run().iterate_rows())
        print(f"✅ طريقة B نجحت: {len(rows)} rows")
    except Exception as e:
        print(f"❌ طريقة B فشلت: {e}")

    # طريقة C: construct من interfaces
    print("\n--- طريقة C: interfaces.construct_plugin ---")
    try:
        from volatility3.framework.interfaces.plugins import construct_plugin
        import inspect
        sig = inspect.signature(construct_plugin)
        print(f"  construct_plugin signature: {sig}")
        p = construct_plugin(ctx, automagic, PsList, "plugins", None, None)
        rows = list(p.run().iterate_rows())
        print(f"✅ طريقة C نجحت: {len(rows)} rows")
    except ImportError:
        print("  construct_plugin غير موجود في هذا الإصدار")
    except Exception as e:
        print(f"❌ طريقة C فشلت: {e}")

    # طريقة D: run_plugin من CLI
    print("\n--- طريقة D: volatility3.framework.plugins.construct ---")
    try:
        from volatility3.framework import plugins as fw_plugins
        import inspect
        members = [m for m in dir(fw_plugins) if 'construct' in m.lower() or 'build' in m.lower()]
        print(f"  Available in plugins: {members}")
    except Exception as e:
        print(f"  {e}")

    # طريقة E: مباشرة بعد automagic على pslist
    print("\n--- طريقة E: automagic مباشرة على pslist ثم تشغيله ---")
    try:
        ctx2 = contexts.Context()
        ctx2.config["automagic.LayerStacker.single_location"] = file_uri
        available2 = vol_automagic.available(ctx2)
        automagic2 = vol_automagic.choose_automagic(available2, PsList)
        vol_automagic.run(automagic2, ctx2, PsList, "plugins.PsList")
        p = PsList(ctx2, "plugins.PsList")
        rows = list(p.run().iterate_rows())
        print(f"✅ طريقة E نجحت: {len(rows)} rows")
        # اطبع أول صفين
        for row in rows[:2]:
            print(f"  row sample: {row}")
    except Exception as e:
        import traceback
        print(f"❌ طريقة E فشلت: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else r"D:\Challenge.raw"
    test_volatility(path)