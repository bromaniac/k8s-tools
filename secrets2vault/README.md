## Project Overview
These scripts form a pipeline for processing secrets and storing them in HashiCorp Vault.

There is a Go implementation of the decoder for use by people that don't have Python installed.

Instead of create-secrets.py I suggest the excellent Medusa tool for import into Vault: [Medusa](https://github.com/jonasvinther/medusa)

### decode-stdin.py
**Purpose**: Decodes Base64-encoded secrets from stdin

Get the secret like this:
```bash
kubectl get secret -n myns mysecret -oyaml | yq '.data'
```

**Process**:
1. Reads lines from standard input
2. Each line should be in format `key: base64-encoded-value`
3. Decodes the Base64 values
4. Outputs decoded key-value pairs in format `key: decoded-value`

**Usage**:
```bash
cat encoded_secrets.txt | python decode-stdin.py
```

### create-secret.py
**Purpose**: Stores decoded secrets into HashiCorp Vault

**Process**:
1. Takes required arguments:
   - `--path`: Vault path where secrets will be stored
   - `--engine`: Vault secrets engine name
   - `--token`: Vault authentication token
2. Reads key-value pairs from stdin (format: `key: value`)
3. Stores each secret in Vault at specified path

**Usage**:
```bash
python create-secret.py --path <path> --engine <engine> --token <token> < decoded_secrets.txt
```

### Combined Pipeline Usage
```bash
cat encoded_secrets.txt | python decode-stdin.py | python create-secret.py --path <path> --engine <engine> --token <token>
```

This pipeline decodes Base64 secrets and stores them directly in Vault in one operation.

### Links
https://www.freekb.net/Article?id=5568
