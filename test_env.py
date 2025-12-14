import sys
print("Python is working")
print(sys.executable)
try:
    import pandas
    print("Pandas imported")
except ImportError as e:
    print(f"Pandas error: {e}")
