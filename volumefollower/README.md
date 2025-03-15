# VolumeFollower

A Kubernetes utility to track volume placements and deploy pods
on the node with the volume already attached to it.

⏺ This is a script to interact with the Kubernetes API that can:

  1. Find which node a PVC (Persistent Volume Claim) is attached to
  2. Display detailed information about the PVC including:
    - Which node it's attached to
    - What pods are using the PVC
    - Volume details and status
  3. Deploy a pod on a specific node

# Usage:

  ## Find which node a PVC is attached to (using default namespace)
  volumefollower pvc-node my-pvc-name

  ## Find which node a PVC is attached to in a specific namespace
  volumefollower pvc-node my-pvc-name -n my-namespace

  ## Use a specific kubeconfig file
  volumefollower pvc-node my-pvc-name --kubeconfig /path/to/kubeconfig

  ## Deploy a pod on a specific node
  volumefollower deploy-pod my-pod worker-node1 -i debian:latest -c "sleep 3600"

  ## Deploy a pod with a PVC mounted
  volumefollower deploy-pod my-pod worker-node1 --pvc my-pvc-name --mount-path /mnt/data

  ## Deploy a pod with a PVC using default mount path (/data)
  volumefollower deploy-pod my-pod worker-node1 --pvc my-pvc-name

  The utility works in both in-cluster and out-of-cluster environments by automatically detecting the appropriate configuration.

# Hacking
To work on this code you should run it in dev mode:
```bash
uv venv .venv && source .venv/bin/activate && uv pip install -e ".[dev]"
```
# TODO
- Add tests for the pod deployment code
- Add support for multiple PVC mounts in a single pod
