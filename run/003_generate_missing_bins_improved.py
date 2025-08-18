#!/usr/bin/env python3
"""
Improved script to generate missing bins in settlement_times.json data.

This script identifies missing bins and populates them with intelligent estimates
based on existing data patterns and interpolation.
"""

import json
from typing import Dict, List, Tuple
from collections import defaultdict
import statistics

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

def get_bin_index(bin_name: str) -> int:
    """Get the index of a bin in the EXPECTED_BINS list."""
    try:
        return EXPECTED_BINS.index(bin_name)
    except ValueError:
        return -1

def interpolate_bin_data(bin_stats: Dict, target_bin: str, existing_bins: List[str], route_data: Dict = None) -> Dict:
    """
    Interpolate bin data based on surrounding bins or use fallback strategies.
    
    Args:
        bin_stats: Global statistics across all combinations
        target_bin: The bin we're trying to generate
        existing_bins: List of existing bins for this combination
        route_data: The specific route's data (for baseline scaling)
    """
    target_index = get_bin_index(target_bin)
    
    # Strategy 1: Use conservative estimates based on bin size (baseline scaling)
    # Higher value bins typically have longer settlement times
    if target_bin == "50000-100000":
        base_multiplier = 1.2
    elif target_bin == "100000-300000":
        base_multiplier = 1.5
    elif target_bin == "300000-400000":
        base_multiplier = 1.8
    elif target_bin == "400000-500000":
        base_multiplier = 2.0
    elif target_bin == "500000-700000":
        base_multiplier = 2.5
    elif target_bin == "700000-1000000":
        base_multiplier = 3.0
    elif target_bin == "1000000+":
        base_multiplier = 4.0
    else:
        base_multiplier = 1.0
    
    # Use the 0-50000 bin as baseline if available for THIS SPECIFIC ROUTE
    baseline_bin = "0-50000"
    if route_data and baseline_bin in route_data:
        # Use route-specific baseline data
        baseline_p50 = route_data[baseline_bin]["settlement_duration_minutes_p50"]
        estimated_p50 = baseline_p50 * base_multiplier
        estimated_p25 = estimated_p50 * 0.7
        estimated_p75 = estimated_p50 * 1.3
        
        return {
            "settlement_duration_minutes_p25": round(estimated_p25, 2),
            "settlement_duration_minutes_p50": round(estimated_p50, 2),
            "settlement_duration_minutes_p75": round(estimated_p75, 2),
            "sample_size": 0,
            "generated": True,
            "method": "baseline_scaling"
        }
    
    # Fallback: Use global average if route-specific baseline not available
    if baseline_bin in bin_stats and bin_stats[baseline_bin]["p50"]:
        baseline_p50 = statistics.mean(bin_stats[baseline_bin]["p50"])
        estimated_p50 = baseline_p50 * base_multiplier
        estimated_p25 = estimated_p50 * 0.7
        estimated_p75 = estimated_p50 * 1.3
        
        return {
            "settlement_duration_minutes_p25": round(estimated_p25, 2),
            "settlement_duration_minutes_p50": round(estimated_p50, 2),
            "settlement_duration_minutes_p75": round(estimated_p75, 2),
            "sample_size": 0,
            "generated": True,
            "method": "baseline_scaling_global"
        }
    
    # Strategy 2: Interpolate from surrounding bins (weighted interpolation)
    surrounding_data = []
    for bin_name in existing_bins:
        if bin_name in bin_stats and bin_stats[bin_name]["p25"]:
            bin_index = get_bin_index(bin_name)
            if bin_index != -1:
                # Calculate distance weight (closer bins get higher weight)
                distance = abs(bin_index - target_index)
                weight = 1.0 / (distance + 1)  # +1 to avoid division by zero
                
                avg_p25 = statistics.mean(bin_stats[bin_name]["p25"])
                avg_p50 = statistics.mean(bin_stats[bin_name]["p50"])
                avg_p75 = statistics.mean(bin_stats[bin_name]["p75"])
                
                surrounding_data.append({
                    "weight": weight,
                    "p25": avg_p25,
                    "p50": avg_p50,
                    "p75": avg_p75
                })
    
    if surrounding_data:
        # Weighted average of surrounding bins
        total_weight = sum(item["weight"] for item in surrounding_data)
        weighted_p25 = sum(item["weight"] * item["p25"] for item in surrounding_data) / total_weight
        weighted_p50 = sum(item["weight"] * item["p50"] for item in surrounding_data) / total_weight
        weighted_p75 = sum(item["weight"] * item["p75"] for item in surrounding_data) / total_weight
        
        return {
            "settlement_duration_minutes_p25": round(weighted_p25, 2),
            "settlement_duration_minutes_p50": round(weighted_p50, 2),
            "settlement_duration_minutes_p75": round(weighted_p75, 2),
            "sample_size": 0,
            "generated": True,
            "method": "weighted_interpolation"
        }
    
    # Strategy 3: Use data from the same bin across all combinations
    if target_bin in bin_stats and bin_stats[target_bin]["p25"]:
        return {
            "settlement_duration_minutes_p25": statistics.mean(bin_stats[target_bin]["p25"]),
            "settlement_duration_minutes_p50": statistics.mean(bin_stats[target_bin]["p50"]),
            "settlement_duration_minutes_p75": statistics.mean(bin_stats[target_bin]["p75"]),
            "sample_size": 0,
            "generated": True,
            "method": "cross_combination_average"
        }
    
    # Strategy 4: Fallback to reasonable defaults
    return {
        "settlement_duration_minutes_p25": 10.0,
        "settlement_duration_minutes_p50": 15.0,
        "settlement_duration_minutes_p75": 25.0,
        "sample_size": 0,
        "generated": True,
        "method": "default_fallback"
    }

def populate_missing_bins(data: Dict, missing_combinations: List[Tuple[str, str, str, List[str]]]) -> Dict:
    """
    Populate missing bins with intelligent estimates.
    
    Returns a copy of the data with missing bins filled in.
    """
    # Create a deep copy of the data
    populated_data = json.loads(json.dumps(data))
    
    # Collect statistics for each bin
    bin_stats = collect_bin_statistics(data)
    
    # Populate missing bins
    for origin_chain_id, destination_chain_id, tickerhash, missing_bins in missing_combinations:
        # Get existing bins for this combination
        existing_bins = list(populated_data[origin_chain_id][destination_chain_id][tickerhash].keys())
        
        for bin_name in missing_bins:
            # Get the specific route's data for baseline scaling
            route_data = populated_data[origin_chain_id][destination_chain_id][tickerhash]
            generated_data = interpolate_bin_data(bin_stats, bin_name, existing_bins, route_data)
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
    
    print("\n🚀 Generation Strategy:")
    print("  1. Baseline scaling from route-specific 0-50000 bin")
    print("  2. Baseline scaling from global 0-50000 bin (fallback)")
    print("  3. Weighted interpolation from surrounding bins")
    print("  4. Use cross-combination averages when available")
    print("  5. Conservative default values as fallback")

def main():
    """Main function to run the bin generation."""
    try:
        # Load the data
        print("Loading settlement_times.json...")
        data = load_settlement_data('settlement_times_from_csv.json')
        
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
        print("Generating missing bins with intelligent estimates...")
        populated_data = populate_missing_bins(data, missing_combinations)
        
        # Save the populated data
        output_file = '../output/settlement_times_populated_improved_from.json'
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
