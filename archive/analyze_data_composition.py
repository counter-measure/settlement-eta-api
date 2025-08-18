#!/usr/bin/env python3
"""
Script to analyze the composition of real vs generated data in settlement_times_populated_improved.json.
"""

import json
from typing import Dict, Tuple

def load_settlement_data(file_path: str) -> Dict:
    """Load the settlement times JSON data."""
    with open(file_path, 'r') as f:
        return json.load(f)

def analyze_data_composition(data: Dict) -> Tuple[int, int, int, Dict]:
    """
    Analyze the composition of real vs generated data.
    
    Returns:
        - Total bins
        - Real data bins
        - Generated bins
        - Breakdown by bin type
    """
    total_bins = 0
    real_data_bins = 0
    generated_bins = 0
    bin_type_breakdown = {}
    
    for origin_chain_id, destinations in data.items():
        for destination_chain_id, tickerhashes in destinations.items():
            for tickerhash, bins in tickerhashes.items():
                for bin_name, bin_data in bins.items():
                    total_bins += 1
                    
                    # Check if this bin was generated
                    if bin_data.get("generated", False):
                        generated_bins += 1
                        method = bin_data.get("method", "unknown")
                        if method not in bin_type_breakdown:
                            bin_type_breakdown[method] = 0
                        bin_type_breakdown[method] += 1
                    else:
                        real_data_bins += 1
    
    return total_bins, real_data_bins, generated_bins, bin_type_breakdown

def print_analysis_report(total_bins: int, real_data_bins: int, generated_bins: int, bin_type_breakdown: Dict):
    """Print a formatted analysis report."""
    print("🔍 Data Composition Analysis")
    print("=" * 50)
    
    print(f"📊 Overall Statistics:")
    print(f"  Total bins: {total_bins:,}")
    print(f"  Real data bins: {real_data_bins:,}")
    print(f"  Generated bins: {generated_bins:,}")
    
    print(f"\n📈 Percentages:")
    real_percentage = (real_data_bins / total_bins) * 100
    generated_percentage = (generated_bins / total_bins) * 100
    print(f"  Real data: {real_percentage:.1f}%")
    print(f"  Generated: {generated_percentage:.1f}%")
    
    print(f"\n🔧 Generation Method Breakdown:")
    for method, count in sorted(bin_type_breakdown.items()):
        method_percentage = (count / total_bins) * 100
        print(f"  {method}: {count:,} bins ({method_percentage:.1f}%)")
    
    print(f"\n💡 Key Insights:")
    if generated_percentage > 50:
        print(f"  ⚠️  More than half of the data is generated")
    elif generated_percentage > 25:
        print(f"  ⚠️  A significant portion ({generated_percentage:.1f}%) is generated")
    else:
        print(f"  ✅ Most data ({real_percentage:.1f}%) is real")
    
    print(f"  📝 {generated_bins:,} bins were artificially created to fill gaps")
    print(f"  🎯 {real_data_bins:,} bins contain actual transaction data")

def analyze_by_bin_size(data: Dict):
    """Analyze data composition by bin size."""
    print(f"\n📦 Analysis by Bin Size")
    print("=" * 50)
    
    bin_sizes = [
        "0-50000",
        "50000-100000", 
        "100000-300000",
        "300000-400000",
        "400000-500000",
        "500000-700000",
        "700000-1000000",
        "1000000+"
    ]
    
    for bin_size in bin_sizes:
        real_count = 0
        generated_count = 0
        
        for origin_chain_id, destinations in data.items():
            for destination_chain_id, tickerhashes in destinations.items():
                for tickerhash, bins in tickerhashes.items():
                    if bin_size in bins:
                        if bins[bin_size].get("generated", False):
                            generated_count += 1
                        else:
                            real_count += 1
        
        total = real_count + generated_count
        if total > 0:
            real_pct = (real_count / total) * 100
            generated_pct = (generated_count / total) * 100
            print(f"  {bin_size}: {real_count:,} real, {generated_count:,} generated ({real_pct:.1f}% real)")

def main():
    """Main function to run the analysis."""
    try:
        # Load the data
        print("Loading settlement_times_populated_improved.json...")
        data = load_settlement_data('settlement_times_populated_improved.json')
        
        # Analyze composition
        print("Analyzing data composition...")
        total_bins, real_data_bins, generated_bins, bin_type_breakdown = analyze_data_composition(data)
        
        # Print report
        print_analysis_report(total_bins, real_data_bins, generated_bins, bin_type_breakdown)
        
        # Analyze by bin size
        analyze_by_bin_size(data)
        
    except FileNotFoundError:
        print("❌ Error: settlement_times_populated_improved.json not found in current directory")
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in settlement_times_populated_improved.json")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
