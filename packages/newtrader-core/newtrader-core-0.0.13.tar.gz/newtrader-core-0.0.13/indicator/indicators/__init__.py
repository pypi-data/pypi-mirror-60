import glob
import importlib
import sys
from os.path import dirname, join, basename, isfile

modules1 = glob.glob(join(dirname(__file__), "*.py"))
modules2 = glob.glob(join(dirname(__file__), "*.pyx"))
__all__ = [basename(f)[:-3] for f in modules1 if isfile(f) and not f.endswith('__init__.py')]
__all__ += [basename(f)[:-4] for f in modules2 if isfile(f)]

classes = {}

for indicator in __all__:
    module = importlib.import_module('.' + indicator, 'indicator.indicators')
    if hasattr(module, 'export'):
        iClass = module.export
        setattr(sys.modules['indicator'], indicator.upper(), iClass)
        classes[indicator.upper()] = iClass
