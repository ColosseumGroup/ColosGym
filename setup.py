#!/usr/bin/python3
#setup.py
from setuptools import setup, Extension

GameSolver = Extension('GameSolver', sources=["rng.c","net.c","game.c","GameSolver.c"])
setup(name="GameSolver_pkg", version='1.0', description="asd", ext_modules=[GameSolver])
#在使用GameSolver之前，需要使用这个脚本
#用法
#python setup.py install