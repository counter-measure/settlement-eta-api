# Goal
Include estimated settlement time in the quote endpoint.

# Proposed Solution

## **User Flow**

1. User requests quote from /routes/quote
2. /routes/quote endpoint returns settlement time based on algo chosen below

## Algo

1. User requests quote with:
    - Origin
    - Dest
    - Asset
    - Amount
2. Values are looked up in the matrix below
3. P25 and P75 settlement times are returned as a range in the /routes/quotes endpoint

**Route / Asset Settlement time matrix below**

https://everclear.metabaseapp.com/question/1126-settlement-time-eta-api 

**Route / Token Settlement time JSON lookup below**
settlement_duration_percentiles_with_asset.json 

**Example implementation:**
asset_specific_lookup_example.js

**Data details:**

- Includes all route and asset combinations from the last 30 days
- Internal solver addresses and MM addresses have been filtered out
- Only routes that have been used 3 times or more in the last 30 days are present
- Amounts have been binned into practical sized bins