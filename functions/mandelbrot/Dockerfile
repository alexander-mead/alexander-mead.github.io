# Base image (specifying OS/Python etc.)
FROM public.ecr.aws/lambda/python:3.10

# Commands to run when creating the image
# The order matters here, as the layers are built up
COPY requirements.txt ./
RUN python3.10 -m pip install -r requirements.txt -t .
COPY mandelbrot.py lambda.py ./

# What is actually run (entry point)
CMD ["lambda.handler"]