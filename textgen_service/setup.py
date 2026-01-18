from setuptools import setup
from mypyc.build import mypycify

setup(
    name="cyberguard_core",
    ext_modules=mypycify([
        "core.py",
    ]),
)
