# Technical Requirements: Settlement Time ETA Feature

## Document Information

- **Feature**: Settlement Time ETA Endpoint
- **Document Version**: 1.0
- **Last Updated**: January 27, 2025
- **Related Documents**: PRD.md, user_stories.md, asset_specific_lookup_example.js

## Overview

This document outlines the technical requirements for implementing the Settlement Time ETA feature, which provides estimated settlement duration ranges for bridge quotes. The feature addresses critical customer pain points around settlement time inconsistency and enables informed decision-making for bridge users.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Analytics     │    │   Data Pipeline │    │   API Layer     │
│   Pipeline      │───▶│   (ETL Jobs)    │───▶│   (Quote API)   │
│   (Goldsky)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Data Storage  │    │   Cache Layer   │
                       │   (JSON Files)  │    │   (Redis)       │
                       └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Data Collection**: Analytics pipeline collects settlement duration data
2. **Data Processing**: Daily ETL job processes and aggregates data
3. **Data Storage**: Optimized JSON structures for fast lookups
4. **API Layer**: Quote endpoint enhanced with settlement estimates
5. **Caching**: In-memory caching for performance optimization

## Data Requirements

### Data Sources

#### Primary Data Source
- **Source**: Existing Goldsky/analytics infrastructure
- **Format**: Settlement duration data with asset-specific granularity
- **Frequency**: Daily updates with rolling 30-day window
- **Filtering**: Exclude internal solver and market maker addresses
- **Minimum Sample Size**: ≥3 transactions per route/asset/amount combination

#### Data Structure Requirements

**Asset-Specific Data Structure**
```json
{
  "origin_chain": {
    "destination_chain": {
      "asset_symbol": {
        "amount_range": {
          "settlement_duration_minutes_p25": number,
          "settlement_duration_minutes_p75": number,
          "sample_size": number
        }
      }
    }
  }
}
```

**Route Category Averages Structure**
```json
{
  "route_category": {
    "asset_symbol": {
      "amount_range": {
        "settlement_duration_minutes_p25": number,
        "settlement_duration_minutes_p75": number,
        "sample_size": number,
        "confidence": "high|medium|low",
        "description": string
      }
    }
  }
}
```

### Data Quality Requirements

- **Accuracy**: Settlement times within P25-P75 range 75% of time
- **Freshness**: Data updated daily with monitoring alerts
- **Completeness**: 100% route coverage with fallback estimates
- **Consistency**: Standardized units (minutes) across all responses
- **Transparency**: Sample sizes and confidence indicators included

## API Requirements

### Endpoint Specification

**Enhanced Quote Endpoint**
```
POST /routes/quote
```

**Request Body** (Unchanged)
```json
{
  "originChainId": 42161,
  "destinationChainId": 1,
  "asset": "0xa0b86a33e6fe17d1c55c4acb1e7c5e6e1f3f8c2d",
  "amount": "100000000000000000000000"
}
```

**Enhanced Response**
```json
{
  "route": {
    "originChainId": 42161,
    "destinationChainId": 1,
    "asset": "0xa0b86a33e6fe17d1c55c4acb1e7c5e6e1f3f8c2d",
    "amount": "100000000000000000000000"
  },
  "fees": {
    "everclear": "90000000000000000000",
    "gas": "15000000000000000",
    "total": "105000000000000000000"
  },
  "limits": {
    "min": "1000000000000000000",
    "max": "1000000000000000000000000"
  },
  "priceImpact": "0.12",
  "destinationAmountReceived": "99895000000000000000000",
  "settlementEstimate": {
    "p25Minutes": 15,
    "p75Minutes": 49,
    "displayRange": "15-49 minutes",
    "confidenceLevel": "high",
    "dataSource": "exact_route_with_asset",
    "assetSymbol": "USDC",
    "sampleSize": 99,
    "note": "Based on 99 recent transactions",
    "lastUpdated": "2025-08-07"
  },
  "timestamp": "2025-08-07T10:30:00.000Z"
}
```

### API Response Fields

**settlementEstimate** (object, optional)
- **p25Minutes** (number): 25th percentile settlement time in minutes
- **p75Minutes** (number): 75th percentile settlement time in minutes
- **displayRange** (string): Human-readable range for UI display
- **confidenceLevel** (string): Data quality indicator ("high", "medium", "low")
- **dataSource** (string): Source of settlement data
- **assetSymbol** (string): Asset symbol used for estimation
- **sampleSize** (number): Number of transactions used for calculation
- **note** (string, optional): Additional context for fallback estimates
- **lastUpdated** (string): ISO date when settlement data was last refreshed

