curl --request POST http://127.0.0.1:3000/mandelbrot \
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