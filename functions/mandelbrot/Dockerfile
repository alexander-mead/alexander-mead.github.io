# Base image (specifying OS/Python etc.)
FROM public.ecr.aws/lambda/python:3.10

# Commands to run when creating the image
# The order matters here, as the layers are built up

# Fortran stuff
RUN yum install gcc-gfortran -y
RUN pip install f90wrap
COPY Fortran ./Fortran
RUN cd Fortran && ./f2py.sh

# Python stuff
RUN python3.10 -m pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN python3.10 -m pip install poetry
RUN python3.10 -m poetry config virtualenvs.create false
COPY mandelbrot.py lambda.py ./
COPY pyproject.toml poetry.lock ./
RUN python3.10 -m poetry install

# What is actually run (entrypoint)
CMD ["lambda.handler"]