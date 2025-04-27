#!/usr/bin/env python3
"""
Test runner script for PDF Comparison Tool.
Runs all tests and generates a coverage report.
"""

import sys
import os
import subprocess
import argparse
import webbrowser
from pathlib import Path
from datetime import datetime

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run tests for PDF Comparison Tool')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--failfast', action='store_true', help='Stop on first failure')
    parser.add_argument('--file', '-f', help='Run specific test file')
    return parser.parse_args()

def run_tests(args):
    """Run the tests with specified options"""
    # Base command
    cmd = ['pytest']
    
    # Add options
    if args.verbose:
        cmd.append('-v')
    if args.failfast:
        cmd.append('--failfast')
    
    # Coverage options
    if args.coverage or args.html:
        cmd.extend([
            '--cov=src',
            '--cov-report=term-missing'
        ])
        if args.html:
            cmd.append('--cov-report=html')
    
    # Specific file or all tests
    if args.file:
        cmd.append(args.file)
    else:
        cmd.append('tests/')
    
    # Run tests
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {str(e)}", file=sys.stderr)
        return 1

def generate_test_report(success, args):
    """Generate a test report"""
    report_dir = Path('test-reports')
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = report_dir / f'test_report_{timestamp}.txt'
    
    with open(report_path, 'w') as f:
        f.write("PDF Comparison Tool - Test Report\n")
        f.write("================================\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Status: {'SUCCESS' if success else 'FAILURE'}\n\n")
        
        # Test configuration
        f.write("Test Configuration:\n")
        f.write(f"- Coverage: {args.coverage}\n")
        f.write(f"- HTML Coverage: {args.html}\n")
        f.write(f"- Verbose: {args.verbose}\n")
        f.write(f"- Failfast: {args.failfast}\n")
        f.write(f"- Specific File: {args.file if args.file else 'All tests'}\n\n")
        
        # Coverage report
        if args.coverage or args.html:
            f.write("Coverage Report:\n")
            if Path('.coverage').exists():
                try:
                    coverage_cmd = ['coverage', 'report']
                    coverage_output = subprocess.check_output(coverage_cmd, text=True)
                    f.write(coverage_output)
                except Exception as e:
                    f.write(f"Error generating coverage report: {str(e)}\n")
        
        print(f"\nTest report saved to: {report_path}")

def open_coverage_report():
    """Open the HTML coverage report in the default browser"""
    report_path = Path('htmlcov/index.html')
    if report_path.exists():
        try:
            # For web-based environment, print the path instead
            print(f"\nCoverage report generated at: {report_path}")
            print("Please open it in your web browser to view the detailed coverage information.")
        except Exception as e:
            print(f"Error opening coverage report: {str(e)}", file=sys.stderr)
    else:
        print("Coverage report not found. Did you run with --html option?", file=sys.stderr)

def main():
    """Main entry point"""
    print("PDF Comparison Tool - Test Runner")
    print("================================")
    
    args = parse_args()
    
    # Ensure we're in the project root directory
    if not Path('src').exists() or not Path('tests').exists():
        print("Error: Please run this script from the project root directory", file=sys.stderr)
        return 1
    
    # Run tests
    print("\nRunning tests...")
    success = run_tests(args) == 0
    
    # Generate report
    generate_test_report(success, args)
    
    # Open coverage report if requested
    if args.html and success:
        open_coverage_report()
    
    # Print summary
    print("\nTest Summary:")
    print("-------------")
    print(f"Status: {'SUCCESS' if success else 'FAILURE'}")
    if args.coverage or args.html:
        print("Coverage report generated")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
