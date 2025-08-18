#!/usr/bin/env python3
"""
Script to convert settlement_times_populated_improved.json to CSV format.
Maps chain IDs and tickerhashes to readable names using chain_data.json.
"""

import json
import csv
from typing import Dict, List, Tuple

def load_chain_data(file_path: str) -> Dict:
    """Load the chain data JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def load_settlement_data(file_path: str) -> Dict:
    """Load the settlement times JSON data."""
    with open(file_path, 'r') as f:
        return json.load(f)

def build_chain_name_mapping(chain_data: Dict) -> Dict[str, str]:
    """Build a mapping from chain ID to chain name."""
    chain_names = {}
    
    # Add hub if it has a name
    if 'hub' in chain_data:
        chain_names['25327'] = 'Everclear Hub'
    
    # Add all chains
    if 'chains' in chain_data:
        for chain_id, chain_info in chain_data['chains'].items():
            # Try to get a meaningful name
            if 'name' in chain_info:
                chain_names[chain_id] = chain_info['name']
            elif 'network' in chain_info:
                # Use network + chain_id as fallback
                chain_names[chain_id] = f"{chain_info['network'].title()} {chain_id}"
            else:
                chain_names[chain_id] = f"Chain {chain_id}"
    
    return chain_names

def build_asset_name_mapping(chain_data: Dict) -> Dict[str, str]:
    """Build a mapping from tickerhash to asset symbol."""
    asset_names = {}
    
    # Process hub assets
    if 'hub' in chain_data and 'assets' in chain_data['hub']:
        for symbol, asset_info in chain_data['hub']['assets'].items():
            if 'tickerHash' in asset_info:
                asset_names[asset_info['tickerHash']] = symbol
    
    # Process chain assets
    if 'chains' in chain_data:
        for chain_id, chain_info in chain_data['chains'].items():
            if 'assets' in chain_info:
                for symbol, asset_info in chain_info['assets'].items():
                    if 'tickerHash' in asset_info:
                        asset_names[asset_info['tickerHash']] = symbol
    
    return asset_names

def flatten_settlement_data(data: Dict, chain_names: Dict[str, str], asset_names: Dict[str, str]) -> List[Dict]:
    """Flatten the nested settlement data into a list of records."""
    records = []
    
    for origin_chain_id, destinations in data.items():
        origin_chain_name = chain_names.get(origin_chain_id, f"Chain {origin_chain_id}")
        
        for destination_chain_id, tickerhashes in destinations.items():
            destination_chain_name = chain_names.get(destination_chain_id, f"Chain {destination_chain_id}")
            
            for tickerhash, bins in tickerhashes.items():
                asset_name = asset_names.get(tickerhash, f"Asset {tickerhash[:10]}...")
                
                for bin_name, bin_data in bins.items():
                    record = {
                        'origin_chain_id': origin_chain_id,
                        'origin_chain_name': origin_chain_name,
                        'destination_chain_id': destination_chain_id,
                        'destination_chain_name': destination_chain_name,
                        'tickerhash': tickerhash,
                        'asset_name': asset_name,
                        'bin': bin_name,
                        'settlement_duration_minutes_p25': bin_data.get('settlement_duration_minutes_p25', ''),
                        'settlement_duration_minutes_p50': bin_data.get('settlement_duration_minutes_p50', ''),
                        'settlement_duration_minutes_p75': bin_data.get('settlement_duration_minutes_p75', ''),
                        'sample_size': bin_data.get('sample_size', ''),
                        'generated': bin_data.get('generated', False),
                        'method': bin_data.get('method', '')
                    }
                    records.append(record)
    
    return records

def write_csv(records: List[Dict], output_file: str):
    """Write the records to a CSV file."""
    if not records:
        print("No records to write.")
        return
    
    fieldnames = records[0].keys()
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"CSV file written: {output_file}")
    print(f"Total records: {len(records)}")

def main():
    """Main function to convert JSON to CSV."""
    try:
        # Load data files
        print("Loading chain data...")
        chain_data = load_chain_data('chain_data.json')
        
        print("Loading settlement data...")
        settlement_data = load_settlement_data('../output/settlement_times_populated_improved_from.json')
        
        # Build mappings
        print("Building chain name mappings...")
        chain_names = build_chain_name_mapping(chain_data)
        
        print("Building asset name mappings...")
        asset_names = build_asset_name_mapping(chain_data)
        
        print(f"Found {len(chain_names)} chain names")
        print(f"Found {len(asset_names)} asset names")
        
        # Flatten data
        print("Flattening settlement data...")
        records = flatten_settlement_data(settlement_data, chain_names, asset_names)
        
        # Write CSV
        output_file = '../output/settlement_times_improved.csv'
        write_csv(records, output_file)
        
        # Print some sample mappings
        print("\nSample chain name mappings:")
        for i, (chain_id, name) in enumerate(list(chain_names.items())[:5]):
            print(f"  {chain_id} -> {name}")
        
        print("\nSample asset name mappings:")
        for i, (tickerhash, symbol) in enumerate(list(asset_names.items())[:5]):
            print(f"  {tickerhash[:20]}... -> {symbol}")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
