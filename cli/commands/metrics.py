"""
ZenithOne Explorer CLI - Metrics Commands

Display system, workload, and container performance metrics.
"""

import argparse
from typing import Dict, Any


def register(subparsers) -> None:
    """Register metrics commands."""
    
    # Main metrics command
    metrics_parser = subparsers.add_parser(
        'metrics',
        help='View performance metrics',
        description='Display system, workload, and container metrics'
    )
    
    metrics_subparsers = metrics_parser.add_subparsers(
        title='metrics commands',
        dest='metrics_command',
        help='Metrics operations'
    )
    
    # System metrics
    system_parser = metrics_subparsers.add_parser(
        'system',
        help='System metrics',
        description='Display system-wide performance metrics'
    )
    system_parser.add_argument(
        '--refresh',
        type=int,
        help='Auto-refresh interval in seconds'
    )
    
    # Workload metrics
    workload_parser = metrics_subparsers.add_parser(
        'workload',
        help='Workload metrics',
        description='Display workload performance metrics'
    )
    workload_parser.add_argument(
        'workload_id',
        nargs='?',
        help='Workload ID (optional, shows all if omitted)'
    )
    workload_parser.add_argument(
        '--refresh',
        type=int,
        help='Auto-refresh interval in seconds'
    )
    
    # Container metrics
    container_parser = metrics_subparsers.add_parser(
        'container',
        help='Container metrics',
        description='Display container resource usage metrics'
    )
    container_parser.add_argument(
        'container_id',
        nargs='?',
        help='Container ID (optional, shows all if omitted)'
    )
    container_parser.add_argument(
        '--refresh',
        type=int,
        help='Auto-refresh interval in seconds'
    )
    
    # Performance summary
    summary_parser = metrics_subparsers.add_parser(
        'summary',
        help='Performance summary',
        description='Display overall performance summary'
    )


def execute(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Execute metrics command."""
    if not args.metrics_command:
        context['output'].error("No metrics command specified. Use 'zenith metrics --help' for usage.")
        return 1
    
    handlers = {
        'system': show_system_metrics,
        'workload': show_workload_metrics,
        'container': show_container_metrics,
        'summary': show_summary,
    }
    
    handler = handlers.get(args.metrics_command)
    if not handler:
        context['output'].error(f"Unknown metrics command: {args.metrics_command}")
        return 1
    
    return handler(args, context)


def show_system_metrics(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Show system metrics."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info("Fetching system metrics...")
        metrics = api_client.get_system_metrics()
        
        # Format metrics for display
        if 'cpu' in metrics:
            output.print("\n=== CPU Metrics ===")
            output.print_data(metrics['cpu'])
        
        if 'memory' in metrics:
            output.print("\n=== Memory Metrics ===")
            output.print_data(metrics['memory'])
        
        if 'disk' in metrics:
            output.print("\n=== Disk Metrics ===")
            output.print_data(metrics['disk'])
        
        if 'network' in metrics:
            output.print("\n=== Network Metrics ===")
            output.print_data(metrics['network'])
        
        return 0
        
    except Exception as e:
        output.error(f"Failed to fetch system metrics: {e}")
        return 1


def show_workload_metrics(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Show workload metrics."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        if args.workload_id:
            output.info(f"Fetching metrics for workload {args.workload_id}...")
            metrics = api_client.get_workload_metrics(args.workload_id)
        else:
            output.info("Fetching metrics for all workloads...")
            metrics = api_client.get_workload_metrics()
        
        output.print_data(metrics)
        return 0
        
    except Exception as e:
        output.error(f"Failed to fetch workload metrics: {e}")
        return 1


def show_container_metrics(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Show container metrics."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        if args.container_id:
            output.info(f"Fetching metrics for container {args.container_id}...")
            metrics = api_client.get_container_metrics(args.container_id)
        else:
            output.info("Fetching metrics for all containers...")
            metrics = api_client.get_container_metrics()
        
        output.print_data(metrics)
        return 0
        
    except Exception as e:
        output.error(f"Failed to fetch container metrics: {e}")
        return 1


def show_summary(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Show performance summary."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info("Fetching performance summary...")
        
        # Get all metrics
        system_metrics = api_client.get_system_metrics()
        workload_metrics = api_client.get_workload_metrics()
        container_metrics = api_client.get_container_metrics()
        
        # Display summary
        output.print("\n=== Performance Summary ===\n")
        
        output.print("System:")
        if 'cpu' in system_metrics:
            output.print(f"  CPU Usage: {system_metrics['cpu'].get('usage_percent', 'N/A')}%")
        if 'memory' in system_metrics:
            output.print(f"  Memory Usage: {system_metrics['memory'].get('usage_percent', 'N/A')}%")
        
        output.print("\nWorkloads:")
        if isinstance(workload_metrics, list):
            output.print(f"  Total: {len(workload_metrics)}")
            running = sum(1 for w in workload_metrics if w.get('status') == 'running')
            output.print(f"  Running: {running}")
        
        output.print("\nContainers:")
        if isinstance(container_metrics, list):
            output.print(f"  Total: {len(container_metrics)}")
            running = sum(1 for c in container_metrics if c.get('status') == 'running')
            output.print(f"  Running: {running}")
        
        return 0
        
    except Exception as e:
        output.error(f"Failed to fetch performance summary: {e}")
        return 1
