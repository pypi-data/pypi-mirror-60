import os
import glob
from setuptools import setup




try:
    from Cython.Distutils.extension import Extension
    from Cython.Distutils import build_ext as _build_ext
except ImportError as e:
    from setuptools import Extension
    from setuptools.command.build_ext import build_ext as _build_ext
    USING_CYTHON = False

else:
    USING_CYTHON = True

ext = 'pyx' if USING_CYTHON else 'c'
sources = []
cython_modules = ['indicator/indicators', 'quotation',
                  'trade', 'broker', 'runner', 'strategies']
package_data = {}
for m in cython_modules:
    package_data['newtrader.core.'+m.replace('/','.')] =  glob.glob(f'{m}/*.pxd')
    sources+=glob.glob(f'{m}/*.%s' % (ext,))
extensions = [
    Extension(source.split('.')[0].replace(os.path.sep, '.'),
              sources=[source],
            #   include_dirs=[numpy.get_include()]
              )
    for source in sources]

class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())

cmdclass = {'build_ext': build_ext}



setup(
    name="newtrader-core",
    version="0.0.11",
    author='Jiayi Su',
    author_email='nathaniel@finop.cloud',
    ext_modules=extensions,
    url="http://newtrader.finop.cloud",
    package_dir={
        "newtrader.core": ""
    },
    install_requires=[
        "numpy",
        "pandas",
        "prettytable",
        "tqdm",
        "tables",
        "click",
    ],
    setup_requires=[
        "numpy",
    ],
    package_data={
        "":["*.pxd"]
    },
    python_requires='>=3.8.1',
    cmdclass=cmdclass,
    packages=["newtrader.core",
              "newtrader.core.indicator",
              "newtrader.core.indicator.indicators",
              "newtrader.core.indicator.analyzer",
              "newtrader.core.indicator.generator",
              "newtrader.core.indicator.wrappers",
              "newtrader.core.broker",
              "newtrader.core.trade",
              "newtrader.core.quotation", "newtrader.core.strategies", "newtrader.core.runner"],
)
