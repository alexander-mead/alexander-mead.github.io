import argparse

import requests

# Read the server URL from command line arguments
parser = argparse.ArgumentParser(description="Test the worlds server.")
parser.add_argument(
    "--server", type=str, required=True, help="The URL of the server to test."
)
args = parser.parse_args()

response = requests.get(f"{args.server}/ping")
print("Ping Response:", response.json())

response = requests.post(f"{args.server}/worlds")
print("Worlds Response:", response.json())
