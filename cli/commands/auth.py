"""
ZenithOne Explorer CLI - Authentication Commands

Handles user authentication including login, logout, and user information.
"""

import argparse
import getpass
from typing import Dict, Any


def register(subparsers) -> None:
    """Register authentication commands."""
    
    # Login command
    login_parser = subparsers.add_parser(
        'login',
        help='Login to ZenithOne Explorer',
        description='Authenticate with the ZenithOne Explorer API'
    )
    login_parser.add_argument(
        'username',
        nargs='?',
        help='Username (will prompt if not provided)'
    )
    login_parser.add_argument(
        '--password',
        help='Password (not recommended, will prompt if not provided)'
    )
    login_parser.set_defaults(func=login)
    
    # Logout command
    logout_parser = subparsers.add_parser(
        'logout',
        help='Logout from ZenithOne Explorer',
        description='Invalidate authentication token and logout'
    )
    logout_parser.set_defaults(func=logout)
    
    # Whoami command
    whoami_parser = subparsers.add_parser(
        'whoami',
        help='Show current user information',
        description='Display information about the currently authenticated user'
    )
    whoami_parser.set_defaults(func=whoami)


def login(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """
    Login command implementation.
    
    Args:
        args: Command arguments
        context: CLI context with config, output, and api_client
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    output = context['output']
    config = context['config']
    
    try:
        # Get username
        username = args.username
        if not username:
            username = input("Username: ")
        
        # Get password
        password = args.password
        if not password:
            password = getpass.getpass("Password: ")
        
        # Create API client for login
        from cli.lib.api_client import APIClient
        api_client = APIClient(
            base_url=config.get_api_url(),
            timeout=config.get('timeout', 30),
            verify_ssl=config.get('verify_ssl', True)
        )
        
        # Attempt login
        output.info("Authenticating...")
        response = api_client.login(username, password)
        
        # Save token to config
        if 'access_token' in response:
            config.set_token(response['access_token'])
            config.save()
            
            output.success(f"Successfully logged in as {username}")
            
            # Display user info if available
            if 'user' in response:
                user = response['user']
                output.print(f"\nUser ID: {user.get('id')}")
                output.print(f"Role: {user.get('role', 'user')}")
                if 'email' in user:
                    output.print(f"Email: {user.get('email')}")
            
            return 0
        else:
            output.error("Login failed: No token received")
            return 1
            
    except Exception as e:
        output.error(f"Login failed: {e}")
        if context.get('debug'):
            import traceback
            traceback.print_exc()
        return 1


def logout(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """
    Logout command implementation.
    
    Args:
        args: Command arguments
        context: CLI context with config, output, and api_client
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    output = context['output']
    config = context['config']
    api_client = context.get('api_client')
    
    try:
        if not config.has_token():
            output.warning("Not currently logged in")
            return 0
        
        # Attempt to invalidate token on server
        if api_client:
            try:
                api_client.logout()
                output.info("Token invalidated on server")
            except Exception as e:
                output.warning(f"Could not invalidate token on server: {e}")
        
        # Clear local token
        config.clear_token()
        config.save()
        
        output.success("Successfully logged out")
        return 0
        
    except Exception as e:
        output.error(f"Logout failed: {e}")
        if context.get('debug'):
            import traceback
            traceback.print_exc()
        return 1


def whoami(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """
    Whoami command implementation.
    
    Args:
        args: Command arguments
        context: CLI context with config, output, and api_client
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    output = context['output']
    config = context['config']
    api_client = context.get('api_client')
    
    try:
        if not config.has_token():
            output.error("Not logged in. Use 'zenith login' to authenticate.")
            return 1
        
        if not api_client:
            output.error("API client not initialized")
            return 1
        
        # Get current user info
        output.info("Fetching user information...")
        user_info = api_client.whoami()
        
        # Display user information
        output.print_data(user_info)
        
        return 0
        
    except Exception as e:
        output.error(f"Failed to get user information: {e}")
        if context.get('debug'):
            import traceback
            traceback.print_exc()
        return 1
