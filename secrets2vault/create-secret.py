import hvac
import sys
import argparse

# Add command line argument handling
parser = argparse.ArgumentParser(description="Write secrets to Vault")
parser.add_argument("--path", required=True, help="Path where secrets will be stored")
parser.add_argument("--engine", required=True, help="Secrets engine name")
parser.add_argument("--token", required=True, help="Vault token")

# Parse arguments
try:
    args = parser.parse_args()
except SystemExit:
    print(
        "Error: Missing required arguments. Need --path, --engine, and --token",
        file=sys.stderr,
    )
    sys.exit(1)

# Store arguments in variables
path = args.path
engine = args.engine
token = args.token

# Authentication
client = hvac.Client(
    url="http://127.0.0.1:8200",
    token=token,
)

# Exit if we are not connected to Vault
if not client.is_authenticated():
    print("Error: Failed to authenticate with Vault", file=sys.stderr)
    sys.exit(1)


# Split the line into key and value
def process_lines(lines):
    split_dict = {}
    for line in lines:
        try:
            key, value = line.strip().split(": ")
            split_dict[key] = value
        except ValueError:
            print(f"Error processing line: {line.strip()}", file=sys.stderr)
            print("Lines must be in 'key: value' format", file=sys.stderr)
            sys.exit(1)
    return split_dict


# Read lines from standard input
lines = sys.stdin.readlines()

# Process lines and return a dict
secrets_dict = process_lines(lines)

# Write the secrets to Vault
create_response = client.secrets.kv.v2.create_or_update_secret(
    path=path,
    mount_point=engine,
    secret=secrets_dict,
)

print("Wrote secrets to Vault")
client.logout()
