import sys
import platform

print("Python version:", sys.version, flush=True)
print("Platform:", platform.platform(), flush=True)

packages = [
    "numpy", "pandas", "scipy", "sklearn", "lightgbm", 
    "torch", "joblib", "pytest", "fastapi", "uvicorn", 
    "sqlalchemy", "shap", "pydantic"
]

for pkg in packages:
    try:
        mod = __import__(pkg)
        ver = getattr(mod, "__version__", "installed")
        print(f"  {pkg:15s}: {ver}", flush=True)
    except Exception as e:
        print(f"  {pkg:15s}: NOT INSTALLED ({e})", flush=True)
