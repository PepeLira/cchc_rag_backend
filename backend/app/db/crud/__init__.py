import os
import pkgutil
import inspect
from types import ModuleType
from pathlib import Path

# Get the directory of the current package
package_dir = Path(__file__).parent

# Dynamically import all modules in the package
for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
    module = __import__(f"{__name__}.{module_name}", fromlist=["*"])
    for name, obj in vars(module).items():
        # Add functions to the current package namespace
        if inspect.isfunction(obj):
            globals()[name] = obj
