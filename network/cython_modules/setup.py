from setuptools import setup
from Cython.Build import cythonize

# python setup.py build_ext --inplace
setup(
    name="Cython module for distance calculation",
    ext_modules=cythonize("distance_calculator.pyx", build_dir="bin/"),
    zip_safe=False,
)