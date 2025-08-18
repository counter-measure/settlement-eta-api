#!/usr/bin/env python3
import json

# Chain name to ID mapping based on chain_data.json
CHAIN_NAME_TO_ID = {
    "arbitrum": "42161",
    "base": "8453", 
    "berachain": "80094",
    "blast": "81457",
    "bnb": "56",
    "ethereum": "1",
    "ink": "57073",
    "linea": "59144",
    "optimism": "10",
    "polygon": "137",
    "ronin": "2020",
    "solana": "1399811149",
    "sonic": "146",
    "unichain": "130",
    "zircuit": "48900",
    "zksync": "324",
    "avalanche_c": "43114"  # This appears to be avalanche
}

def update_chain_names(data):
    """Recursively update chain names to chain IDs in the data structure"""
    if isinstance(data, dict):
        updated_data = {}
        for key, value in data.items():
            # Check if this key is a chain name that needs to be updated
            if key in CHAIN_NAME_TO_ID:
                new_key = CHAIN_NAME_TO_ID[key]
                updated_data[new_key] = update_chain_names(value)
            else:
                updated_data[key] = update_chain_names(value)
        return updated_data
    elif isinstance(data, list):
        return [update_chain_names(item) for item in data]
    else:
        return data

def main():
    # Read the settlement data
    with open('settlement_duration_percentiles_with_asset.json', 'r') as f:
        settlement_data = json.load(f)
    
    # Update the chain names
    updated_data = update_chain_names(settlement_data)
    
    # Write the updated data back to the file
    with open('settlement_duration_percentiles_with_asset.json', 'w') as f:
        json.dump(updated_data, f, indent=2)
    
    print("Successfully updated chain names to chain IDs!")
    print("\nChain name to ID mappings used:")
    for name, id in CHAIN_NAME_TO_ID.items():
        print(f"  {name} -> {id}")

if __name__ == "__main__":
    main()
