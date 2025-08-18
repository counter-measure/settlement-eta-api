#!/usr/bin/env python3
"""
Script to generate missing bins in settlement_times.json data.

This script identifies missing bins and populates them with the maximum
values from the same bin sizes across other combinations.
"""

import json
from typing import Dict, List, Tuple
from collections import defaultdict

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

def collect_bin_statistics(data: Dict) -> Dict[str, Dict[str, List[float]]]:
    """
    Collect statistics for each bin across all combinations.
    
    Returns a dict with bin names as keys and lists of values for each metric.
    """
    bin_stats = defaultdict(lambda: defaultdict(list))
    
    for origin_chain_id, destinations in data.items():
        for destination_chain_id, tickerhashes in destinations.items():
            for tickerhash, bins in tickerhashes.items():
                for bin_name, bin_data in bins.items():
                    if bin_name in EXPECTED_BINS:
                        bin_stats[bin_name]["p25"].append(bin_data["settlement_duration_minutes_p25"])
                        bin_stats[bin_name]["p50"].append(bin_data["settlement_duration_minutes_p50"])
                        bin_stats[bin_name]["p75"].append(bin_data["settlement_duration_minutes_p75"])
    
    return bin_stats

def generate_missing_bin_data(bin_stats: Dict[str, Dict[str, List[float]]], bin_name: str) -> Dict:
    """
    Generate missing bin data using maximum values from the same bin across all combinations.
    """
    if bin_name not in bin_stats:
        # If no data exists for this bin, return default values
        return {
            "settlement_duration_minutes_p25": 0.0,
            "settlement_duration_minutes_p50": 0.0,
            "settlement_duration_minutes_p75": 0.0,
            "sample_size": 0,
            "generated": True
        }
    
    stats = bin_stats[bin_name]
    
    return {
        "settlement_duration_minutes_p25": max(stats["p25"]) if stats["p25"] else 0.0,
        "settlement_duration_minutes_p50": max(stats["p50"]) if stats["p50"] else 0.0,
        "settlement_duration_minutes_p75": max(stats["p75"]) if stats["p75"] else 0.0,
        "sample_size": 0,
        "generated": True
    }

def populate_missing_bins(data: Dict, missing_combinations: List[Tuple[str, str, str, List[str]]]) -> Dict:
    """
    Populate missing bins with generated data.
    
    Returns a copy of the data with missing bins filled in.
    """
    # Create a deep copy of the data
    populated_data = json.loads(json.dumps(data))
    
    # Collect statistics for each bin
    bin_stats = collect_bin_statistics(data)
    
    # Populate missing bins
    for origin_chain_id, destination_chain_id, tickerhash, missing_bins in missing_combinations:
        for bin_name in missing_bins:
            generated_data = generate_missing_bin_data(bin_stats, bin_name)
            populated_data[origin_chain_id][destination_chain_id][tickerhash][bin_name] = generated_data
    
    return populated_data

def save_populated_data(data: Dict, output_file: str):
    """Save the populated data to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

def print_generation_summary(missing_combinations: List[Tuple[str, str, str, List[str]]], bin_stats: Dict):
    """Print a summary of what will be generated."""
    print("🔍 Analysis Summary:")
    print(f"Total combinations with missing bins: {len(missing_combinations)}")
    
    print("\n📊 Available data per bin:")
    for bin_name in EXPECTED_BINS:
        if bin_name in bin_stats:
            p25_count = len(bin_stats[bin_name]["p25"])
            p50_count = len(bin_stats[bin_name]["p50"])
            p75_count = len(bin_stats[bin_name]["p75"])
            print(f"  {bin_name}: {p25_count} combinations with data")
        else:
            print(f"  {bin_name}: No data available")
    
    print("\n⚠️  Note: Missing bins will be populated with maximum values from the same bin size across all combinations.")
    print("   This provides conservative estimates for settlement times.")

def main():
    """Main function to run the bin generation."""
    try:
        # Load the data
        print("Loading settlement_times.json...")
        data = load_settlement_data('settlement_times.json')
        
        # Find missing bins
        print("Analyzing data for missing bins...")
        missing_combinations = find_missing_bins(data)
        
        if not missing_combinations:
            print("✅ All combinations have all expected bins! No action needed.")
            return
        
        # Collect bin statistics
        print("Collecting statistics for existing bins...")
        bin_stats = collect_bin_statistics(data)
        
        # Print summary
        print_generation_summary(missing_combinations, bin_stats)
        
        # Ask for confirmation
        print(f"\n🚀 Ready to generate {len(missing_combinations)} missing bin combinations.")
        response = input("Proceed with generation? (y/N): ").strip().lower()
        
        if response not in ['y', 'yes']:
            print("Operation cancelled.")
            return
        
        # Populate missing bins
        print("Generating missing bins...")
        populated_data = populate_missing_bins(data, missing_combinations)
        
        # Save the populated data
        output_file = 'settlement_times_populated.json'
        save_populated_data(populated_data, output_file)
        
        print(f"✅ Successfully generated missing bins!")
        print(f"📁 Output saved to: {output_file}")
        print(f"📊 Total combinations: {len(missing_combinations)}")
        
        # Show some examples of what was generated
        print("\n📋 Examples of generated bins:")
        count = 0
        for origin_chain_id, destination_chain_id, tickerhash, missing_bins in missing_combinations[:3]:
            if count >= 3:
                break
            print(f"  Origin: {origin_chain_id}, Dest: {destination_chain_id}")
            print(f"  Tickerhash: {tickerhash[:20]}...")
            print(f"  Generated bins: {', '.join(missing_bins[:3])}")
            if len(missing_bins) > 3:
                print(f"    ... and {len(missing_bins) - 3} more")
            print()
            count += 1
        
    except FileNotFoundError:
        print("❌ Error: settlement_times.json not found in current directory")
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in settlement_times.json")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