### Data Source Values

- `"exact_route_with_asset"`: Exact match for route and asset
- `"route_with_different_asset"`: Route exists but different asset used
- `"route_category_average"`: L1/L2 category average used

## Performance Requirements

### Response Time Requirements

- **Settlement Time Lookup**: <50ms (O(1) complexity)
- **Quote Endpoint Response**: <200ms (currently ~150ms)
- **API Throughput**: Support 10x current volume (aggregator-scale)
- **Cache Performance**: In-memory caching with daily refresh

### Scalability Requirements

- **Concurrent Requests**: Support aggregator-scale load
- **Data Volume**: Handle 27 chains × 5 assets × 8 amount ranges
- **Cache Strategy**: Redis for in-memory caching
- **Horizontal Scaling**: Support for multiple API instances

### Reliability Requirements

- **Uptime**: 99.9% availability
- **Error Handling**: Graceful degradation without affecting existing functionality
- **Data Freshness**: Daily updates with monitoring alerts
- **Backward Compatibility**: Existing integrations continue to work

## Data Processing Requirements

### ETL Pipeline Requirements

**Daily Data Processing**
- Process settlement data from analytics pipeline
- Calculate P25 and P75 percentiles for each route/asset/amount combination
- Filter routes with <3 transactions in last 30 days
- Generate optimized JSON structures for fast lookups
- Update route category averages with asset-specific data

**Data Validation**
- Sample size validation (minimum 3 transactions)
- Confidence level calculation based on sample size
- Data freshness monitoring
- Error handling for missing or invalid data

### Amount Range Binning

**Supported Amount Ranges**
- $0 - $50,000
- $50,000 - $100,000
- $100,000 - $300,000
- $300,000 - $400,000
- $400,000 - $500,000
- $500,000 - $700,000
- $700,000 - $1,000,000
- $1,000,000+

**Binning Logic**
- Select appropriate bin based on user's requested amount
- Fall back to closest available range if exact match not found
- Handle edge cases (amounts above highest range)

## Fallback Strategy Requirements

### Multi-Tier Fallback System

**Tier 1: Exact Route with Specific Asset** (Highest Priority)
- Look for exact match: `fromChain -> toChain -> assetSymbol -> amountRange`
- Provides most accurate estimates based on actual asset data
- Confidence level: "high"

**Tier 2: Any Available Asset Data** (Medium Priority)
- If specific asset not found, use any available asset data for the route
- Example: Requesting USDT data but only WETH data available
- Confidence level: "medium"
- Includes note explaining which asset data was used

**Tier 3: Asset-Specific L1/L2 Route Category Averages** (Lowest Priority)
- Use asset-specific route category averages (L2→L1, L2→L2, L1→L2, L1→L1)
- Based on historical performance patterns for specific assets
- Structure: `route_category -> asset_symbol -> amount_range -> settlement_data`
- Confidence level: "low" to "medium"
- Includes note explaining the estimation method and asset used

### Chain Classification Requirements

**L1 Chains**
- ethereum, bnb, solana, avalanche_c, polygon, ronin

**L2 Chains**
- arbitrum, base, optimism, linea, zksync, unichain, zircuit, blast, berachain, ink

**Route Categories**
- L1_to_L1: L1 chain to L1 chain
- L1_to_L2: L1 chain to L2 chain
- L2_to_L1: L2 chain to L1 chain
- L2_to_L2: L2 chain to L2 chain

## Asset Support Requirements

### Supported Assets

**Primary Assets**
- **USDC**: Most widely used stablecoin
- **WETH**: Wrapped Ethereum
- **USDT**: Tether stablecoin

**Additional Assets**
- **cbBTC**: Coinbase Bitcoin
- **xPufETH**: Puffer Finance staked ETH

### Asset Address Mapping

**Chain ID to Chain Name Mapping**
- 42161 = arbitrum
- 1 = ethereum
- 8453 = base
- 10 = optimism
- 137 = polygon
- 56 = bnb
- 59144 = linea
- 324 = zksync
- And 19 additional chains...

**Asset Address to Symbol Mapping**
- Standardized mapping for all supported assets
- Support for new assets through configuration
- Validation of asset addresses

## Security Requirements

### Data Privacy
- No user-identifiable information in settlement calculations
- Aggregate data only (no individual transaction details)
- Secure handling of analytics data

### API Security
- Existing API rate limits apply
- Input validation for all quote parameters
- Protection against injection attacks
- Secure error handling (no sensitive data in error messages)

