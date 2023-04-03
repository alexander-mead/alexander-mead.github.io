# Base image (specifying OS/Python etc.)
FROM public.ecr.aws/lambda/python:3.9

# Commands to run when creating the image
# The order matters here, as the layers are built up
RUN pip install f90wrap
RUN yum install gcc-gfortran -y
COPY Fortran ./Fortran
RUN cd Fortran && ./f2py.sh
COPY requirements.txt ./
RUN python3.9 -m pip install -r requirements.txt -t .
COPY mandelbrot.py lambda.py ./

# What is actually run (entry point)
CMD ["lambda.handler"]