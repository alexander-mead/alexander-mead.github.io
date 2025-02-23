# Read the URL from the command line
# url=http://127.0.0.1:3000/nbody
# url=https://qte7wuo072.execute-api.eu-west-2.amazonaws.com/Prod/nbody # digiLab
# url=https://g6afw1nc9a.execute-api.eu-west-2.amazonaws.com/Prod/nbody # Personal
if [ "$#" -ne 1 ]; then
    echo "Usage: test.sh <url>" 
    exit 1
fi
url=$1

curl --request POST $url \
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