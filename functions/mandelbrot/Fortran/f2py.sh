#!/bin/sh

name=mandelbrot

gfortran -c -fPIC -O3 $name.f90 &&
f90wrap -m $name $name.f90 &&
f2py -c -m $name f90wrap_$name.f90 $name.o
