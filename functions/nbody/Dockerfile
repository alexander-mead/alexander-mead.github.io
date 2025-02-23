# Base image (specifying OS/Python etc.)
FROM public.ecr.aws/lambda/python:3.10

# Commands to run when creating the image
RUN yum install gcc-gfortran -y
RUN yum install make -y
RUN yum install which -y
# COPY requirements.txt ./
# RUN python3.10 -m pip install -r requirements.txt -t .
RUN python3.10 -m pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN python3.10 -m pip install poetry
RUN python3.10 -m poetry config virtualenvs.create false
COPY nbody.py lambda.py ./
COPY pyproject.toml poetry.lock ./
RUN python3.10 -m poetry install

# What is actually run (entrypoint)
CMD ["lambda.handler"]