#!/usr/bin/env python3
"""
Script to convert settlement_time_data.csv back to JSON format.
Converts human-readable chain names and asset symbols back to the nested JSON structure.
"""

import json
import csv
from typing import Dict, List, Tuple
import re

# Chain name to ID mapping (based on common knowledge)
CHAIN_NAME_TO_ID = {
    "arbitrum": "42161",
    "avalanche_c": "43114", 
    "base": "8453",
    "berachain": "80085",
    "blast": "81457",
    "bnb": "56",
    "ethereum": "1",
    "ink": "167000",
    "linea": "59144",
    "mode": "34443",
    "optimism": "10",
    "polygon": "137",
    "ronin": "2020",
    "scroll": "534352",
    "solana": "1399811149",
    "sonic": "1900",
    "taiko": "167008",
    "tron": "728126428",
    "unichain": "130",
    "zircuit": "324",
    "zksync": "324"
}

# Asset symbol to tickerhash mapping (based on common assets)
ASSET_SYMBOL_TO_TICKERHASH = {
    "USDC": "0xd6aca1be9729c13d677335161321649cccae6a591554772516700f986f942eaa",
    "USDT": "0x8b1a1d9c2b109e527c9134b25b1a1833b16b6594f92daa9f6d9b7a6024bce9d0",
    "WETH": "0x0f8a193ff464434486c0daf7db2a895884365d2bc84ba47a68fcf89c1b14b5b8",
    "cbBTC": "0x5b071b590a59395f4028a6c4c9f0c5d2e3b0c0c0c0c0c0c0c0c0c0c0c0c0c0",
    "xPufETH": "0x8b1a1d9c2b109e527c9134b25b1a1833b16b6594f92daa9f6d9b7a6024bce9d1"
}

def load_csv_data(file_path: str) -> List[Dict]:
    """Load the CSV data and return as a list of dictionaries."""
    records = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            records.append(row)
    return records

def parse_amount_range(floor_str: str, ceil_str: str) -> str:
    """
    Convert amount range to bin format.
    Examples:
    - 0, "50,000" -> "0-50000"
    - "50,000", "100,000" -> "50000-100000"
    - "1,000,000", "" -> "1000000+"
    """
    # Remove commas and convert to numbers
    floor = floor_str.replace(",", "")
    ceil = ceil_str.replace(",", "") if ceil_str else ""
    
    if not ceil or ceil == "":
        # Handle the "1,000,000+" case
        return "1000000+"
    
    # Convert to integers for comparison
    try:
        floor_num = int(float(floor))
        ceil_num = int(float(ceil))
        return f"{floor_num}-{ceil_num}"
    except ValueError:
        # Fallback to string format
        return f"{floor}-{ceil}"

def convert_csv_to_json_structure(csv_records: List[Dict]) -> Dict:
    """
    Convert CSV records to the nested JSON structure.
    
    Target structure:
    {
        "chain_id": {
            "destination_chain_id": {
                "tickerhash": {
                    "bin": {
                        "settlement_duration_minutes_p25": value,
                        "settlement_duration_minutes_p50": value,
                        "settlement_duration_minutes_p75": value,
                        "sample_size": value
                    }
                }
            }
        }
    }
    """
    json_structure = {}
    
    for record in csv_records:
        # Get chain IDs
        from_chain_name = record['from_chain_name']
        to_chain_name = record['to_chain_name']
        
        from_chain_id = CHAIN_NAME_TO_ID.get(from_chain_name, from_chain_name)
        to_chain_id = CHAIN_NAME_TO_ID.get(to_chain_name, to_chain_name)
        
        # Get asset tickerhash
        asset_symbol = record['from_asset_symbol']
        tickerhash = ASSET_SYMBOL_TO_TICKERHASH.get(asset_symbol, f"0x{asset_symbol.lower()}")
        
        # Parse amount range to bin format
        bin_name = parse_amount_range(
            record['from_asset_amount_usd_floor'],
            record['from_asset_amount_usd_ceil']
        )
        
        # Create bin data
        bin_data = {
            "settlement_duration_minutes_p25": float(record['settlement_duration_minutes_p25'].replace(",", "")),
            "settlement_duration_minutes_p50": float(record['settlement_duration_minutes_p50'].replace(",", "")),
            "settlement_duration_minutes_p75": float(record['settlement_duration_minutes_p75'].replace(",", "")),
            "sample_size": int(record['sample_size'])
        }
        
        # Build nested structure
        if from_chain_id not in json_structure:
            json_structure[from_chain_id] = {}
        
        if to_chain_id not in json_structure[from_chain_id]:
            json_structure[from_chain_id][to_chain_id] = {}
        
        if tickerhash not in json_structure[from_chain_id][to_chain_id]:
            json_structure[from_chain_id][to_chain_id][tickerhash] = {}
        
        # Add bin data
        json_structure[from_chain_id][to_chain_id][tickerhash][bin_name] = bin_data
    
    return json_structure

