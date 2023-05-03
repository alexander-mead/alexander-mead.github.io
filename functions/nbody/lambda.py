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
        "A_s": 2.1e-9,
        "sigma_8": float(body["sigma_8"]),
        "n_s": float(body["n_s"]),
        "m_nu": 0.,
    }
    kmin = float(body["kmin"])
    kmax = float(body["kmax"])
    nk = int(body["nk"])
    z = float(body["z"])
    L = float(body["Lbox"])
    n = int(body["npix"])
    pad = 0.02
    seed = 123
    vmin, vmax = 1e-3, 1e4  # Change these if log_normal_transform = False
    # vmin, vmax = -15., 15.
    cmap = "cubehelix"
    np.random.seed(seed)
    box_h_units = True
    log_normal_transform = True
    plot_log_overdensity = True  # Should be False if log_normal_transform = False
    norm_sigma8 = True
    data = nbody.make_image(params, (kmin, kmax), nk, z, L, n, (vmin, vmax),
                            box_h_units=box_h_units,
                            log_normal_transform=log_normal_transform,
                            plot_log_overdensity=plot_log_overdensity,
                            norm_sigma8=norm_sigma8,
                            cmap=cmap, pad_inches=pad,
                            verbose=True,
                            )
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
