import importlib.util
import inspect
import os
import sys

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "plugins")

REQUIRED_FUNC = "run_scraper"
REQUIRED_PARAMS = ["query", "output_file"]

def validate_plugin(path, plugin_name):
    try:
        spec = importlib.util.spec_from_file_location(plugin_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Failed to import {plugin_name}: {e}")
        return False

    if not hasattr(module, REQUIRED_FUNC):
        print(f"{plugin_name} is missing required function: {REQUIRED_FUNC}()")
        return False

    func = getattr(module, REQUIRED_FUNC)
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    for req_param in REQUIRED_PARAMS:
        if req_param not in params:
            print(f"{plugin_name} is missing required argument: '{req_param}' in {REQUIRED_FUNC}()")
            return False

    print(f"{plugin_name} passed validation.")
    return True

def run_validation():
    print("Validating plugins...\n")
    plugin_files = [f for f in os.listdir(PLUGIN_DIR) if f.endswith(".py") and f != "__init__.py"]
    
    if not plugin_files:
        print("No plugins found.")
        return

    failed = []
    for plugin_file in plugin_files:
        path = os.path.join(PLUGIN_DIR, plugin_file)
        plugin_name = plugin_file[:-3]
        if not validate_plugin(path, plugin_name):
            failed.append(plugin_file)

    if not failed:
        print("\nAll plugins are valid!")
    else:
        print("\nSome plugins failed validation:")
        for f in failed:
            print(f" - {f}")
        sys.exit(1)

if __name__ == "__main__":
    run_validation()
