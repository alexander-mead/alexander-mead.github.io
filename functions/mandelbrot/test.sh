#!/bin/bash

# Read the URL from the command line
# url=http://127.0.0.1:3000
# url=https://x7or5gwlkk.execute-api.eu-west-2.amazonaws.com/Prod # Personal
if [ "$#" -ne 1 ]; then
    echo "Usage: test.sh <url>" 
    exit 1
fi
url=$1

curl --request POST $url/mandelbrot\
    --header "Content-Type: application/json" \
    --header "Accept: application/json" \
    --data '{
        "real": -0.5,
        "imag": 0,
        "zoom": 1,
        "depth": 2,
        "color": "cubehelix",
        "width": 1000,
        "height": 1000,
        "sigma": 0.5,
        "transform": 1
    }'