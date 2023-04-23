# Standard imports
import json
import base64

# Project imports
import mandelbrot


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
    real_centre = float(body["real"])
    imag_centre = float(body["imag"])
    patch_zoom = float(body["zoom"])
    max_iters = int(body["depth"])
    cmap = body["color"]
    rmin, rmax = real_centre-1./patch_zoom, real_centre+1./patch_zoom
    imin, imax = imag_centre-1./patch_zoom, imag_centre+1./patch_zoom
    width, height = int(body["width"]), int(body["height"])
    sigma = float(body["sigma"])
    transform = float(body["transform"])
    smooth = True
    bound = True
    method = "numba"
    data = mandelbrot.create_image(
        rmin, rmax, imin, imax, max_iters, width, height,
        sigma=sigma, transform=transform,
        cmap=cmap, smooth=smooth, bound=bound, method=method)
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
