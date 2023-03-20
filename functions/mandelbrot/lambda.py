import json
import base64

# TODO: Check on relative import vs. ... import
# from . import mandelbrot
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
    # if patch_depth == 'low':
    #     max_iters = 64
    # elif patch_depth == 'medium':
    #     max_iters = 128
    # elif patch_depth == 'high':
    #     max_iters = 256
    # elif patch_depth == 'vhigh':
    #     max_iters = 512
    # else:
    #     raise Exception("Invalid patch depth.")
    # max_iters = int(patch_depth)
    width, height = 1000, 1000
    # if color_scheme == 'binary':
    #     cmap = 'binary_r'
    # else:
    #     cmap = color_scheme
    sigma = 0.75
    data = mandelbrot.create_image(
        rmin, rmax, imin, imax, max_iters, width, height,
        cmap=cmap, figsize=(6, 6), dpi=224, sigma=sigma)

    # Return the response
    response = {
        "message": "Request received.",
        "data": str(data),  # TODO: Is this necessary?
    }
    return {
        "statusCode": 200,  # 200 = OK
        "headers": {  # Headers are necessary for CORS
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        },
        "body": json.dumps(response),
    }
