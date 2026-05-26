"""
ZenithOne Explorer CLI - Container Commands

Handles container management including listing, starting, stopping, and monitoring.
"""

import argparse
from typing import Dict, Any


def register(subparsers) -> None:
    """Register container commands."""
    
    # Main container command
    container_parser = subparsers.add_parser(
        'container',
        help='Manage containers',
        description='Create, start, stop, and monitor containers'
    )
    
    container_subparsers = container_parser.add_subparsers(
        title='container commands',
        dest='container_command',
        help='Container operations'
    )
    
    # List containers
    list_parser = container_subparsers.add_parser(
        'list',
        help='List containers',
        description='List all containers with optional filtering'
    )
    list_parser.add_argument(
        '--status',
        choices=['running', 'stopped', 'paused', 'exited'],
        help='Filter by status'
    )
    list_parser.add_argument(
        '--all',
        action='store_true',
        help='Show all containers (including stopped)'
    )
    
    # Get container details
    get_parser = container_subparsers.add_parser(
        'get',
        help='Get container details',
        description='Display detailed information about a specific container'
    )
    get_parser.add_argument(
        'container_id',
        help='Container ID or name'
    )
    
    # Start container
    start_parser = container_subparsers.add_parser(
        'start',
        help='Start container',
        description='Start a stopped container'
    )
    start_parser.add_argument(
        'container_id',
        help='Container ID or name'
    )
    
    # Stop container
    stop_parser = container_subparsers.add_parser(
        'stop',
        help='Stop container',
        description='Stop a running container'
    )
    stop_parser.add_argument(
        'container_id',
        help='Container ID or name'
    )
    stop_parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Timeout in seconds before force kill (default: 10)'
    )
    
    # Restart container
    restart_parser = container_subparsers.add_parser(
        'restart',
        help='Restart container',
        description='Restart a container'
    )
    restart_parser.add_argument(
        'container_id',
        help='Container ID or name'
    )
    
    # Delete container
    delete_parser = container_subparsers.add_parser(
        'delete',
        help='Delete container',
        description='Delete a container'
    )
    delete_parser.add_argument(
        'container_id',
        help='Container ID or name'
    )
    delete_parser.add_argument(
        '--force',
        action='store_true',
        help='Force deletion without confirmation'
    )
    
    # Get container logs
    logs_parser = container_subparsers.add_parser(
        'logs',
        help='Get container logs',
        description='Display logs from a container'
    )
    logs_parser.add_argument(
        'container_id',
        help='Container ID or name'
    )
    logs_parser.add_argument(
        '--tail',
        type=int,
        default=100,
        help='Number of lines to show (default: 100)'
    )
    logs_parser.add_argument(
        '--follow',
        action='store_true',
        help='Follow log output'
    )
    
    # Inspect container
    inspect_parser = container_subparsers.add_parser(
        'inspect',
        help='Inspect container',
        description='Display detailed container information'
    )
    inspect_parser.add_argument(
        'container_id',
        help='Container ID or name'
    )
    
    # Container stats
    stats_parser = container_subparsers.add_parser(
        'stats',
        help='Container statistics',
        description='Display resource usage statistics for containers'
    )
    stats_parser.add_argument(
        'container_id',
        nargs='?',
        help='Container ID or name (optional, shows all if omitted)'
    )


def execute(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """
    Execute container command.
    
    Args:
        args: Command arguments
        context: CLI context
        
    Returns:
        Exit code
    """
    if not args.container_command:
        context['output'].error("No container command specified. Use 'zenith container --help' for usage.")
        return 1
    
    # Map commands to handlers
    command_handlers = {
        'list': list_containers,
        'get': get_container,
        'start': start_container,
        'stop': stop_container,
        'restart': restart_container,
        'delete': delete_container,
        'logs': get_logs,
        'inspect': inspect_container,
        'stats': get_stats,
    }
    
    handler = command_handlers.get(args.container_command)
    if not handler:
        context['output'].error(f"Unknown container command: {args.container_command}")
        return 1
    
    return handler(args, context)


def list_containers(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """List containers."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info("Fetching containers...")
        containers = api_client.list_containers(status=args.status)
        
        if not containers:
            output.info("No containers found")
            return 0
        
        # Format for display
        headers = ['ID', 'Name', 'Image', 'Status', 'Created']
        output.print_data(containers, headers=headers)
        
        output.print(f"\nTotal: {len(containers)} container(s)")
        return 0
        
    except Exception as e:
        output.error(f"Failed to list containers: {e}")
        return 1


def get_container(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Get container details."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info(f"Fetching container {args.container_id}...")
        container = api_client.get_container(args.container_id)
        
        output.print_data(container)
        return 0
        
    except Exception as e:
        output.error(f"Failed to get container: {e}")
        return 1


def start_container(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Start container."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info(f"Starting container {args.container_id}...")
        result = api_client.start_container(args.container_id)
        
        output.success("Container started successfully")
        output.print_data(result)
        return 0
        
    except Exception as e:
        output.error(f"Failed to start container: {e}")
        return 1


def stop_container(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Stop container."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info(f"Stopping container {args.container_id}...")
        result = api_client.stop_container(args.container_id)
        
        output.success("Container stopped successfully")
        output.print_data(result)
        return 0
        
    except Exception as e:
        output.error(f"Failed to stop container: {e}")
        return 1


def restart_container(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Restart container."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info(f"Restarting container {args.container_id}...")
        result = api_client.restart_container(args.container_id)
        
        output.success("Container restarted successfully")
        output.print_data(result)
        return 0
        
    except Exception as e:
        output.error(f"Failed to restart container: {e}")
        return 1


def delete_container(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Delete container."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        # Confirm deletion unless --force
        if not args.force:
            response = input(f"Are you sure you want to delete container {args.container_id}? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                output.info("Deletion cancelled")
                return 0
        
        output.info(f"Deleting container {args.container_id}...")
        api_client.delete_container(args.container_id)
        
        output.success("Container deleted successfully")
        return 0
        
    except Exception as e:
        output.error(f"Failed to delete container: {e}")
        return 1


def get_logs(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Get container logs."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info(f"Fetching logs for container {args.container_id}...")
        logs = api_client.get_container_logs(args.container_id, tail=args.tail)
        
        if 'logs' in logs:
            output.print(logs['logs'])
        else:
            output.print_data(logs)
        
        return 0
        
    except Exception as e:
        output.error(f"Failed to get logs: {e}")
        return 1


def inspect_container(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Inspect container."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info(f"Inspecting container {args.container_id}...")
        container = api_client.get_container(args.container_id)
        
        output.print_data(container)
        return 0
        
    except Exception as e:
        output.error(f"Failed to inspect container: {e}")
        return 1


def get_stats(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Get container statistics."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        if args.container_id:
            output.info(f"Fetching stats for container {args.container_id}...")
            stats = api_client.get_container_metrics(args.container_id)
        else:
            output.info("Fetching stats for all containers...")
            stats = api_client.get_container_metrics()
        
        output.print_data(stats)
        return 0
        
    except Exception as e:
        output.error(f"Failed to get stats: {e}")
        return 1
