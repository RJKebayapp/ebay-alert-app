#!/usr/bin/env python3
"""
Migration script for database schema management.
This script uses Alembic to manage database migrations.
"""

import argparse
import os
import sys
import subprocess
from datetime import datetime

def run_command(command):
    """Run a shell command and print the output."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(f"Error: {result.stderr}", file=sys.stderr)
    
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    
    return result

def setup_alembic():
    """Initialize Alembic if not already set up."""
    if not os.path.exists('alembic'):
        print("Initializing Alembic...")
        run_command(['alembic', 'init', 'alembic'])
        print("Alembic initialized. Please configure alembic/env.py if needed.")
    else:
        print("Alembic is already initialized.")

def create_migration(message=None):
    """Create a new migration."""
    if not message:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        message = f"migration_{timestamp}"
    
    print(f"Creating migration: {message}")
    run_command(['alembic', 'revision', '--autogenerate', '-m', message])

def upgrade_database(revision='head'):
    """Upgrade the database to the specified revision."""
    print(f"Upgrading database to: {revision}")
    run_command(['alembic', 'upgrade', revision])

def downgrade_database(revision='-1'):
    """Downgrade the database to the specified revision."""
    print(f"Downgrading database to: {revision}")
    run_command(['alembic', 'downgrade', revision])

def show_history():
    """Show migration history."""
    print("Migration history:")
    run_command(['alembic', 'history'])

def show_current():
    """Show current revision."""
    print("Current revision:")
    run_command(['alembic', 'current'])

def main():
    """Main function to parse arguments and execute commands."""
    parser = argparse.ArgumentParser(description='Manage database migrations')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Initialize Alembic')
    
    # Create migration command
    create_parser = subparsers.add_parser('create', help='Create a new migration')
    create_parser.add_argument('-m', '--message', help='Migration message')
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade the database')
    upgrade_parser.add_argument('revision', nargs='?', default='head', help='Revision to upgrade to (default: head)')
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade the database')
    downgrade_parser.add_argument('revision', nargs='?', default='-1', help='Revision to downgrade to (default: -1)')
    
    # History command
    subparsers.add_parser('history', help='Show migration history')
    
    # Current command
    subparsers.add_parser('current', help='Show current revision')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup_alembic()
    elif args.command == 'create':
        create_migration(args.message)
    elif args.command == 'upgrade':
        upgrade_database(args.revision)
    elif args.command == 'downgrade':
        downgrade_database(args.revision)
    elif args.command == 'history':
        show_history()
    elif args.command == 'current':
        show_current()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
