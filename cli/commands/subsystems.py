"""
ZenithOne Explorer CLI - Subsystem Commands

Handles z/OS subsystem operations (JES, CICS, DB2, TSO).
"""

import argparse
from typing import Dict, Any
from pathlib import Path


def register(subparsers) -> None:
    """Register subsystem commands."""
    
    # Main subsystem command
    subsystem_parser = subparsers.add_parser(
        'subsystem',
        help='Manage z/OS subsystems',
        description='Interact with JES, CICS, DB2, and TSO subsystems'
    )
    
    subsystem_subparsers = subsystem_parser.add_subparsers(
        title='subsystem commands',
        dest='subsystem_command',
        help='Subsystem operations'
    )
    
    # JES commands
    jes_parser = subsystem_subparsers.add_parser(
        'jes',
        help='JES (Job Entry Subsystem) operations'
    )
    jes_subparsers = jes_parser.add_subparsers(dest='jes_action')
    
    # JES submit
    jes_submit = jes_subparsers.add_parser('submit', help='Submit JCL job')
    jes_submit.add_argument('jcl_file', help='Path to JCL file')
    jes_submit.add_argument('--priority', choices=['LOW', 'NORMAL', 'HIGH'], default='NORMAL')
    
    # JES status
    jes_status = jes_subparsers.add_parser('status', help='Get JES status')
    
    # JES job
    jes_job = jes_subparsers.add_parser('job', help='Get job status')
    jes_job.add_argument('job_id', help='Job ID')
    
    # JES list
    jes_list = jes_subparsers.add_parser('list', help='List jobs')
    jes_list.add_argument('--status', help='Filter by status')
    
    # CICS commands
    cics_parser = subsystem_subparsers.add_parser(
        'cics',
        help='CICS (Customer Information Control System) operations'
    )
    cics_subparsers = cics_parser.add_subparsers(dest='cics_action')
    
    # CICS status
    cics_status = cics_subparsers.add_parser('status', help='Get CICS status')
    
    # CICS transaction
    cics_trans = cics_subparsers.add_parser('transaction', help='Process transaction')
    cics_trans.add_argument('program', help='Program name')
    cics_trans.add_argument('--data', help='Transaction data (JSON)')
    cics_trans.add_argument('--file', help='Load data from file')
    
    # CICS list
    cics_list = cics_subparsers.add_parser('list', help='List transactions')
    
    # DB2 commands
    db2_parser = subsystem_subparsers.add_parser(
        'db2',
        help='DB2 database operations'
    )
    db2_subparsers = db2_parser.add_subparsers(dest='db2_action')
    
    # DB2 status
    db2_status = db2_subparsers.add_parser('status', help='Get DB2 status')
    
    # DB2 query
    db2_query = db2_subparsers.add_parser('query', help='Execute SQL query')
    db2_query.add_argument('sql', nargs='?', help='SQL query')
    db2_query.add_argument('--file', help='Load SQL from file')
    
    # DB2 tables
    db2_tables = db2_subparsers.add_parser('tables', help='List tables')
    
    # TSO commands
    tso_parser = subsystem_subparsers.add_parser(
        'tso',
        help='TSO (Time Sharing Option) operations'
    )
    tso_subparsers = tso_parser.add_subparsers(dest='tso_action')
    
    # TSO status
    tso_status = tso_subparsers.add_parser('status', help='Get TSO status')
    
    # TSO command
    tso_cmd = tso_subparsers.add_parser('exec', help='Execute TSO command')
    tso_cmd.add_argument('command', help='TSO command')
    
    # TSO session
    tso_session = tso_subparsers.add_parser('session', help='Interactive TSO session')


