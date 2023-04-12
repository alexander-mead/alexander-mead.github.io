#!/bin/sh

name=mandelbrot

./clean.sh
gfortran -c -O3 $name.f90 &&
f90wrap -m $name $name.f90 &&
python3 -m numpy.f2py -c -m $name $name.f90
