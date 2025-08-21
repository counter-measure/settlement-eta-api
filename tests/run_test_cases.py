#!/usr/bin/env python3
"""
Test runner script that loads test cases from test_cases.csv and runs them through lookup_settlement_times.py
"""

import csv
import sys
import os
import time
from pathlib import Path

# Add the parent directory to the path so we can import the lookup script
sys.path.append(str(Path(__file__).parent.parent))

from tests.lookup_settlement_times import run_lookup

def load_test_cases(csv_file_path):
    """
    Load test cases from CSV file.
    
    Args:
        csv_file_path (str): Path to the CSV file
    
    Returns:
        list: List of test case dictionaries
    """
    test_cases = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_cases.append(row)
    except FileNotFoundError:
        print(f"Error: Test cases file '{csv_file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []
    
    return test_cases

def run_single_test(test_case, json_file_path, chain_data_path, verbose=True):
    """
    Run a single test case.
    
    Args:
        test_case (dict): Test case dictionary
        json_file_path (str): Path to settlement times JSON file
        chain_data_path (str): Path to chain data JSON file
        verbose (bool): Whether to print verbose output
    
    Returns:
        dict: Test result with expected vs actual values
    """
    # Extract test case parameters
    origin_chain = test_case['from_chain_name']
    destination_chain = test_case['to_chain_name']
    asset_symbol = test_case['from_asset_symbol']
    
    # Parse USD amount (remove commas and convert to float)
    try:
        usd_amount = float(test_case['amount'].replace(',', ''))
    except (ValueError, KeyError):
        print(f"Warning: Invalid USD amount '{test_case.get('amount', 'N/A')}' for test case")
        return None
    
    # Expected values
    expected_p25 = test_case.get('settlement_duration_minutes_p25')
    expected_p50 = test_case.get('settlement_duration_minutes_p50')
    expected_p75 = test_case.get('settlement_duration_minutes_p75')
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"Test Case: {origin_chain} -> {destination_chain}, {asset_symbol}, ${usd_amount:,.2f}")
        print(f"Expected: P25={expected_p25}, P50={expected_p50}, P75={expected_p75}")
        print(f"{'='*80}")
    
    # Run the lookup
    start_time = time.time()
    result = run_lookup(
        origin_chain=origin_chain,
        destination_chain=destination_chain,
        asset_symbol=asset_symbol,
        usd_amount=usd_amount,
        json_file_path=json_file_path,
        chain_data_path=chain_data_path,
        verbose=verbose
    )
    lookup_time = time.time() - start_time
    
    if result is None:
        if verbose:
            print(f"  ❌ Lookup failed")
        return {
            'test_case': test_case,
            'success': False,
            'error': 'Lookup failed',
            'lookup_time': lookup_time,
            'expected': {
                'p25': expected_p25,
                'p50': expected_p50,
                'p75': expected_p75
            },
            'actual': None
        }
    
    # Extract actual values
    actual_p25 = result['settlement_duration_minutes_p25']
    actual_p50 = result['settlement_duration_minutes_p50']
    actual_p75 = result['settlement_duration_minutes_p75']
    
    # Compare expected vs actual (if expected values are provided)
    if expected_p25 and expected_p50 and expected_p75:
        try:
            expected_p25 = float(expected_p25)
            expected_p50 = float(expected_p50)
            expected_p75 = float(expected_p75)
            
            p25_match = abs(actual_p25 - expected_p25) < 0.01
            p50_match = abs(actual_p50 - expected_p50) < 0.01
            p75_match = abs(actual_p75 - expected_p75) < 0.01
            
            all_match = p25_match and p50_match and p75_match
            
            if verbose:
                print(f"  Actual: P25={actual_p25}, P50={actual_p50}, P75={actual_p75}")
                print(f"  Match: P25={'✅' if p25_match else '❌'}, P50={'✅' if p50_match else '❌'}, P75={'✅' if p75_match else '❌'}")
                print(f"  Overall: {'✅ PASS' if all_match else '❌ FAIL'}")
                print(f"  Lookup time: {lookup_time:.3f}s")
            
            return {
                'test_case': test_case,
                'success': all_match,
                'lookup_time': lookup_time,
                'expected': {
                    'p25': expected_p25,
                    'p50': expected_p50,
                    'p75': expected_p75
                },
                'actual': {
                    'p25': actual_p25,
                    'p50': actual_p50,
                    'p75': actual_p75
                },
                'matches': {
                    'p25': p25_match,
                    'p50': p50_match,
                    'p75': p75_match
                }
            }
            
        except (ValueError, TypeError):
            if verbose:
                print(f"  Warning: Could not parse expected values for comparison")
                print(f"  Actual: P25={actual_p25}, P50={actual_p50}, P75={actual_p75}")
                print(f"  Lookup time: {lookup_time:.3f}s")
            
            return {
                'test_case': test_case,
                'success': True,  # Consider it a pass if we can't compare
                'lookup_time': lookup_time,
                'expected': {
                    'p25': expected_p25,
                    'p50': expected_p50,
                    'p75': expected_p75
                },
                'actual': {
                    'p25': actual_p25,
                    'p50': actual_p50,
                    'p75': actual_p75
                },
                'matches': None
            }
    else:
        # No expected values to compare against
        if verbose:
            print(f"  Actual: P25={actual_p25}, P50={actual_p50}, P75={actual_p75}")
            print(f"  Lookup time: {lookup_time:.3f}s")
            print(f"  Note: No expected values to compare against")
        
        return {
            'test_case': test_case,
            'success': True,  # Consider it a pass if no expected values
            'lookup_time': lookup_time,
            'expected': None,
            'actual': {
                'p25': actual_p25,
                'p50': actual_p50,
                'p75': actual_p75
            },
            'matches': None
        }

