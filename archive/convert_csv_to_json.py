#!/usr/bin/env python3
"""
Script to convert settlement_time_data.csv to the same format as settlement_times.json
Now includes settlement_duration_minutes_p50 column
"""

import json
import csv
import os

def load_json_file(file_path):
    """Load and return JSON data from file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def load_csv_file(file_path):
    """Load and return CSV data from file"""
    try:
        data = []
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def save_json_file(file_path, data):
    """Save JSON data to file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved converted data to {file_path}")
    except Exception as e:
        print(f"Error saving {file_path}: {e}")

def get_chain_id_mapping():
    """Create a mapping from chain names to chain IDs"""
    # Based on the existing JSON structure and common chain mappings
    chain_mapping = {
        'arbitrum': '42161',
        'avalanche_c': '43114',
        'base': '8453',
        'berachain': '80094',
        'blast': '81457',
        'bnb': '56',
        'ethereum': '1',
        'ink': '57073',
        'linea': '59144',
        'mode': '34443',
        'optimism': '10',
        'polygon': '137',
        'ronin': '2020',
        'scroll': '534352',
        'solana': '1399811149',
        'sonic': '146',
        'taiko': '167000',
        'tron': '728126428',
        'unichain': '130',
        'zircuit': '48900',
        'zksync': '324'
    }
    return chain_mapping

def get_asset_ticker_hash_mapping():
    """Create a mapping from asset symbols to ticker hashes"""
    # Based on the existing JSON structure
    asset_mapping = {
        'WETH': '0x0f8a193ff464434486c0daf7db2a895884365d2bc84ba47a68fcf89c1b14b5b8',
        'USDC': '0xd6aca1be9729c13d677335161321649cccae6a591554772516700f986f942eaa',
        'USDT': '0x8b1a1d9c2b109e527c9134b25b1a1833b16b6594f92daa9f6d9b7a6024bce9d0',
        'ETH': '0xaaaebeba3810b1e6b70781f14b2d72c1cb89c0b2b320c43bb67ff79f562f5ff4',
        'CLEAR': '0x06ac253a00ee13562eecafc06057c6db73566a05bdce988194aad3616e28e87c',
        'xPufETH': '0x7ca978c7f993c411238b0887969711b470a3133448ab70e4f18aa4d63dcb7907',
        'cbBTC': '0xab7216efe876c5163ebb1d05a1a6b63e00fb73d1d68ddf079460c106356fd162',
        'WBTC': '0x98da2c5e4c6b1db946694570273b859a6e4083ccc8faa155edfc4c54eb3cfd73'
    }
    return asset_mapping

def parse_amount_range(amount_str):
    """Parse amount range string and return formatted range"""
    if not amount_str or amount_str == '':
        return "1000000+"
    
    # Remove commas and quotes
    amount_str = amount_str.replace(',', '').replace('"', '')
    
    if amount_str == "50,000":
        return "0-50000"
    elif amount_str == "100,000":
        return "50000-100000"
    elif amount_str == "300,000":
        return "100000-300000"
    elif amount_str == "400,000":
        return "300000-400000"
    elif amount_str == "500,000":
        return "400000-500000"
    elif amount_str == "700,000":
        return "500000-700000"
    elif amount_str == "1,000,000":
        return "700000-1000000"
    else:
        # Handle other cases or return default
        return "0-50000"

def convert_csv_to_json_format(csv_data):
    """Convert CSV data to the JSON format structure"""
    chain_mapping = get_chain_id_mapping()
    asset_mapping = get_asset_ticker_hash_mapping()
    
    result = {}
    
    for row in csv_data:
        from_chain = row['from_chain_name']
        to_chain = row['to_chain_name']
        asset = row['from_asset_symbol']
        amount_range = parse_amount_range(row['from_asset_amount_usd_ceil'])
        
        # Get chain IDs
        from_chain_id = chain_mapping.get(from_chain)
        to_chain_id = chain_mapping.get(to_chain)
        
        if not from_chain_id or not to_chain_id:
            print(f"Warning: Unknown chain name: {from_chain} or {to_chain}")
            continue
        
        # Get asset ticker hash
        asset_ticker_hash = asset_mapping.get(asset)
        if not asset_ticker_hash:
            print(f"Warning: Unknown asset symbol: {asset}")
            continue
        
        # Initialize structure if not exists
        if from_chain_id not in result:
            result[from_chain_id] = {}
        
        if to_chain_id not in result[from_chain_id]:
            result[from_chain_id][to_chain_id] = {}
        
        if asset_ticker_hash not in result[from_chain_id][to_chain_id]:
            result[from_chain_id][to_chain_id][asset_ticker_hash] = {}
        
        # Add amount range data with all three percentiles
        result[from_chain_id][to_chain_id][asset_ticker_hash][amount_range] = {
            "settlement_duration_minutes_p25": float(row['settlement_duration_minutes_p25'].replace(',', '')),
            "settlement_duration_minutes_p50": float(row['settlement_duration_minutes_p50'].replace(',', '')),
            "settlement_duration_minutes_p75": float(row['settlement_duration_minutes_p75'].replace(',', '')),
            "sample_size": int(row['sample_size'])
        }
    
    return result

def main():
    # File paths
    csv_file = "settlement_time_data.csv"
    output_file = "settlement_times_converted.json"
    
    # Load CSV data
    print("Loading CSV data...")
    csv_data = load_csv_file(csv_file)
    if not csv_data:
        return
    
    print(f"Loaded {len(csv_data)} rows from CSV")
    
    # Convert to JSON format
    print("Converting CSV to JSON format...")
    json_data = convert_csv_to_json_format(csv_data)
    
    # Save converted data
    print("Saving converted data...")
    save_json_file(output_file, json_data)
    
    print("Conversion completed successfully!")
    print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    main()
