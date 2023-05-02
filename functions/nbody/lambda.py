# Standard imports
import json
import base64

# Project imports
import numpy as np
import nbody


def unwrap_payload(event):
    if "body" not in event:  # Get body
        raise Exception("No body in request.")
    body = event["body"]
    if "isBase64Encoded" in event:  # Decode
        if event["isBase64Encoded"]:
            body = base64.b64decode(body)
    try:  # Parse
        payload = json.loads(body)
    except:
        raise Exception("Could not parse body as JSON.")
    return payload


def handler(event, context, verbose=True):
    # Necessary for lambda.py

    # See what the handler receives
    if verbose:
        print()
        print("Event:", type(event), event, "\n")
        print("Event body:", type(event["body"]), event["body"], "\n")
        print("Context:", type(context), context, "\n")

    # Generate image
    body = unwrap_payload(event)
    params = {
        "Omega_m": float(body["Omega_m"]),
        "Omega_b": float(body["Omega_b"]),
        "H_0": float(body["H_0"]),
        "w_0": -1.,
        "w_a": 0.,
        "sigma_8": float(body["sigma_8"]),
        "n_s": float(body["n_s"]),
        "m_nu": 0.,
    }
    kmin = 1e-3
    kmax = 1e1
    nk = 128
    z = 0.
    L = 512.
    n = 1000
    pad = 0.02
    seed = 123
    np.random.seed(seed)
    data = nbody.make_image(params, (kmin, kmax), nk, z, L, n, pad_inches=pad)
    data = base64.b64encode(data)  # Encode to base64 bytes
    data = data.decode()           # Convert bytes to string

    # Construct the response
    status = 200  # 200 = OK
    headers = {  # Headers are necessary for CORS
        "Content-Type": "application/json",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "*",
        "Access-Control-Allow-Methods": "*",
    }
    response = {
        "message": "Request received.",
        "data": data,
    }

    # Return the response
    result = {
        "statusCode": status,
        "headers": headers,
        "body": json.dumps(response),
    }
    return result
