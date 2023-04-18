from setuptools import setup
from Cython.Build import cythonize

setup(
    name="Cython module for distance calculation",
    ext_modules=cythonize("distance_calculator.pyx", build_dir="bin/"),
    zip_safe=False,
)