def execute(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Execute subsystem command."""
    if not args.subsystem_command:
        context['output'].error("No subsystem specified. Use 'zenith subsystem --help' for usage.")
        return 1
    
    handlers = {
        'jes': handle_jes,
        'cics': handle_cics,
        'db2': handle_db2,
        'tso': handle_tso,
    }
    
    handler = handlers.get(args.subsystem_command)
    if not handler:
        context['output'].error(f"Unknown subsystem: {args.subsystem_command}")
        return 1
    
    return handler(args, context)


def handle_jes(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Handle JES commands."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        if args.jes_action == 'submit':
            # Read JCL file
            jcl_path = Path(args.jcl_file)
            if not jcl_path.exists():
                output.error(f"JCL file not found: {args.jcl_file}")
                return 1
            
            with open(jcl_path, 'r') as f:
                jcl_content = f.read()
            
            output.info("Submitting JCL job...")
            result = api_client.submit_job(jcl_content, args.priority)
            output.success(f"Job submitted: {result.get('job_id')}")
            output.print_data(result)
            
        elif args.jes_action == 'status':
            output.info("Fetching JES status...")
            status = api_client.get_subsystem_status('jes')
            output.print_data(status)
            
        elif args.jes_action == 'job':
            output.info(f"Fetching job {args.job_id}...")
            job = api_client.get_job_status(args.job_id)
            output.print_data(job)
            
        elif args.jes_action == 'list':
            output.info("Listing jobs...")
            result = api_client.execute_subsystem_command('jes', 'list_jobs', {'status': args.status} if args.status else None)
            output.print_data(result)
            
        else:
            output.error(f"Unknown JES action: {args.jes_action}")
            return 1
        
        return 0
        
    except Exception as e:
        output.error(f"JES operation failed: {e}")
        return 1


def handle_cics(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Handle CICS commands."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        if args.cics_action == 'status':
            output.info("Fetching CICS status...")
            status = api_client.get_subsystem_status('cics')
            output.print_data(status)
            
        elif args.cics_action == 'transaction':
            import json
            
            # Get transaction data
            if args.file:
                with open(args.file, 'r') as f:
                    data = json.load(f)
            elif args.data:
                data = json.loads(args.data)
            else:
                data = {}
            
            output.info(f"Processing transaction for program {args.program}...")
            result = api_client.process_transaction(args.program, data)
            output.success("Transaction processed")
            output.print_data(result)
            
        elif args.cics_action == 'list':
            output.info("Listing transactions...")
            result = api_client.execute_subsystem_command('cics', 'list_transactions')
            output.print_data(result)
            
        else:
            output.error(f"Unknown CICS action: {args.cics_action}")
            return 1
        
        return 0
        
    except Exception as e:
        output.error(f"CICS operation failed: {e}")
        return 1


def handle_db2(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Handle DB2 commands."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        if args.db2_action == 'status':
            output.info("Fetching DB2 status...")
            status = api_client.get_subsystem_status('db2')
            output.print_data(status)
            
        elif args.db2_action == 'query':
            # Get SQL query
            if args.file:
                with open(args.file, 'r') as f:
                    sql = f.read()
            elif args.sql:
                sql = args.sql
            else:
                output.error("No SQL query provided")
                return 1
            
            output.info("Executing SQL query...")
            result = api_client.execute_sql(sql)
            output.print_data(result)
            
        elif args.db2_action == 'tables':
            output.info("Listing tables...")
            result = api_client.execute_subsystem_command('db2', 'list_tables')
            output.print_data(result)
            
        else:
            output.error(f"Unknown DB2 action: {args.db2_action}")
            return 1
        
        return 0
        
    except Exception as e:
        output.error(f"DB2 operation failed: {e}")
        return 1


def handle_tso(args: argparse.Namespace, context: Dict[str, Any]) -> int:
    """Handle TSO commands."""
    output = context['output']
    api_client = context.get('api_client')
    
    if not api_client:
        output.error("Not authenticated. Use 'zenith login' first.")
        return 1
    
    try:
        if args.tso_action == 'status':
            output.info("Fetching TSO status...")
            status = api_client.get_subsystem_status('tso')
            output.print_data(status)
            
        elif args.tso_action == 'exec':
            output.info(f"Executing TSO command: {args.command}")
            result = api_client.execute_tso_command(args.command)
            
            if 'output' in result:
                output.print(result['output'])
            else:
                output.print_data(result)
            
        elif args.tso_action == 'session':
            output.info("Starting interactive TSO session...")
            output.warning("Interactive sessions not yet implemented")
            return 1
            
        else:
            output.error(f"Unknown TSO action: {args.tso_action}")
            return 1
        
        return 0
        
    except Exception as e:
        output.error(f"TSO operation failed: {e}")
        return 1
