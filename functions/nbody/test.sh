curl --request POST http://127.0.0.1:3000/nbody \
    --header "Content-Type: application/json" \
    --header "Accept: application/json" \
    --data '{
        "kmin": 0.001,
        "kmax": 10,
        "nk": 100,
        "z": 0,
        "color": "cubehelix",
        "npix": 1000,
        "Lbox": 500,
        "Tbox": 1,
        "Omega_m": 0.3,
        "Omega_b": 0.045,
        "H_0": 70.0,
        "sigma_8": 0.8,
        "A_s": 2e-9,
        "n_s": 0.96,
        "w_0": -1,
        "w_a": 0,
        "m_nu": 0.0
    }'