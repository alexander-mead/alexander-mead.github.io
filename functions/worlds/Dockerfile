# Base image (specifying OS/Python etc.)
FROM public.ecr.aws/lambda/python:3.12-build

# Install git
RUN dnf install -y git

# Commands to run when creating the image
RUN python3.12 -m pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN python3.12 -m pip install uv
COPY lambda.py ./
COPY pyproject.toml uv.lock ./
RUN python3.12 -m uv sync

# What is actually run (entrypoint)
CMD ["lambda.handler"]