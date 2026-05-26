"""
ZenithOne Explorer CLI - Workload Commands

Handles workload management including listing, creating, scheduling, and monitoring.
"""

import argparse
import json
from typing import Dict, Any
from pathlib import Path


def register(subparsers) -> None:
    """Register workload commands."""
    
    # Main workload command
    workload_parser = subparsers.add_parser(
        'workload',
        help='Manage workloads',
        description='Create, schedule, and monitor workloads'
    )
    
    workload_subparsers = workload_parser.add_subparsers(
        title='workload commands',
        dest='workload_command',
        help='Workload operations'
    )
    
    # List workloads
    list_parser = workload_subparsers.add_parser(
        'list',
        help='List workloads',
        description='List all workloads with optional filtering'
    )
    list_parser.add_argument(
        '--status',
        choices=['pending', 'running', 'completed', 'failed', 'cancelled'],
        help='Filter by status'
    )
    list_parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Maximum number of results (default: 100)'
    )
    list_parser.add_argument(
        '--offset',
        type=int,
        default=0,
        help='Offset for pagination (default: 0)'
    )
    
    # Get workload details
    get_parser = workload_subparsers.add_parser(
        'get',
        help='Get workload details',
        description='Display detailed information about a specific workload'
    )
    get_parser.add_argument(
        'workload_id',
        help='Workload ID'
    )
    
    # Create workload
    create_parser = workload_subparsers.add_parser(
        'create',
        help='Create new workload',
        description='Create a new workload from specification'
    )
    create_parser.add_argument(
        '--name',
        required=True,
        help='Workload name'
    )
    create_parser.add_argument(
        '--type',
        required=True,
        choices=['batch', 'interactive', 'service', 'scheduled'],
        help='Workload type'
    )
    create_parser.add_argument(
        '--image',
        required=True,
        help='Container image'
    )
    create_parser.add_argument(
        '--command',
        help='Command to execute'
    )
    create_parser.add_argument(
        '--args',
        nargs='*',
        help='Command arguments'
    )
    create_parser.add_argument(
        '--env',
        action='append',
        help='Environment variables (KEY=VALUE)'
    )
    create_parser.add_argument(
        '--cpu',
        type=float,
        help='CPU limit (cores)'
    )
    create_parser.add_argument(
        '--memory',
        type=int,
        help='Memory limit (MB)'
    )
    create_parser.add_argument(
        '--priority',
        choices=['low', 'normal', 'high', 'critical'],
        default='normal',
        help='Workload priority (default: normal)'
    )
    create_parser.add_argument(
        '--file',
        type=str,
        help='Load workload specification from JSON file'
    )
    
    # Update workload
    update_parser = workload_subparsers.add_parser(
        'update',
        help='Update workload',
        description='Update an existing workload'
    )
    update_parser.add_argument(
        'workload_id',
        help='Workload ID'
    )
    update_parser.add_argument(
        '--name',
        help='New workload name'
    )
    update_parser.add_argument(
        '--priority',
        choices=['low', 'normal', 'high', 'critical'],
        help='New priority'
    )
    update_parser.add_argument(
        '--file',
        type=str,
        help='Load update specification from JSON file'
    )
    
    # Delete workload
    delete_parser = workload_subparsers.add_parser(
        'delete',
        help='Delete workload',
        description='Delete a workload'
    )
    delete_parser.add_argument(
        'workload_id',
        help='Workload ID'
    )
    delete_parser.add_argument(
        '--force',
        action='store_true',
        help='Force deletion without confirmation'
    )
    
    # Schedule workload
    schedule_parser = workload_subparsers.add_parser(
        'schedule',
        help='Schedule workload',
        description='Schedule a workload for execution'
    )
    schedule_parser.add_argument(
        'workload_id',
        help='Workload ID'
    )
    
    # Get workload logs
    logs_parser = workload_subparsers.add_parser(
        'logs',
        help='Get workload logs',
        description='Display execution logs for a workload'
    )
    logs_parser.add_argument(
        'workload_id',
        help='Workload ID'
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
    
    # Get workload status
    status_parser = workload_subparsers.add_parser(
        'status',
        help='Get workload status',
        description='Display current status of a workload'
    )
    status_parser.add_argument(
        'workload_id',
        help='Workload ID'
    )


def execute(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """
    Execute workload command.
    
    Args:
        args: Command arguments
        context: CLI context
        
    Returns:
        Exit code
    """
    if not args.workload_command:
        context['output'].error("No workload command specified. Use 'zenith workload --help' for usage.")
        return 1
    
    # Map commands to handlers
    command_handlers = {
        'list': list_workloads,
        'get': get_workload,
        'create': create_workload,
        'update': update_workload,
        'delete': delete_workload,
        'schedule': schedule_workload,
        'logs': get_logs,
        'status': get_status,
    }
    
    handler = command_handlers.get(args.workload_command)
    if not handler:
        context['output'].error(f"Unknown workload command: {args.workload_command}")
        return 1
    
    return handler(args, context)


def list_workloads(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """List workloads."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info("Fetching workloads...")
        workloads = api_client.list_workloads(
            status=args.status,
            limit=args.limit,
            offset=args.offset
        )
        
        if not workloads:
            output.info("No workloads found")
            return 0
        
        # Format for display
        headers = ['ID', 'Name', 'Type', 'Status', 'Priority', 'Created']
        output.print_data(workloads, headers=headers)
        
        output.print(f"\nTotal: {len(workloads)} workload(s)")
        return 0
        
    except Exception as e:
        output.error(f"Failed to list workloads: {e}")
        return 1


def get_workload(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Get workload details."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info(f"Fetching workload {args.workload_id}...")
        workload = api_client.get_workload(args.workload_id)
        
        output.print_data(workload)
        return 0
        
    except Exception as e:
        output.error(f"Failed to get workload: {e}")
        return 1


def create_workload(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Create new workload."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        # Load from file if specified
        if args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                output.error(f"File not found: {args.file}")
                return 1
            
            with open(file_path, 'r') as f:
                workload_data = json.load(f)
        else:
            # Build workload data from arguments
            workload_data = {
                'name': args.name,
                'type': args.type,
                'image': args.image,
                'priority': args.priority,
            }
            
            if args.command:
                workload_data['command'] = args.command
            
            if args.args:
                workload_data['args'] = args.args
            
            if args.env:
                env_dict = {}
                for env_var in args.env:
                    if '=' in env_var:
                        key, value = env_var.split('=', 1)
                        env_dict[key] = value
                workload_data['environment'] = env_dict
            
            if args.cpu:
                workload_data['cpu_limit'] = args.cpu
            
            if args.memory:
                workload_data['memory_limit'] = args.memory
        
        output.info("Creating workload...")
        result = api_client.create_workload(workload_data)
        
        output.success(f"Workload created successfully")
        output.print_data(result)
        return 0
        
    except Exception as e:
        output.error(f"Failed to create workload: {e}")
        return 1


def update_workload(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Update workload."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        # Load from file if specified
        if args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                output.error(f"File not found: {args.file}")
                return 1
            
            with open(file_path, 'r') as f:
                update_data = json.load(f)
        else:
            # Build update data from arguments
            update_data = {}
            
            if args.name:
                update_data['name'] = args.name
            
            if args.priority:
                update_data['priority'] = args.priority
        
        if not update_data:
            output.error("No update data provided")
            return 1
        
        output.info(f"Updating workload {args.workload_id}...")
        result = api_client.update_workload(args.workload_id, update_data)
        
        output.success("Workload updated successfully")
        output.print_data(result)
        return 0
        
    except Exception as e:
        output.error(f"Failed to update workload: {e}")
        return 1


def delete_workload(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Delete workload."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        # Confirm deletion unless --force
        if not args.force:
            response = input(f"Are you sure you want to delete workload {args.workload_id}? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                output.info("Deletion cancelled")
                return 0
        
        output.info(f"Deleting workload {args.workload_id}...")
        api_client.delete_workload(args.workload_id)
        
        output.success("Workload deleted successfully")
        return 0
        
    except Exception as e:
        output.error(f"Failed to delete workload: {e}")
        return 1


def schedule_workload(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Schedule workload for execution."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info(f"Scheduling workload {args.workload_id}...")
        result = api_client.schedule_workload(args.workload_id)
        
        output.success("Workload scheduled successfully")
        output.print_data(result)
        return 0
        
    except Exception as e:
        output.error(f"Failed to schedule workload: {e}")
        return 1


def get_logs(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Get workload logs."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info(f"Fetching logs for workload {args.workload_id}...")
        logs = api_client.get_workload_logs(args.workload_id)
        
        if 'logs' in logs:
            output.print(logs['logs'])
        else:
            output.print_data(logs)
        
        return 0
        
    except Exception as e:
        output.error(f"Failed to get logs: {e}")
        return 1


def get_status(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Get workload status."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        output.info(f"Fetching status for workload {args.workload_id}...")
        workload = api_client.get_workload(args.workload_id)
        
        # Display key status information
        status_info = {
            'ID': workload.get('id'),
            'Name': workload.get('name'),
            'Status': workload.get('status'),
            'Type': workload.get('type'),
            'Priority': workload.get('priority'),
            'Created': workload.get('created_at'),
            'Updated': workload.get('updated_at'),
        }
        
        if 'started_at' in workload:
            status_info['Started'] = workload['started_at']
        
        if 'completed_at' in workload:
            status_info['Completed'] = workload['completed_at']
        
        output.print_data(status_info)
        return 0
        
    except Exception as e:
        output.error(f"Failed to get status: {e}")
        return 1
