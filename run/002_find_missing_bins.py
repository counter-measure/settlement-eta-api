#!/usr/bin/env python3
"""
Script to find missing bins in settlement_times.json data.

This script analyzes the JSON data to identify which combinations of
origin_chain_id, destination_chain_id, and tickerhash are missing
any of the expected amount bins.
"""

import json
import sys
from typing import Dict, List, Set, Tuple

# Expected bins based on the case statement
EXPECTED_BINS = [
    "0-50000",
    "50000-100000", 
    "100000-300000",
    "300000-400000",
    "400000-500000",
    "500000-700000",
    "700000-1000000",
    "1000000+"
]

def load_settlement_data(file_path: str) -> Dict:
    """Load the settlement times JSON data."""
    with open(file_path, 'r') as f:
        return json.load(f)

def find_missing_bins(data: Dict) -> List[Tuple[str, str, str, List[str]]]:
    """
    Find combinations that are missing bins.
    
    Returns a list of tuples containing:
    (origin_chain_id, destination_chain_id, tickerhash, [missing_bins])
    """
    missing_combinations = []
    
    for origin_chain_id, destinations in data.items():
        for destination_chain_id, tickerhashes in destinations.items():
            for tickerhash, bins in tickerhashes.items():
                # Get the bins that exist for this combination
                existing_bins = set(bins.keys())
                
                # Find missing bins
                missing_bins = [bin_name for bin_name in EXPECTED_BINS if bin_name not in existing_bins]
                
                if missing_bins:
                    missing_combinations.append((
                        origin_chain_id,
                        destination_chain_id,
                        tickerhash,
                        missing_bins
                    ))
    
    return missing_combinations

def print_missing_bins_report(missing_combinations: List[Tuple[str, str, str, List[str]]]):
    """Print a formatted report of missing bins."""
    if not missing_combinations:
        print("✅ All combinations have all expected bins!")
        return
    
    print(f"❌ Found {len(missing_combinations)} combinations missing bins:\n")
    
    for origin_chain_id, destination_chain_id, tickerhash, missing_bins in missing_combinations:
        print(f"Origin Chain ID: {origin_chain_id}")
        print(f"Destination Chain ID: {destination_chain_id}")
        print(f"Tickerhash: {tickerhash}")
        print(f"Missing Bins: {', '.join(missing_bins)}")
        print("-" * 80)

def main():
    """Main function to run the analysis."""
    try:
        # Get filename from command line argument or use default
        filename = sys.argv[1] if len(sys.argv) > 1 else 'settlement_times.json'
        
        # Load the data
        print(f"Loading {filename}...")
        data = load_settlement_data(filename)
        
        # Find missing bins
        print("Analyzing data for missing bins...")
        missing_combinations = find_missing_bins(data)
        
        # Print report
        print_missing_bins_report(missing_combinations)
        
        # Summary statistics
        total_combinations = sum(
            len(destinations) * sum(len(tickerhashes) for tickerhashes in destinations.values())
            for destinations in data.values()
        )
        
        print(f"\n📊 Summary:")
        print(f"Total combinations: {total_combinations}")
        print(f"Combinations with missing bins: {len(missing_combinations)}")
        print(f"Combinations with all bins: {total_combinations - len(missing_combinations)}")
        
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found in current directory")
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {filename}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
