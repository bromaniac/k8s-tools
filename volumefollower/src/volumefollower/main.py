"""Main module for the VolumeFollower application."""

import argparse
import sys

from volumefollower.k8s import deploy_pod_on_node, get_pvc_details, initialize_client


def get_pvc_node(pvc_name, namespace, kubeconfig=None):
    """Get the node a PVC is attached to.

    Args:
        pvc_name: Name of the PVC
        namespace: Kubernetes namespace
        kubeconfig: Path to kubeconfig file (optional)

    Returns:
        int: Exit code (0 for success)
    """
    try:
        # Initialize kubernetes client
        initialize_client(kubeconfig)

        # Get PVC details including node attachment
        pvc_info = get_pvc_details(pvc_name, namespace)

        # Display the results
        print(f"PVC: {pvc_info['name']}")
        print(f"Namespace: {pvc_info['namespace']}")
        print(f"Status: {pvc_info['status']}")
        print(f"Volume: {pvc_info.get('volume_name', 'Not bound')}")

        if "attached_node" in pvc_info and pvc_info["attached_node"]:
            print(f"Attached to node: {pvc_info['attached_node']}")

            if pvc_info.get("pods"):
                print("\nPods using this PVC:")
                for pod in pvc_info["pods"]:
                    print(
                        f"  - {pod['name']} (Status: {pod['status']}, "
                        f"Node: {pod.get('node', 'unknown')})"
                    )
        else:
            print("Not attached to any node")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def deploy_pod(
    pod_name, node_name, namespace, image="debian:latest", command=None, kubeconfig=None
):
    """Deploy a pod on a specific node.

    Args:
        pod_name: Name to give the pod
        node_name: Name of the node to run the pod on
        namespace: Kubernetes namespace
        image: Container image to use (defaults to debian:latest)
        command: Command to run in the container (list of strings)
        kubeconfig: Path to kubeconfig file (optional)

    Returns:
        int: Exit code (0 for success)
    """
    try:
        # Deploy the pod
        pod_info = deploy_pod_on_node(
            pod_name=pod_name,
            node_name=node_name,
            namespace=namespace,
            image=image,
            command=command.split() if command else None,
            kubeconfig=kubeconfig,
        )

        # Display the results
        print("Pod successfully deployed:")
        print(f"Name: {pod_info['name']}")
        print(f"Namespace: {pod_info['namespace']}")
        print(f"Status: {pod_info['status']}")
        print(f"Node: {pod_info['node']}")
        if "creation_time" in pod_info and pod_info["creation_time"]:
            print(f"Created at: {pod_info['creation_time']}")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(args=None):
    """Run the main application.

    Args:
        args: Command line arguments (uses sys.argv if None)

    Returns:
        int: Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(description="VolumeFollower Kubernetes utilities")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # PVC node finder command
    pvc_parser = subparsers.add_parser(
        "pvc-node", help="Find which node a PVC is attached to"
    )
    pvc_parser.add_argument("pvc_name", help="Name of the PVC")
    pvc_parser.add_argument(
        "-n", "--namespace", default="default", help="Kubernetes namespace"
    )
    pvc_parser.add_argument("--kubeconfig", help="Path to kubeconfig file")

    # Pod deployment command
    pod_parser = subparsers.add_parser(
        "deploy-pod", help="Deploy a pod on a specific node"
    )
    pod_parser.add_argument("pod_name", help="Name for the pod")
    pod_parser.add_argument("node_name", help="Name of the node to run the pod on")
    pod_parser.add_argument(
        "-n", "--namespace", default="default", help="Kubernetes namespace"
    )
    pod_parser.add_argument(
        "-i", "--image", default="debian:latest", help="Container image to use"
    )
    pod_parser.add_argument("-c", "--command", help="Command to run in the container")
    pod_parser.add_argument("--kubeconfig", help="Path to kubeconfig file")

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # Execute the appropriate command
    if parsed_args.command == "pvc-node":
        return get_pvc_node(
            parsed_args.pvc_name, parsed_args.namespace, parsed_args.kubeconfig
        )
    elif parsed_args.command == "deploy-pod":
        return deploy_pod(
            parsed_args.pod_name,
            parsed_args.node_name,
            parsed_args.namespace,
            parsed_args.image,
            parsed_args.command,
            parsed_args.kubeconfig,
        )
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
