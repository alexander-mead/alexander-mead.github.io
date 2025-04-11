# Read the URL from the command line
# url=http://127.0.0.1:3000/nbody
# url=https://wfa3ikw7ra.execute-api.eu-west-2.amazonaws.com/Prod/nbody # Personal
if [[ -z "${1:-}"  ]]; then
    echo "Usage: $0 <url> [<api_key>]" 
    exit 1
fi
URL=$1
API_KEY=${2:-}

curl --request POST $URL \
    --header "Content-Type: application/json" \
    --header "Accept: application/json" \
    --header "X-Api-Key: $API_KEY" \
    --data '{
        "kmin": 0.001,
        "kmax": 10,
        "nk": 100,
        "z": 0,
        "color": "cubehelix",
        "npix": 100,
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