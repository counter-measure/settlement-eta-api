#!/usr/bin/env python3
"""
Script to count the total number of objects in settlement_times.json.
"""

import json
from typing import Dict

def load_settlement_data(file_path: str) -> Dict:
    """Load the settlement times JSON data."""
    with open(file_path, 'r') as f:
        return json.load(f)

def count_objects(data: Dict) -> Dict:
    """
    Count objects at each level of the JSON structure.
    
    Returns a dict with counts for each level.
    """
    counts = {
        'origin_chain_ids': 0,
        'destination_chain_ids': 0,
        'tickerhashes': 0,
        'bins': 0,
        'total_combinations': 0
    }
    
    for origin_chain_id, destinations in data.items():
        counts['origin_chain_ids'] += 1
        
        for destination_chain_id, tickerhashes in destinations.items():
            counts['destination_chain_ids'] += 1
            
            for tickerhash, bins in tickerhashes.items():
                counts['tickerhashes'] += 1
                
                for bin_name, bin_data in bins.items():
                    counts['bins'] += 1
    
    # Calculate total unique combinations
    counts['total_combinations'] = counts['tickerhashes']
    
    return counts

def print_object_count_report(counts: Dict):
    """Print a formatted report of object counts."""
    print("🔍 Object Count Analysis - Original settlement_times.json")
    print("=" * 60)
    
    print(f"📊 Object Counts:")
    print(f"  Origin Chain IDs: {counts['origin_chain_ids']:,}")
    print(f"  Destination Chain IDs: {counts['destination_chain_ids']:,}")
    print(f"  Tickerhashes: {counts['tickerhashes']:,}")
    print(f"  Individual Bins: {counts['bins']:,}")
    
    print(f"\n🎯 Key Metrics:")
    print(f"  Total Unique Combinations: {counts['total_combinations']:,}")
    print(f"  Average Bins per Combination: {counts['bins'] / counts['total_combinations']:.1f}")
    
    print(f"\n💡 Structure Breakdown:")
    print(f"  The file contains {counts['origin_chain_ids']} origin chains")
    print(f"  Each origin chain connects to multiple destination chains")
    print(f"  Each origin-destination pair has multiple tickerhashes")
    print(f"  Each tickerhash has multiple amount bins")
    print(f"  Total of {counts['bins']:,} individual bin objects")

def main():
    """Main function to run the object count."""
    try:
        # Load the data
        print("Loading settlement_times.json...")
        data = load_settlement_data('settlement_times.json')
        
        # Count objects
        print("Counting objects...")
        counts = count_objects(data)
        
        # Print report
        print_object_count_report(counts)
        
    except FileNotFoundError:
        print("❌ Error: settlement_times.json not found in current directory")
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in settlement_times.json")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
