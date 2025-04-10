#!/bin/bash

# Read the URL from the command line
# url=http://127.0.0.1:3000
# url=https://x7or5gwlkk.execute-api.eu-west-2.amazonaws.com/Prod # Personal
if [[ -z "${1:-}"  ]]; then
    echo "Usage: $0 <url> [<api_key>]" 
    exit 1
fi
URL=$1
API_KEY=${2:-}

curl --request POST $URL/mandelbrot\
    --header "Content-Type: application/json" \
    --header "Accept: application/json" \
    --header "X-Api-Key: $API_KEY" \
    --data '{
        "real": -0.5,
        "imag": 0,
        "zoom": 1,
        "depth": 2,
        "color": "cubehelix",
        "width": 100,
        "height": 100,
        "sigma": 0.5,
        "transform": 1
    }'