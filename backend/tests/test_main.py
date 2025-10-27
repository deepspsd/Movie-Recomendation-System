import sys
sys.path.insert(0, '.')

try:
    import main
    print("✅ main.py imports successfully!")
except Exception as e:
    print(f"❌ Error importing main.py: {e}")
    import traceback
    traceback.print_exc()
