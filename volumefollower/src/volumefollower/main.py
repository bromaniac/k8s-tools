"""Main module for the VolumeFollower application.

This module provides functionality to find a PVC's node attachment and
deploy a pod on that node with the PVC mounted.
"""

import argparse
import sys

from volumefollower.k8s import deploy_pod_on_node, find_pvc_node, initialize_client


def main(args=None):
    """Run the main application to follow a PVC with a pod.

    Finds which node a PVC is attached to and deploys a Debian pod
    on that node with the PVC mounted at /data, running a sleep infinity command.

    Args:
        args: Command line arguments (uses sys.argv if None)

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(description="VolumeFollower Kubernetes utilities")
    parser.add_argument("pvc_name", help="Name of the PVC to follow")
    parser.add_argument(
        "-n", "--namespace", default="default", help="Kubernetes namespace"
    )
    parser.add_argument("--kubeconfig", help="Path to kubeconfig file")

    # Parse arguments
    parsed_args = parser.parse_args(args)

    try:
        # Initialize kubernetes client
        initialize_client(parsed_args.kubeconfig)

        # Find which node the PVC is attached to
        node_name = find_pvc_node(parsed_args.pvc_name, parsed_args.namespace)

        if not node_name:
            print(
                f"Error: PVC {parsed_args.pvc_name} is not attached to any node",
                file=sys.stderr,
            )
            return 1

        print(f"PVC {parsed_args.pvc_name} is attached to node {node_name}")

        # Generate a pod name based on PVC name
        pod_name = f"volumefollower-{parsed_args.pvc_name}"

        # Deploy the pod on the same node as the PVC
        pod_info = deploy_pod_on_node(
            pod_name=pod_name,
            node_name=node_name,
            namespace=parsed_args.namespace,
            image="debian:latest",
            command=["/bin/sleep", "infinity"],
            pvc_name=parsed_args.pvc_name,
            mount_path="/data",
            kubeconfig=parsed_args.kubeconfig,
        )

        # Display the results
        print("Pod successfully deployed:")
        print(f"Name: {pod_info['name']}")
        print(f"Namespace: {pod_info['namespace']}")
        print(f"Status: {pod_info['status']}")
        print(f"Node: {pod_info['node']}")
        print(f"PVC: {parsed_args.pvc_name} mounted at /data")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit(main())
