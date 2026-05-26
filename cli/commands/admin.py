"""
ZenithOne Explorer CLI - Admin Commands

Administrative operations including user management, roles, and system configuration.
"""

import argparse
import json
from typing import Dict, Any
from pathlib import Path


def register(subparsers) -> None:
    """Register admin commands."""
    
    # Main admin command
    admin_parser = subparsers.add_parser(
        'admin',
        help='Administrative operations',
        description='Manage users, roles, and system configuration (admin only)'
    )
    
    admin_subparsers = admin_parser.add_subparsers(
        title='admin commands',
        dest='admin_command',
        help='Administrative operations'
    )
    
    # User management
    users_parser = admin_subparsers.add_parser(
        'users',
        help='User management'
    )
    users_subparsers = users_parser.add_subparsers(dest='users_action')
    
    # List users
    users_list = users_subparsers.add_parser('list', help='List all users')
    
    # Get user
    users_get = users_subparsers.add_parser('get', help='Get user details')
    users_get.add_argument('user_id', help='User ID')
    
    # Create user
    users_create = users_subparsers.add_parser('create', help='Create new user')
    users_create.add_argument('--username', required=True, help='Username')
    users_create.add_argument('--email', required=True, help='Email address')
    users_create.add_argument('--password', required=True, help='Password')
    users_create.add_argument('--role', choices=['user', 'admin'], default='user', help='User role')
    users_create.add_argument('--file', help='Load user data from JSON file')
    
    # Update user
    users_update = users_subparsers.add_parser('update', help='Update user')
    users_update.add_argument('user_id', help='User ID')
    users_update.add_argument('--email', help='New email address')
    users_update.add_argument('--role', choices=['user', 'admin'], help='New role')
    users_update.add_argument('--active', type=bool, help='Active status')
    users_update.add_argument('--file', help='Load update data from JSON file')
    
    # Delete user
    users_delete = users_subparsers.add_parser('delete', help='Delete user')
    users_delete.add_argument('user_id', help='User ID')
    users_delete.add_argument('--force', action='store_true', help='Force deletion')
    
    # Role management
    roles_parser = admin_subparsers.add_parser(
        'roles',
        help='Role management'
    )
    roles_subparsers = roles_parser.add_subparsers(dest='roles_action')
    
    # List roles
    roles_list = roles_subparsers.add_parser('list', help='List all roles')
    
    # System management
    system_parser = admin_subparsers.add_parser(
        'system',
        help='System management'
    )
    system_subparsers = system_parser.add_subparsers(dest='system_action')
    
    # System info
    system_info = system_subparsers.add_parser('info', help='Get system information')
    
    # System health
    system_health = system_subparsers.add_parser('health', help='Get system health status')
    
    # System config
    system_config = system_subparsers.add_parser('config', help='View system configuration')


def execute(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Execute admin command."""
    if not args.admin_command:
        context['output'].error("No admin command specified. Use 'zenith admin --help' for usage.")
        return 1
    
    handlers = {
        'users': handle_users,
        'roles': handle_roles,
        'system': handle_system,
    }
    
    handler = handlers.get(args.admin_command)
    if not handler:
        context['output'].error(f"Unknown admin command: {args.admin_command}")
        return 1
    
    return handler(args, context)


def handle_users(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Handle user management commands."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        if args.users_action == 'list':
            output.info("Fetching users...")
            users = api_client.list_users()
            
            if not users:
                output.info("No users found")
                return 0
            
            headers = ['ID', 'Username', 'Email', 'Role', 'Active', 'Created']
            output.print_data(users, headers=headers)
            output.print(f"\nTotal: {len(users)} user(s)")
            
        elif args.users_action == 'get':
            output.info(f"Fetching user {args.user_id}...")
            user = api_client.get_user(args.user_id)
            output.print_data(user)
            
        elif args.users_action == 'create':
            if args.file:
                with open(args.file, 'r') as f:
                    user_data = json.load(f)
            else:
                user_data = {
                    'username': args.username,
                    'email': args.email,
                    'password': args.password,
                    'role': args.role,
                }
            
            output.info("Creating user...")
            result = api_client.create_user(user_data)
            output.success(f"User created: {result.get('username')}")
            output.print_data(result)
            
        elif args.users_action == 'update':
            if args.file:
                with open(args.file, 'r') as f:
                    update_data = json.load(f)
            else:
                update_data = {}
                if args.email:
                    update_data['email'] = args.email
                if args.role:
                    update_data['role'] = args.role
                if args.active is not None:
                    update_data['is_active'] = args.active
            
            if not update_data:
                output.error("No update data provided")
                return 1
            
            output.info(f"Updating user {args.user_id}...")
            result = api_client.update_user(args.user_id, update_data)
            output.success("User updated successfully")
            output.print_data(result)
            
        elif args.users_action == 'delete':
            if not args.force:
                response = input(f"Are you sure you want to delete user {args.user_id}? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    output.info("Deletion cancelled")
                    return 0
            
            output.info(f"Deleting user {args.user_id}...")
            api_client.delete_user(args.user_id)
            output.success("User deleted successfully")
            
        else:
            output.error(f"Unknown users action: {args.users_action}")
            return 1
        
        return 0
        
    except Exception as e:
        output.error(f"User management operation failed: {e}")
        return 1


def handle_roles(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Handle role management commands."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        if args.roles_action == 'list':
            output.info("Fetching roles...")
            roles = api_client.list_roles()
            
            if not roles:
                output.info("No roles found")
                return 0
            
            output.print_data(roles)
            output.print(f"\nTotal: {len(roles)} role(s)")
            
        else:
            output.error(f"Unknown roles action: {args.roles_action}")
            return 1
        
        return 0
        
    except Exception as e:
        output.error(f"Role management operation failed: {e}")
        return 1


def handle_system(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Handle system management commands."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        if args.system_action == 'info':
            output.info("Fetching system information...")
            info = api_client.get_system_info()
            output.print_data(info)
            
        elif args.system_action == 'health':
            output.info("Checking system health...")
            health = api_client.get_system_health()
            
            # Display health status with color coding
            status = health.get('status', 'unknown')
            if status == 'healthy':
                output.success(f"System Status: {status}")
            elif status == 'degraded':
                output.warning(f"System Status: {status}")
            else:
                output.error(f"System Status: {status}")
            
            output.print_data(health)
            
        elif args.system_action == 'config':
            output.info("Fetching system configuration...")
            config = api_client.get_system_info()
            
            if 'config' in config:
                output.print_data(config['config'])
            else:
                output.print_data(config)
            
        else:
            output.error(f"Unknown system action: {args.system_action}")
            return 1
        
        return 0
        
    except Exception as e:
        output.error(f"System management operation failed: {e}")
        return 1
