import os
import importlib
import inspect
from app.db.session import Base

# Get the current package name
package_name = __name__

# Initialize the __all__ list
__all__ = []

# Iterate over all files in the package directory
package_dir = os.path.dirname(__file__)
for filename in os.listdir(package_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = filename[:-3]
        module = importlib.import_module(f'.{module_name}', package_name)
        
        # Inspect the module to find all classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Ensure the class is defined in the module (not imported)
            if obj.__module__ == module.__name__:
                globals()[name] = obj
                __all__.append(name)
