# Settlement Time Lookup Tests

This directory contains test cases and a test runner script for validating the settlement time lookup functionality.

## Files

- **`test_cases.csv`** - Contains 353 test cases with expected settlement duration values
- **`lookup_settlement_times.py`** - Modified lookup script that can be imported and used programmatically
- **`run_test_cases.py`** - Test runner script that executes all test cases from the CSV

## Test Case Format

Each test case in `test_cases.csv` contains:

| Column | Description | Example |
|--------|-------------|---------|
| `from_chain_name` | Origin chain name | `arbitrum`, `ethereum`, `optimism` |
| `to_chain_name` | Destination chain name | `avalanche_c`, `base`, `polygon` |
| `from_asset_symbol` | Asset symbol | `WETH`, `USDC`, `USDT` |
| `amount` | USD amount (with commas) | `23,356`, `40,368`, `37,854` |
| `settlement_duration_minutes_p25` | Expected 25th percentile | `103.5`, `3.25`, `4` |
| `settlement_duration_minutes_p50` | Expected 50th percentile | `203`, `6.5`, `4.5` |
| `settlement_duration_minutes_p75` | Expected 75th percentile | `321`, `41.5`, `8` |

## Running Tests

### Run All Tests
```bash
python3 tests/run_test_cases.py
```

### Run Limited Number of Tests
```bash
python3 tests/run_test_cases.py --max-tests 10
```

### Run with Custom File Paths
```bash
python3 tests/run_test_cases.py \
  --csv tests/test_cases.csv \
  --json output/settlement_times_populated_improved_from.json \
  --chain-data run/chain_data.json
```

### Quiet Mode (Less Output)
```bash
python3 tests/run_test_cases.py --quiet
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--csv` | Path to test cases CSV file | `tests/test_cases.csv` |
| `--json` | Path to settlement times JSON file | `output/settlement_times_populated_improved_from.json` |
| `--chain-data` | Path to chain data JSON file | `run/chain_data.json` |
| `--max-tests` | Maximum number of tests to run | All tests |
| `--quiet`, `-q` | Reduce verbose output | False |

## Test Results

The script provides detailed results for each test case:

- **✅ PASS** - All expected values match actual values
- **❌ FAIL** - One or more expected values don't match actual values
- **Lookup time** - Time taken to perform each lookup
- **Overall summary** - Total tests, pass/fail counts, success rate, timing

## Example Output

```
================================================================================
Test Case: arbitrum -> avalanche_c, USDC, $23,356.00
Expected: P25=103.5, P50=203, P75=321
================================================================================
Looking up: arbitrum -> avalanche_c, USDC, $23,356.00 (bucket: 0-50000)
  Found: P25=103.5, P50=203.0, P75=321.0
  Actual: P25=103.5, P50=203.0, P75=321.0
  Match: P25=✅, P50=✅, P75=✅
  Overall: ✅ PASS
  Lookup time: 0.003s

================================================================================
TEST EXECUTION SUMMARY
================================================================================
Total tests run: 3
Passed: 3
Failed: 0
Success rate: 100.0%
Total execution time: 0.32s
Total lookup time: 0.01s
Average lookup time: 0.003s
```

## Chain Name Mapping

The script automatically converts chain names to chain IDs:

| Chain Name | Chain ID |
|------------|----------|
| `ethereum` | `1` |
| `arbitrum` | `42161` |
| `optimism` | `10` |
| `base` | `8453` |
| `polygon` | `137` |
| `bnb` | `56` |
| `avalanche_c` | `43114` |
| And many more... |

## Integration

The `lookup_settlement_times.py` script can be imported and used programmatically:

```python
from tests.lookup_settlement_times import run_lookup

result = run_lookup(
    origin_chain="arbitrum",
    destination_chain="ethereum", 
    asset_symbol="WETH",
    usd_amount=50000,
    verbose=True
)

if result:
    print(f"P25: {result['settlement_duration_minutes_p25']}")
    print(f"P50: {result['settlement_duration_minutes_p50']}")
    print(f"P75: {result['settlement_duration_minutes_p75']}")
```

## Performance

- **Fast execution**: Each lookup typically takes 2-5ms
- **Efficient**: Processes hundreds of test cases in seconds
- **Scalable**: Can run all 353 test cases or limit to specific numbers
- **Robust**: Handles errors gracefully and provides detailed feedback
