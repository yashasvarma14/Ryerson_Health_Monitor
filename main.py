## main.py ─ Ryerson Health Monitor
## Run ALL five steps in one shot:

## Configuration lives in settings.yaml so reps can tweak thresholds
## without touching code.  Each step prints a confirmation line when done.

from pathlib import Path
import importlib.util
import sys
import yaml

# 1. load settings 
cfg = yaml.safe_load(open("settings.yaml", "r"))
print("DEBUG – expecting raw CSV at:", Path(cfg["raw_csv"]).resolve())

CFG_FILE = Path(__file__).with_name("settings.yaml")
with CFG_FILE.open() as f:
    cfg = yaml.safe_load(f)

# helper to load a script by path and call its run function
def run_script(path: str):
    path_obj = Path(path)
    name = path_obj.stem
    spec = importlib.util.spec_from_file_location(name, path_obj)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    if hasattr(module, "run"):
        module.run(cfg)
    else:
        print(f"Error: {name} has no run function")

def main():
    scripts = [
        "scripts/00_clean_data.py",
        "scripts/01_monthly_health.py",
        "scripts/02_visual_data.py",
        "scripts/03_predictive_health.py",
        "scripts/04_contact_alerts.py",
    ]
    for s in scripts:
        print(f"\nRunning {s} ...")
        run_script(s)

    dash = Path(cfg["html_dashboard"]).resolve()
    rep  = Path(cfg["rep_html"]).resolve()
    print("\nDone!")
    print(f"Open dashboard at: {dash}")
    print(f"Rep call list at : {rep}")

if __name__ == "__main__":
    main()
