"""Kubernetes client utilities for VolumeFollower.

This module provides functions to interact with Kubernetes to find
which node a PVC is attached to and deploy a pod on that node with
the PVC mounted. It uses the official Kubernetes Python client.
"""

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException


def initialize_client(config_file=None):
    """Initialize the Kubernetes client configuration.

    Args:
        config_file: Optional path to kubeconfig file. If None, uses default
            location (~/.kube/config) or in-cluster configuration.
    """
    try:
        if config_file:
            config.load_kube_config(config_file=config_file)
        else:
            try:
                # Try loading from default config file
                config.load_kube_config()
            except config.config_exception.ConfigException:
                # If not available, try in-cluster config
                config.load_incluster_config()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Kubernetes client: {e}") from e


def find_pvc_node(pvc_name, pvc_namespace="default"):
    """Find the node a specific PVC is attached to.

    Args:
        pvc_name: Name of the PersistentVolumeClaim
        pvc_namespace: Namespace of the PersistentVolumeClaim

    Returns:
        Node name if found, None otherwise
    """
    # Initialize API clients
    core_v1 = client.CoreV1Api()
    storage_v1 = client.StorageV1Api()

    # Get the PVC to find its PV
    try:
        pvc = core_v1.read_namespaced_persistent_volume_claim(
            name=pvc_name, namespace=pvc_namespace
        )

        # If PVC doesn't have a volume yet, it's not attached
        if not pvc.spec.volume_name:
            return None

        pv_name = pvc.spec.volume_name
    except ApiException as e:
        raise RuntimeError(f"Failed to get PVC {pvc_name}: {e}") from e

    # Check volume attachments to find which node has this PV attached
    try:
        attachments = storage_v1.list_volume_attachment()

        for attachment in attachments.items:
            # Check if this attachment is for our PV
            if (
                attachment.spec.source.persistent_volume_name == pv_name
                and attachment.status
                and attachment.status.attached
            ):
                return attachment.spec.node_name

        # If we get here, we didn't find an attachment
        return None
    except ApiException as e:
        raise RuntimeError(f"Failed to list volume attachments: {e}") from e


def deploy_pod_on_node(
    pod_name,
    node_name,
    namespace="default",
    image="debian:latest",
    command=None,
    args=None,
    labels=None,
    annotations=None,
    kubeconfig=None,
    pvc_name=None,
    mount_path="/data",
):
    """Deploy a pod on a specific Kubernetes node.

    Creates a Debian pod on the specified node, that runs
    "sleep infinity" with a specified PVC mounted at /data.

    Args:
        pod_name: Name to give the pod
        node_name: Name of the node to schedule the pod on
        namespace: Kubernetes namespace for the pod
        image: Container image to use (defaults to debian:latest)
        command: List of command strings to override the image's entrypoint
        args: List of arguments to the command
        labels: Dictionary of labels to apply to the pod
        annotations: Dictionary of annotations to apply to the pod
        kubeconfig: Path to kubeconfig file
        pvc_name: Name of PVC to mount in the pod
        mount_path: Path to mount the PVC in the container (default: /data)

    Returns:
        Dictionary with pod details including status
    """
    # Make sure the kubernetes client is initialized
    initialize_client(kubeconfig)

    # Initialize the CoreV1Api client
    core_v1 = client.CoreV1Api()

    # Prepare container for pod spec
    container = client.V1Container(
        name=f"{pod_name}-container",
        image=image,
        # Default sleep command if none specified
        command=(
            ["/bin/sleep", "infinity"] if command is None and args is None else command
        ),
        args=args,
    )

    # Add volume mount to container if PVC is specified
    volumes = []
    if pvc_name:
        # Add volume mount to container
        container.volume_mounts = [
            client.V1VolumeMount(name="data-volume", mount_path=mount_path)
        ]

        # Add volume to pod spec
        volumes.append(
            client.V1Volume(
                name="data-volume",
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                    claim_name=pvc_name
                ),
            )
        )

    # Set up the pod configuration
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(
            name=pod_name,
            namespace=namespace,
            labels=labels or {},
            annotations=annotations or {},
        ),
        spec=client.V1PodSpec(
            node_name=node_name,  # Ensure pod runs on the specified node
            containers=[container],
            volumes=volumes if volumes else None,
            restart_policy="Never",  # Don't restart the pod when it completes
        ),
    )

    try:
        # Create the pod
        created_pod = core_v1.create_namespaced_pod(namespace=namespace, body=pod)

        # Return pod details
        return {
            "name": created_pod.metadata.name,
            "namespace": created_pod.metadata.namespace,
            "node": created_pod.spec.node_name,
            "status": created_pod.status.phase,
            "creation_time": (
                created_pod.metadata.creation_timestamp.isoformat()
                if created_pod.metadata.creation_timestamp
                else None
            ),
        }

    except ApiException as e:
        msg = f"Failed to create pod {pod_name} on node {node_name}: {e}"
        raise RuntimeError(msg) from e