### Infrastructure Security
- Secure data pipeline connections
- Encrypted data storage
- Access controls for data updates
- Monitoring for suspicious activity

## Monitoring and Alerting Requirements

### Performance Monitoring
- API response time monitoring
- Settlement lookup performance tracking
- Cache hit/miss ratio monitoring
- Throughput and concurrency monitoring

### Data Quality Monitoring
- Data freshness alerts (daily updates)
- Sample size monitoring
- Confidence level tracking
- Data accuracy validation

### Error Monitoring
- API error rate monitoring
- Data pipeline failure alerts
- Cache failure handling
- Graceful degradation monitoring

## Integration Requirements

### Aggregator Integration
- **Li.Fi Integration**: Primary aggregator partner
- **API Compatibility**: Standardized response format
- **Documentation**: Integration guides and examples
- **Support**: Dedicated integration support

### Backward Compatibility
- All existing response fields remain unchanged
- `settlementEstimate` is optional and can be safely ignored
- Existing integrations continue to work without modification
- No breaking changes to current API

## Testing Requirements

### Unit Testing
- Settlement lookup function testing
- Fallback strategy testing
- Data structure validation
- Performance testing (<50ms lookup)

### Integration Testing
- API endpoint testing
- Cache integration testing
- Data pipeline testing
- Aggregator integration testing

### Load Testing
- Aggregator-scale load testing
- Concurrent request handling
- Memory usage optimization
- Response time validation

### Data Quality Testing
- Sample size validation
- Confidence level accuracy
- Data freshness verification
- Fallback strategy validation

## Deployment Requirements

### Environment Setup
- **Development**: Local testing environment
- **Staging**: Pre-production testing
- **Production**: Live API deployment

### Data Pipeline Deployment
- Daily ETL job scheduling
- Data validation checks
- Error handling and retry logic
- Monitoring and alerting setup

### API Deployment
- Blue-green deployment strategy
- Zero-downtime updates
- Rollback capabilities
- Health check endpoints

## Documentation Requirements

### Technical Documentation
- API specification documentation
- Data structure documentation
- Integration guides for aggregators
- Performance optimization guides

### User Documentation
- Settlement time explanation
- Confidence level interpretation
- Fallback strategy explanation
- Best practices for aggregators

### Operational Documentation
- Deployment procedures
- Monitoring and alerting setup
- Troubleshooting guides
- Data pipeline maintenance

## Success Criteria

### Technical Success Metrics
- **API Performance**: 99.9% uptime, <200ms response time
- **Lookup Performance**: <50ms settlement time lookup
- **Data Accuracy**: Settlement times within P25-P75 range 75% of time
- **Coverage**: 100% route coverage with fallback estimates

### Business Success Metrics
- **Aggregator Adoption**: Li.Fi + 2 other major aggregators
- **Route Selection**: 15% increase in Everclear selection rate
- **Customer Satisfaction**: 50% reduction in settlement-time tickets
- **API Adoption**: 90% of quote requests include settlement time data

## Risk Mitigation

### Technical Risks
- **Data Quality**: Insufficient historical data for some routes
  - *Mitigation*: Multi-tier fallback strategy, clear sample size indicators
- **Performance Impact**: Aggregator-scale load affects response times
  - *Mitigation*: Optimized data structures, caching, horizontal scaling
- **Cache Invalidation**: Stale data provides inaccurate estimates
  - *Mitigation*: Daily automated updates, monitoring alerts

### Business Risks
- **Aggregator Standards**: Estimates don't meet aggregator requirements
  - *Mitigation*: Close collaboration with Li.Fi, flexible response format
- **Competitive Transparency**: Showing settlement times may highlight weaknesses
  - *Mitigation*: Focus on routes where we perform well, continuous improvement
- **User Expectations**: Retail users expect estimates to be guarantees
  - *Mitigation*: Clear disclaimers, confidence indicators, education

## Implementation Timeline

### Phase 1: Core Implementation (Weeks 1-4)
- Data pipeline setup and testing
- Asset-specific data structure implementation
- Basic lookup functionality
- Unit testing and validation

### Phase 2: API Enhancement (Weeks 5-8)
- Quote endpoint enhancement
- Fallback strategy implementation
- Performance optimization
- Integration testing

### Phase 3: Aggregator Integration (Weeks 9-12)
- Li.Fi partnership integration
- Load testing and optimization
- Documentation and guides
- Production deployment

### Phase 4: Launch and Scaling (Weeks 13-16)
- Production deployment
- Monitoring and alerting setup
- Additional aggregator partnerships
- Performance monitoring and optimization
