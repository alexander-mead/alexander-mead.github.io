#!/bin/sh

name=mandelbrot

./clean.sh
gfortran -c -O3 $name.f90 &&
f90wrap -m $name $name.f90 &&
# python3 -m numpy.f2py -h $name.pyf -m $name $name.f90 &&
# python3 -m numpy.f2py -c $name.pyf $name.f90
# f2py -c -m $name f90wrap_$name.f90 $name.o
python3 -m numpy.f2py -c -m $name $name.f90
