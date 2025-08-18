# CSV Conversion Summary

## Overview
Successfully converted `settlement_times_populated_improved.json` to CSV format with human-readable names for chains and assets.

## Conversion Details

### Input Files
- **Source**: `settlement_times_populated_improved.json` (15,846 lines)
- **Mapping**: `chain_data.json` (1,582 lines)

### Output File
- **CSV**: `settlement_times_populated_improved.csv` (304 KB, 1,945 rows)

## Data Mapping Results

### Chain Names
- **Total chains mapped**: 25
- **Mapping format**: `Evm {chain_id}` (e.g., "Evm 42161", "Evm 43114")
- **Special case**: Chain 25327 → "Everclear Hub"

### Asset Names
- **Total assets mapped**: 18
- **Successfully mapped assets**:
  - USDC: 768 records
  - WETH: 800 records  
  - USDT: 304 records
  - cbBTC: 16 records
  - xPufETH: 56 records

## CSV Structure

### Columns
1. `origin_chain_id` - Original chain ID
2. `origin_chain_name` - Human-readable origin chain name
3. `destination_chain_id` - Original destination chain ID
4. `destination_chain_name` - Human-readable destination chain name
5. `tickerhash` - Original tickerhash
6. `asset_name` - Human-readable asset symbol
7. `bin` - Transaction amount bin
8. `settlement_duration_minutes_p25` - 25th percentile settlement time
9. `settlement_duration_minutes_p50` - 50th percentile settlement time
10. `settlement_duration_minutes_p75` - 75th percentile settlement time
11. `sample_size` - Number of samples for this bin
12. `generated` - Whether data was generated (True/False)
13. `method` - Generation method used

### Data Coverage
- **Total records**: 1,944 (excluding header)
- **Unique origin chains**: 25
- **Unique destination chains**: 25
- **Unique assets**: 18
- **Transaction bins**: 8 per combination

## Benefits of CSV Format

1. **Human-readable**: Chain IDs and tickerhashes are now readable names
2. **Spreadsheet compatible**: Easy to open in Excel, Google Sheets, etc.
3. **Analysis ready**: Can be easily imported into data analysis tools
4. **Filterable**: Easy to filter by chain, asset, or bin
5. **Sortable**: Can sort by any column for better insights

## Usage Examples

### Filter by Asset
```bash
# Get all USDC settlement times
grep "USDC" settlement_times_populated_improved.csv
```

### Filter by Chain
```bash
# Get all data for Arbitrum (42161)
grep "Evm 42161" settlement_times_populated_improved.csv
```

### Filter by Generated Data
```bash
# Get only generated data
grep "True" settlement_times_populated_improved.csv
```

## Script Features

The conversion script (`convert_to_csv.py`) includes:
- **Automatic mapping**: Builds chain and asset name mappings from `chain_data.json`
- **Fallback handling**: Uses descriptive names when exact matches aren't found
- **Data preservation**: Maintains all original data while adding readable names
- **Error handling**: Graceful handling of missing or malformed data
- **Progress reporting**: Shows mapping statistics and sample results
