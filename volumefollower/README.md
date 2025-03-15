# VolumeFollower

A simple Kubernetes utility to deploy a pod on the node where a PVC is attached.

## What it does

This tool:
1. Finds which node a PVC (Persistent Volume Claim) is attached to
2. Deploys a Debian pod on that node with the PVC mounted at /data
3. Configures the pod to run "sleep infinity" (never terminate)

## Usage

```
volumefollower my-pvc-name -n my-namespace
```

### Arguments

- `pvc_name`: Name of the PVC to follow (required)
- `-n, --namespace`: Kubernetes namespace (defaults to "default")
- `--kubeconfig`: Path to kubeconfig file (optional)

### Example

```bash
# Follow a PVC in the default namespace
volumefollower my-pvc

# Follow a PVC in a specific namespace
volumefollower my-pvc -n my-namespace 

# Use a specific kubeconfig file
volumefollower my-pvc --kubeconfig /path/to/kubeconfig
```

The utility works in both in-cluster and out-of-cluster environments by automatically detecting the appropriate configuration.

## Development

To work on this code you should run it in dev mode:
```bash
uv venv .venv && source .venv/bin/activate && uv pip install -e ".[dev]"
```
