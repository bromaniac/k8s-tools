import base64
import sys


def decrypt_base64(encoded_str):
    # Decode the base64 encoded string
    decoded_bytes = base64.b64decode(encoded_str)
    # Convert bytes to string
    decoded_str = decoded_bytes.decode("utf-8")
    return decoded_str


def process_lines(lines):
    decrypted_dict = {}
    for line in lines:
        # Split the line into key and base64 encoded string
        try:
            key, encoded_str = line.strip().split(": ")
            # Decrypt the base64 encoded string
            decrypted_str = decrypt_base64(encoded_str)
            # Store the result in dictionary
            decrypted_dict[key] = decrypted_str
        except ValueError as e:
            print(f"Error processing line: {line.strip()}", file=sys.stderr)
            print(f"Details: {str(e)}", file=sys.stderr)
            sys.exit(1)
    return decrypted_dict


# Read lines from standard input
lines = sys.stdin.readlines()

# Process lines and decrypt base64 strings
decrypted_dict = process_lines(lines)

# Print the results
for key, value in decrypted_dict.items():
    print(f"{key}: {value}")

# this tool decrypts base64 in a key: b64(value) pair e.g. k8s secrets
# usage: kubectl get secret -n myns mysecret -oyaml | yq '.data' | python3 decode-stdin.py
