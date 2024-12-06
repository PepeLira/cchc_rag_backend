import importlib
import pkgutil
import inspect

def import_all_modules_and_get_classes(package_name):
    package = importlib.import_module(package_name)
    classes = {}
    
    # Import all modules and get classes
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package_name}.{module_name}")
        
        # Get all classes in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Ensure the class is defined in the module (not imported)
            if obj.__module__ == module.__name__:
                classes[name] = obj
    
    return classes

# Import all modules in the current package and get all classes
all_classes = import_all_modules_and_get_classes(__name__)

# Optionally, you can make the classes available at the package level
globals().update(all_classes)