def save_json(data: Dict, output_file: str):
    """Save the JSON data to a file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"JSON file written: {output_file}")

def print_conversion_summary(csv_records: List[Dict], json_structure: Dict):
    """Print a summary of the conversion process."""
    print(f"\n=== Conversion Summary ===")
    print(f"CSV Records: {len(csv_records)}")
    
    # Count unique chains and assets
    unique_from_chains = set(record['from_chain_name'] for record in csv_records)
    unique_to_chains = set(record['to_chain_name'] for record in csv_records)
    unique_assets = set(record['from_asset_symbol'] for record in csv_records)
    
    print(f"Unique Origin Chains: {len(unique_from_chains)}")
    print(f"Unique Destination Chains: {len(unique_to_chains)}")
    print(f"Unique Assets: {len(unique_assets)}")
    
    # Count total bins
    total_bins = 0
    for origin_chain in json_structure.values():
        for destination_chain in origin_chain.values():
            for tickerhash in destination_chain.values():
                total_bins += len(tickerhash)
    
    print(f"Total Bins: {total_bins}")
    
    # Show some sample mappings
    print(f"\n=== Sample Chain Mappings ===")
    for i, (name, chain_id) in enumerate(list(CHAIN_NAME_TO_ID.items())[:5]):
        print(f"  {name} -> {chain_id}")
    
    print(f"\n=== Sample Asset Mappings ===")
    for i, (symbol, tickerhash) in enumerate(list(ASSET_SYMBOL_TO_TICKERHASH.items())[:3]):
        print(f"  {symbol} -> {tickerhash[:20]}...")

def main():
    """Main function to convert CSV to JSON."""
    try:
        input_file = 'settlement_time_data.csv'
        output_file = 'settlement_times_from_csv.json'
        
        print("Loading CSV data...")
        csv_records = load_csv_data(input_file)
        
        if not csv_records:
            print("No CSV records found.")
            return
        
        print(f"Loaded {len(csv_records)} CSV records")
        
        print("Converting to JSON structure...")
        json_structure = convert_csv_to_json_structure(csv_records)
        
        print("Saving JSON file...")
        save_json(json_structure, output_file)
        
        # Print summary
        print_conversion_summary(csv_records, json_structure)
        
        # Show sample of converted data
        print(f"\n=== Sample Converted Data ===")
        sample_origin = list(json_structure.keys())[0]
        sample_dest = list(json_structure[sample_origin].keys())[0]
        sample_asset = list(json_structure[sample_origin][sample_dest].keys())[0]
        sample_bin = list(json_structure[sample_origin][sample_dest][sample_asset].keys())[0]
        
        print(f"Sample route: {sample_origin} -> {sample_dest}")
        print(f"Sample asset: {sample_asset}")
        print(f"Sample bin: {sample_bin}")
        print(f"Sample data: {json_structure[sample_origin][sample_dest][sample_asset][sample_bin]}")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
