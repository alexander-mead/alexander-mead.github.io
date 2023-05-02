# Base image (specifying OS/Python etc.)
FROM public.ecr.aws/lambda/python:3.10

# Commands to run when creating the image
# The order matters here, as the layers are built up
RUN yum install gcc-gfortran -y
RUN yum install make -y
RUN yum install which -y
COPY requirements.txt ./
RUN python3.10 -m pip install -r requirements.txt -t .
COPY nbody.py lambda.py ./

# What is actually run (entry point)
CMD ["lambda.handler"]