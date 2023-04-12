#!/bin/sh

name=mandelbrot

rm -rf __pycache__
rm -rf f90wrap_$name.f90
rm -rf .f2py_f2cmap
rm -rf *.c
rm -rf *.so
rm -rf $name-f2pywrappers2.f90
rm -rf $name.o
rm -rf $name.mod
rm -rf $name.py
rm -rf $name.pyf