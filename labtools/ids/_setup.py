from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    name = "My hello app",
    #script_args = ['--compiler=mingw64'],
    library_dirs = [r'C:\Program Files\IDS\uEye\Develop\Lib'],
    include_dirs = [numpy.get_include(), r'C:\Program Files\IDS\uEye\Develop\include'],
    ext_modules = cythonize("*.pyx", include_path = [numpy.get_include()]),
)