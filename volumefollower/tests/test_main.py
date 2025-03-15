"""Tests for the main module."""

import sys
from unittest.mock import patch

from volumefollower import get_pvc_node, main


def test_main_no_args():
    """Test the main function with no args shows help and returns error code."""
    with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
        mock_parse_args.return_value.command = None
        assert main([]) == 1


def test_main_invalid_command():
    """Test the main function with invalid command shows help and returns error code."""
    with patch("sys.argv", ["volumefollower", "invalid-command"]):
        with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
            mock_parse_args.return_value.command = None
            assert main() == 1


@patch("volumefollower.main.get_pvc_node")
def test_main_pvc_node_command(mock_get_pvc_node):
    """Test the main function with pvc-node command calls get_pvc_node."""
    mock_get_pvc_node.return_value = 0

    with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
        mock_parse_args.return_value.command = "pvc-node"
        mock_parse_args.return_value.pvc_name = "test-pvc"
        mock_parse_args.return_value.namespace = "default"
        mock_parse_args.return_value.kubeconfig = None

        assert main([]) == 0
        mock_get_pvc_node.assert_called_once_with("test-pvc", "default", None)


@patch("volumefollower.main.initialize_client")
@patch("volumefollower.main.get_pvc_details")
def test_get_pvc_node_success(mock_get_pvc_details, mock_init_client):
    """Test get_pvc_node function with successful retrieval."""
    # Mock the PVC details response
    mock_get_pvc_details.return_value = {
        "name": "test-pvc",
        "namespace": "default",
        "status": "Bound",
        "volume_name": "pv-test",
        "attached_node": "worker-1",
        "pods": [{"name": "pod-1", "status": "Running", "node": "worker-1"}],
    }

    with patch("builtins.print") as mock_print:
        result = get_pvc_node("test-pvc", "default", None)
        assert result == 0

        # Verify client was initialized
        mock_init_client.assert_called_once_with(None)

        # Verify PVC details were retrieved
        mock_get_pvc_details.assert_called_once_with("test-pvc", "default")

        # Check print was called with expected output
        assert any("test-pvc" in args[0] for args, _ in mock_print.call_args_list)
        assert any("worker-1" in args[0] for args, _ in mock_print.call_args_list)


@patch("volumefollower.main.initialize_client")
@patch("volumefollower.main.get_pvc_details")
def test_get_pvc_node_not_attached(mock_get_pvc_details, mock_init_client):
    """Test get_pvc_node function when PVC is not attached."""
    # Mock the PVC details response for unattached PVC
    mock_get_pvc_details.return_value = {
        "name": "test-pvc",
        "namespace": "default",
        "status": "Bound",
        "volume_name": "pv-test",
        # No attached_node key
    }

    with patch("builtins.print") as mock_print:
        result = get_pvc_node("test-pvc", "default", None)
        assert result == 0

        # Check print was called with "Not attached" message
        assert any("Not attached" in args[0] for args, _ in mock_print.call_args_list)


@patch("volumefollower.main.initialize_client")
@patch("volumefollower.main.get_pvc_details")
def test_get_pvc_node_error(mock_get_pvc_details, mock_init_client):
    """Test get_pvc_node function handles errors correctly."""
    # Mock an error in get_pvc_details
    mock_get_pvc_details.side_effect = RuntimeError("Test error")

    with patch("builtins.print") as mock_print:
        result = get_pvc_node("test-pvc", "default", None)
        assert result == 1

        # Verify that print was called with an error message
        error_msg = f"Error: {RuntimeError('Test error')}"
        mock_print.assert_called_with(error_msg, file=sys.stderr)
