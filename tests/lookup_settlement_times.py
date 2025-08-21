#!/usr/bin/env python3
"""
Script to look up settlement duration statistics from settlement_times_populated_improved_from.json
"""

import json
import sys
import argparse
import re

def load_chain_data(chain_data_path):
    """
    Load chain data to get asset ticker hashes.
    
    Args:
        chain_data_path (str): Path to chain_data.json file
    
    Returns:
        dict: Chain data containing asset information
    """
    try:
        with open(chain_data_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Chain data file '{chain_data_path}' not found. Asset name lookup will not work.")
        return None
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in chain data file '{chain_data_path}': {e}")
        return None

def get_token_prices():
    """
    Get current token prices in USD.
    
    Returns:
        dict: Dictionary mapping asset symbols to USD prices
    """
    return {
        "USDC": 1.0,
        "USDT": 1.0,
        "ETH": 4250.0,
        "WETH": 4250.0,
        "CLEAR": 0.02029,
        "cbBTC": 113131.51,
        "WBTC": 112734.47,
        "BNB": 300.0,  # Approximate
        "POL": 0.5,    # Approximate
        "AVAX": 35.0,  # Approximate
        "BERA": 0.1,   # Approximate
        "MNT": 0.5,    # Approximate
        "SONIC": 0.01, # Approximate
        "INK": 0.001,  # Approximate
        "APE": 1.5,    # Approximate
        "RON": 0.1,    # Approximate
        "xPufETH": 4250.0  # Same as ETH
    }

def parse_token_amount(amount_string):
    """
    Parse token amount string like "10 WETH" or "1000 USDC".
    
    Args:
        amount_string (str): String like "10 WETH" or "1000 USDC"
    
    Returns:
        tuple: (amount, asset_symbol) or (None, None) if parsing fails
    """
    # Match pattern like "10 WETH" or "1000.5 USDC"
    match = re.match(r'^(\d+(?:\.\d+)?)\s+([A-Za-z]+)$', amount_string.strip())
    if match:
        amount = float(match.group(1))
        asset_symbol = match.group(2).upper()
        return amount, asset_symbol
    return None, None

def convert_to_usd(amount, asset_symbol):
    """
    Convert token amount to USD value.
    
    Args:
        amount (float): Token amount
        asset_symbol (str): Asset symbol (e.g., "WETH", "USDC")
    
    Returns:
        float: USD value
    """
    prices = get_token_prices()
    if asset_symbol in prices:
        return amount * prices[asset_symbol]
    else:
        print(f"Warning: Unknown price for {asset_symbol}, assuming $1")
        return amount

def find_amount_bucket(usd_amount):
    """
    Find the appropriate amount bucket for the given USD amount.
    
    Args:
        usd_amount (float): USD amount
    
    Returns:
        str: Amount bucket string (e.g., "0-50000", "50000-100000")
    """
    if usd_amount <= 50000:
        return "0-50000"
    elif usd_amount <= 100000:
        return "50000-100000"
    elif usd_amount <= 300000:
        return "100000-300000"
    elif usd_amount <= 400000:
        return "300000-400000"
    elif usd_amount <= 500000:
        return "400000-500000"
    elif usd_amount <= 700000:
        return "500000-700000"
    elif usd_amount <= 1000000:
        return "700000-1000000"
    else:
        return "1000000+"

def get_ticker_hash_from_asset_name(chain_data, asset_name, origin_chain=None):
    """
    Convert asset name to ticker hash using chain data.
    
    Args:
        chain_data (dict): Chain data loaded from chain_data.json
        asset_name (str): Asset name (e.g., "WETH", "USDC")
        origin_chain (str, optional): Origin chain ID to narrow search
    
    Returns:
        str: Ticker hash if found, None otherwise
    """
    if not chain_data:
        return None
    
    # Search in hub assets first
    if "hub" in chain_data and "assets" in chain_data["hub"]:
        for symbol, asset_info in chain_data["hub"]["assets"].items():
            if symbol.upper() == asset_name.upper():
                return asset_info["tickerHash"]
    
    # Search in specific chain assets
    if origin_chain and origin_chain in chain_data.get("chains", {}):
        chain_assets = chain_data["chains"][origin_chain].get("assets", {})
        for symbol, asset_info in chain_assets.items():
            if symbol.upper() == asset_name.upper():
                return asset_info["tickerHash"]
    
    # Search in all chains if origin chain not specified or not found
    for chain_id, chain_info in chain_data.get("chains", {}).items():
        if "assets" in chain_info:
            for symbol, asset_info in chain_info["assets"].items():
                if symbol.upper() == asset_name.upper():
                    return asset_info["tickerHash"]
    
    return None

def lookup_settlement_times(json_file_path, origin_chain, destination_chain, asset_hash, amount_range=None):
    """
    Look up settlement duration statistics for specific parameters.
    
    Args:
        json_file_path (str): Path to the JSON file
        origin_chain (str): Origin chain ID
        destination_chain (str): Destination chain ID  
        asset_hash (str): Asset hash to look up
        amount_range (str, optional): Specific amount range to look up (e.g., "0-50000")
    
    Returns:
        dict: Dictionary containing the settlement duration statistics
    """
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{json_file_path}': {e}")
        return None
    
    # Navigate through the nested structure
    if origin_chain not in data:
        print(f"Error: Origin chain '{origin_chain}' not found in data.")
        return None
    
    if destination_chain not in data[origin_chain]:
        print(f"Error: Destination chain '{destination_chain}' not found for origin chain '{origin_chain}'.")
        return None
    
    if asset_hash not in data[origin_chain][destination_chain]:
        print(f"Error: Asset '{asset_hash}' not found for origin chain '{origin_chain}' and destination chain '{destination_chain}'.")
        return None
    
    # Get the asset data
    asset_data = data[origin_chain][destination_chain][asset_hash]
    
    # If amount range is specified, use it; otherwise use the first available
    if amount_range:
        if amount_range not in asset_data:
            print(f"Error: Amount range '{amount_range}' not found for this asset.")
            print(f"Available ranges: {list(asset_data.keys())}")
            return None
        target_range = amount_range
    else:
        # Use the first amount range (typically "0-50000")
        amount_ranges = list(asset_data.keys())
        if not amount_ranges:
            print("Error: No amount ranges found for this asset.")
            return None
        target_range = amount_ranges[0]
        print(f"Note: No amount range specified, using first available: {target_range}")
    
    range_data = asset_data[target_range]
    
    # Extract the requested statistics
    result = {
        "origin_chain": origin_chain,
        "destination_chain": destination_chain,
        "asset": asset_hash,
        "amount_range": target_range,
        "settlement_duration_minutes_p25": range_data.get("settlement_duration_minutes_p25"),
        "settlement_duration_minutes_p50": range_data.get("settlement_duration_minutes_p50"),
        "settlement_duration_minutes_p75": range_data.get("settlement_duration_minutes_p75"),
        "sample_size": range_data.get("sample_size"),
        "generated": range_data.get("generated", False),
        "method": range_data.get("method", "N/A")
    }
    
    return result

def get_chain_id_from_name(chain_name):
    """
    Convert chain name to chain ID.
    
    Args:
        chain_name (str): Chain name (e.g., "ethereum", "arbitrum")
    
    Returns:
        str: Chain ID
    """
    chain_mapping = {
        "ethereum": "1",
        "arbitrum": "42161",
        "optimism": "10",
        "base": "8453",
        "polygon": "137",
        "bnb": "56",
        "avalanche_c": "43114",
        "scroll": "534352",
        "zksync": "324",
        "linea": "59144",
        "blast": "81457",
        "taiko": "167000",
        "mode": "34443",
        "unichain": "130",
        "zircuit": "48900",
        "berachain": "80094",
        "sonic": "146",
        "ink": "57073",
        "ronin": "2020",
        "solana": "1399811149",
        "tron": "728126428",
        "apechain": "33139"
    }
    
    return chain_mapping.get(chain_name.lower(), chain_name)

def run_lookup(origin_chain, destination_chain, asset_symbol, usd_amount, json_file_path="output/settlement_times_populated_improved_from.json", chain_data_path="run/chain_data.json", verbose=False):
    """
    Run a settlement time lookup and return results.
    
    Args:
        origin_chain (str): Origin chain name or ID
        destination_chain (str): Destination chain name or ID
        asset_symbol (str): Asset symbol (e.g., "WETH", "USDC")
        usd_amount (float): USD amount
        json_file_path (str): Path to settlement times JSON file
        chain_data_path (str): Path to chain data JSON file
        verbose (bool): Whether to print verbose output
    
    Returns:
        dict: Lookup results or None if failed
    """
    # Convert chain names to IDs if needed
    origin_chain_id = get_chain_id_from_name(origin_chain)
    destination_chain_id = get_chain_id_from_name(destination_chain)
    
    # Load chain data for asset name lookup
    chain_data = load_chain_data(chain_data_path)
    
    # Find amount bucket
    amount_range = find_amount_bucket(usd_amount)
    
    # Get asset ticker hash
    asset_hash = get_ticker_hash_from_asset_name(chain_data, asset_symbol, origin_chain_id)
    
    if not asset_hash:
        if verbose:
            print(f"Error: Could not find ticker hash for asset '{asset_symbol}'")
        return None
    
    if verbose:
        print(f"Looking up: {origin_chain} -> {destination_chain}, {asset_symbol}, ${usd_amount:,.2f} (bucket: {amount_range})")
    
    # Perform the lookup
    result = lookup_settlement_times(json_file_path, origin_chain_id, destination_chain_id, asset_hash, amount_range)
    
    if result and verbose:
        print(f"  Found: P25={result['settlement_duration_minutes_p25']}, P50={result['settlement_duration_minutes_p50']}, P75={result['settlement_duration_minutes_p75']}")
    
    return result

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Look up settlement duration statistics from JSON file')
    parser.add_argument('--origin', '-o', default="10", help='Origin chain ID (default: 10)')
    parser.add_argument('--destination', '-d', default="1", help='Destination chain ID (default: 1)')
    parser.add_argument('--asset', '-a', default="WETH", 
                       help='Asset name (e.g., "WETH", "USDC") or full ticker hash')
    parser.add_argument('--amount', '-r', help='Amount range to look up (e.g., "0-50000", "50000-100000") or token amount (e.g., "10 WETH")')
    parser.add_argument('--file', '-f', default="output/settlement_times_populated_improved_from.json", 
                       help='JSON file path (default: output/settlement_times_populated_improved_from.json)')
    parser.add_argument('--chain-data', '-c', default="run/chain_data.json",
                       help='Chain data file path (default: run/chain_data.json)')
    
    args = parser.parse_args()
    
    # Load chain data for asset name lookup
    chain_data = load_chain_data(args.chain_data)
    
    # Process amount argument first to see if it contains an asset
    amount_range = None
    token_amount_info = None
    asset_from_amount = None
    
    if args.amount:
        # Check if it's a token amount (e.g., "10 WETH")
        amount, asset_symbol = parse_token_amount(args.amount)
        if amount and asset_symbol:
            # This is a token amount, convert to USD and find bucket
            usd_value = convert_to_usd(amount, asset_symbol)
            amount_range = find_amount_bucket(usd_value)
            token_amount_info = {
                "amount": amount,
                "asset": asset_symbol,
                "usd_value": usd_value,
                "bucket": amount_range
            }
            asset_from_amount = asset_symbol
            print(f"Converted {amount} {asset_symbol} to ${usd_value:,.2f} USD")
            print(f"Amount falls into bucket: {amount_range}")
        else:
            # This is a direct amount range
            amount_range = args.amount
    
    # Determine which asset to use (amount asset takes precedence over --asset argument)
    asset_to_use = asset_from_amount if asset_from_amount else args.asset
    
    # Determine if asset is a name or hash
    asset_hash = asset_to_use
    asset_name = None
    
    if not asset_to_use.startswith("0x"):
        # This looks like an asset name, try to convert to hash
        asset_name = asset_to_use
        asset_hash = get_ticker_hash_from_asset_name(chain_data, asset_name, args.origin)
        
        if not asset_hash:
            print(f"Error: Could not find ticker hash for asset '{asset_name}' in chain data.")
            print("Available assets in hub:")
            if chain_data and "hub" in chain_data and "assets" in chain_data["hub"]:
                for symbol in chain_data["hub"]["assets"].keys():
                    print(f"  - {symbol}")
            print("\nAvailable assets in origin chain:")
            if chain_data and "chains" in chain_data and args.origin in chain_data["chains"]:
                for symbol in chain_data["chains"][args.origin].get("assets", {}).keys():
                    print(f"  - {symbol}")
            print(f"\nPlease use a valid asset name or provide the full ticker hash.")
            sys.exit(1)
        
        print(f"Converted asset name '{asset_name}' to ticker hash: {asset_hash}")
    
    print("Looking up settlement times with parameters:")
    print(f"  Origin chain: {args.origin}")
    print(f"  Destination chain: {args.destination}")
    if asset_name:
        print(f"  Asset: {asset_name} ({asset_hash})")
    else:
        print(f"  Asset: {asset_hash}")
    if token_amount_info:
        print(f"  Token amount: {token_amount_info['amount']} {token_amount_info['asset']} (${token_amount_info['usd_value']:,.2f})")
        print(f"  Amount bucket: {amount_range}")
    elif args.amount:
        print(f"  Amount range: {amount_range}")
    print(f"  JSON file: {args.file}")
    print("-" * 60)
    
    # Perform the lookup
    result = lookup_settlement_times(args.file, args.origin, args.destination, asset_hash, amount_range)
    
    if result:
        print("Results found:")
        print(f"  Amount range: {result['amount_range']}")
        print(f"  P25 (25th percentile): {result['settlement_duration_minutes_p25']} minutes")
        print(f"  P50 (50th percentile): {result['settlement_duration_minutes_p50']} minutes")
        print(f"  P75 (75th percentile): {result['settlement_duration_minutes_p75']} minutes")
        print(f"  Sample size: {result['sample_size']}")
        print(f"  Generated: {result['generated']}")
        if result['generated']:
            print(f"  Method: {result['method']}")
    else:
        print("No results found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
