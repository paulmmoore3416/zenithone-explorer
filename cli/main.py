#!/usr/bin/env python3
"""
ZenithOne Explorer CLI - Main Entry Point

Enterprise-grade command-line interface for managing LinuxONE workloads,
containers, and z/OS subsystems.

Author: IBM Bob AI + Gemini CLI AI
License: MIT
"""

import sys
import argparse
from typing import Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.lib.config import Config
from cli.lib.output import Output, OutputFormat
from cli.lib.api_client import APIClient
from cli.commands import (
    auth,
    workloads,
    containers,
    subsystems,
    admin,
    metrics
)


class ZenithCLI:
    """Main CLI application class."""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.config = Config()
        self.output = Output()
        self.api_client = None
        
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser with all subcommands."""
        parser = argparse.ArgumentParser(
            prog='zenith',
            description='ZenithOne Explorer - Enterprise LinuxONE Management CLI',
            epilog='For more information, visit: https://github.com/paulmmoore3416/zenithone-explorer'
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version=f'%(prog)s {self.VERSION}'
        )
        
        parser.add_argument(
            '--config',
            type=str,
            help='Path to configuration file',
            default=None
        )
        
        parser.add_argument(
            '--format',
            type=str,
            choices=['table', 'json', 'yaml'],
            default='table',
            help='Output format (default: table)'
        )
        
        parser.add_argument(
            '--no-color',
            action='store_true',
            help='Disable colored output'
        )
        
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode'
        )
        
        # Create subparsers for commands
        subparsers = parser.add_subparsers(
            title='commands',
            dest='command',
            help='Available commands'
        )
        
        # Register command modules
        auth.register(subparsers)
        workloads.register(subparsers)
        containers.register(subparsers)
        subsystems.register(subparsers)
        admin.register(subparsers)
        metrics.register(subparsers)
        
        return parser
    
    def initialize(self, args: argparse.Namespace) -> bool:
        """Initialize CLI components based on arguments."""
        try:
            # Load configuration
            if args.config:
                self.config.load(args.config)
            else:
                self.config.load_default()
            
            # Configure output
            self.output.set_format(OutputFormat(args.format))
            self.output.set_color(not args.no_color)
            
            # Initialize API client if authenticated
            if self.config.has_token():
                self.api_client = APIClient(
                    base_url=self.config.get('api_url'),
                    token=self.config.get('token')
                )
            
            return True
            
        except Exception as e:
            self.output.error(f"Initialization failed: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            return False
    
    def run(self, argv: Optional[list] = None) -> int:
        """Run the CLI application."""
        parser = self.create_parser()
        args = parser.parse_args(argv)
        
        # Show help if no command specified
        if not args.command:
            parser.print_help()
            return 0
        
        # Initialize components
        if not self.initialize(args):
            return 1
        
        # Execute command
        try:
            # Get command module
            command_map = {
                'login': auth.login,
                'logout': auth.logout,
                'whoami': auth.whoami,
                'workload': workloads.execute,
                'container': containers.execute,
                'subsystem': subsystems.execute,
                'admin': admin.execute,
                'metrics': metrics.execute,
            }
            
            command_func = command_map.get(args.command)
            if not command_func:
                self.output.error(f"Unknown command: {args.command}")
                return 1
            
            # Execute command with context
            context = {
                'config': self.config,
                'output': self.output,
                'api_client': self.api_client,
                'debug': args.debug
            }
            
            return command_func(args, context)
            
        except KeyboardInterrupt:
            self.output.warning("\nOperation cancelled by user")
            return 130
            
        except Exception as e:
            self.output.error(f"Command failed: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            return 1


def main():
    """Main entry point for the CLI."""
    cli = ZenithCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