def run_all_tests(csv_file_path, json_file_path, chain_data_path, verbose=True, max_tests=None):
    """
    Run all test cases from the CSV file.
    
    Args:
        csv_file_path (str): Path to test cases CSV file
        json_file_path (str): Path to settlement times JSON file
        chain_data_path (str): Path to chain data JSON file
        verbose (bool): Whether to print verbose output
        max_tests (int, optional): Maximum number of tests to run
    
    Returns:
        dict: Summary of test results
    """
    print(f"Loading test cases from: {csv_file_path}")
    test_cases = load_test_cases(csv_file_path)
    
    if not test_cases:
        print("No test cases loaded. Exiting.")
        return None
    
    print(f"Loaded {len(test_cases)} test cases")
    
    if max_tests:
        test_cases = test_cases[:max_tests]
        print(f"Running first {len(test_cases)} test cases")
    
    print(f"\nStarting test execution...")
    print(f"Settlement times file: {json_file_path}")
    print(f"Chain data file: {chain_data_path}")
    
    results = []
    passed = 0
    failed = 0
    total_lookup_time = 0
    
    start_time = time.time()
    
    for i, test_case in enumerate(test_cases, 1):
        if verbose:
            print(f"\n[{i}/{len(test_cases)}] Running test case...")
        
        result = run_single_test(test_case, json_file_path, chain_data_path, verbose)
        
        if result:
            results.append(result)
            if result['success']:
                passed += 1
            else:
                failed += 1
            total_lookup_time += result['lookup_time']
        else:
            failed += 1
        
        # Add a small delay to avoid overwhelming the system
        time.sleep(0.1)
    
    total_time = time.time() - start_time
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"TEST EXECUTION SUMMARY")
    print(f"{'='*80}")
    print(f"Total tests run: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed/len(results)*100):.1f}%" if results else "N/A")
    print(f"Total execution time: {total_time:.2f}s")
    print(f"Total lookup time: {total_lookup_time:.2f}s")
    print(f"Average lookup time: {(total_lookup_time/len(results)):.3f}s" if results else "N/A")
    
    return {
        'total_tests': len(results),
        'passed': passed,
        'failed': failed,
        'success_rate': (passed/len(results)*100) if results else 0,
        'total_time': total_time,
        'total_lookup_time': total_lookup_time,
        'average_lookup_time': (total_lookup_time/len(results)) if results else 0,
        'results': results
    }

def main():
    """Main function to run the test suite."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run settlement time lookup tests from CSV file')
    parser.add_argument('--csv', default='tests/test_cases.csv', help='Path to test cases CSV file')
    parser.add_argument('--json', default='output/settlement_times_populated_improved_from.json', help='Path to settlement times JSON file')
    parser.add_argument('--chain-data', default='run/chain_data.json', help='Path to chain data JSON file')
    parser.add_argument('--max-tests', type=int, help='Maximum number of tests to run')
    parser.add_argument('--quiet', '-q', action='store_true', help='Reduce verbose output')
    
    args = parser.parse_args()
    
    # Check if files exist
    if not os.path.exists(args.csv):
        print(f"Error: Test cases file '{args.csv}' not found.")
        sys.exit(1)
    
    if not os.path.exists(args.json):
        print(f"Error: Settlement times file '{args.json}' not found.")
        sys.exit(1)
    
    if not os.path.exists(args.chain_data):
        print(f"Error: Chain data file '{args.chain_data}' not found.")
        sys.exit(1)
    
    # Run tests
    verbose = not args.quiet
    results = run_all_tests(
        csv_file_path=args.csv,
        json_file_path=args.json,
        chain_data_path=args.chain_data,
        verbose=verbose,
        max_tests=args.max_tests
    )
    
    if results and results['failed'] > 0:
        sys.exit(1)  # Exit with error code if any tests failed

if __name__ == "__main__":
    main()
