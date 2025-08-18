# PRD: Settlement ETA Endpoint

## Document Information

- **Product**: Everclear Bridge
- **Feature**: Settlement Time ETA Endpoint
- **Document Version**: 1.2
- **Last Updated**: August 7, 2025
- **Owner**: Product Team
- **Stakeholders**: Engineering, Business Development, Customer Success

## Executive Summary

This PRD outlines the development of a Settlement Time ETA (Estimated Time of Arrival) endpoint that will provide users with estimated settlement duration ranges when requesting bridge quotes. This addresses a critical customer pain point identified in our market analysis where settlement time inconsistency is a primary concern for DeFi solvers and institutional customers. **Importantly, this feature will be primarily consumed by bridge aggregators like Li.Fi, who will surface this data to millions of retail users through platforms like Jumper.exchange**, making settlement time transparency crucial for our competitive positioning in the aggregator ecosystem.

## Background & Strategic Context

### Problem Statement

According to our customer research and Porter's Five Forces analysis, **settlement time inconsistency** is a major competitive disadvantage for Everclear:

- **Customer Feedback**: "Settlement times are too inconsistent" - identified as primary market feedback
- **Competitive Pressure**: Across.to offers faster, more reliable settlement times
- **Aggregator Requirements**: Bridge aggregators need settlement time data to provide complete route comparisons
- **Retail User Expectations**: End users making bridging decisions want to understand time vs cost tradeoffs
- **Business Impact**: Unpredictable settlement times reduce our selection rate in aggregator UIs and limit our ability to compete on non-price factors

### Strategic Rationale

- **Improves Aggregator Integration**: Provides data aggregators need to fairly represent our service
- **Increases Retail Adoption**: Better positioning in aggregator UIs leads to higher volume
- **Competitive Transparency**: Allows us to compete on reliability, not just price
- **Enables Customer Choice**: Empowers users to make informed time vs cost decisions
- **Supports Premium Positioning**: Transparent performance data can justify our fee structure

## Product Vision & Goals

### Vision

Enable customers and aggregators to make informed bridging decisions by providing accurate, data-driven settlement time estimates that position Everclear competitively in the broader DeFi ecosystem.

### Primary Goals

1. **Increase Aggregator Adoption**: Provide Li.Fi and other aggregators with settlement time data they need
2. **Improve Retail Conversion**: Better positioning in aggregator UIs through transparent performance metrics
3. **Reduce Customer Uncertainty**: Provide P25-P75 settlement time ranges for all supported routes
4. **Enable Informed Decision-Making**: Allow end users to optimize their bridging choices
5. **Strengthen B2B Relationships**: Meet aggregator requirements for comprehensive route data

### Success Metrics

- **Aggregator Integration**: Li.Fi and 2+ other major aggregators displaying our settlement times
- **Route Selection Rate**: 15% increase in Everclear selection rate on aggregator platforms
- **API Adoption**: 90% of quote requests include settlement time data
- **Customer Satisfaction**: Reduction in settlement-time related support tickets by 50%
- **Accuracy**: Settlement times fall within estimated range 75% of the time

## User Personas & Use Cases

### Primary Persona: Bridge Aggregators (Li.Fi)

**Profile**: Technical teams building bridge aggregation platforms and APIs
**Business Model**: Route users to optimal bridges based on cost, speed, and reliability
**Integration Needs**:

- Comprehensive route performance data
- Standardized API responses
- Real-time settlement estimates

**Use Case 1: Route Comparison API**

`As a bridge aggregator (Li.Fi),
I want to receive settlement time estimates in quote responses,
So that I can provide comprehensive route comparisons to my API consumers.`

**Use Case 2: UI Display Optimization**

`As an aggregator platform,
I want to display settlement time ranges alongside fees,
So that users can make informed decisions between speed and cost.`

### Secondary Persona: Retail Bridge Users (via Jumper.exchange)

**Profile**: DeFi users bridging assets between chains via aggregator interfaces
**Behavior**: Price and time sensitive, compare multiple options before bridging
**Needs**:

- Clear understanding of settlement timeframes
- Ability to choose between fast/expensive vs slow/cheap options
- Transparent performance expectations

**Use Case 3: Informed Route Selection**

`As a retail user on Jumper.exchange,
I want to see estimated settlement times for each bridge option,
So that I can choose the route that best fits my urgency and budget.`

**Use Case 4: Planning Bridge Timing**

`As a DeFi user,
I want to know how long my bridge will take,
So that I can plan my subsequent transactions and avoid being stuck with funds in transit.`

### Tertiary Persona: DeFi Solvers

**Profile**: Technical teams running automated arbitrage and rebalancing operations
**Needs**:

- Predictable settlement times for operational planning
- Ability to compare routes based on time vs. cost tradeoffs
- Integration with existing automated systems

**Use Case 5: Automated Route Selection**

`As a DeFi solver,
I want to programmatically access settlement time estimates,
So that my automated systems can optimize for both cost and settlement speed.`

## Functional Requirements

### Core Requirements

### FR-1: Settlement Time Data Integration

**Priority**: P0 (Must Have)

- System SHALL integrate settlement duration data from existing analytics pipeline
- Data SHALL be updated daily with rolling 30-day historical performance
- Only routes with ≥3 transactions in the last 30 days SHALL be included
- Internal solver and market maker addresses SHALL be filtered from the dataset

### FR-2: Quote Endpoint Enhancement

**Priority**: P0 (Must Have)

- `/routes/quote` endpoint SHALL return settlement time estimates for all valid routes
- Response SHALL include both P25 and P75 percentile values in minutes
- Settlement time data SHALL be returned alongside existing quote information
- API SHALL maintain backward compatibility with existing response structure
- Response format SHALL be optimized for aggregator consumption

### FR-3: Amount and Asset-Based Binning

**Priority**: P0 (Must Have)

- Settlement estimates SHALL vary based on transaction amount bins:
    - $0 - $50,000
    - $50,000 - $100,000
    - $100,000 - $300,000
    - $300,000 - $400,000
    - $400,000 - $500,000
    - $500,000 - $700,000
    - $700,000 - $1,000,000
    - $1,000,000+
- System SHALL select appropriate bin based on user's requested amount
- **Asset-specific data SHALL be prioritized** for more accurate settlement estimates
- Supported assets include: USDC, WETH, USDT, cbBTC, xPufETH
- System SHALL fall back to any available asset data for the route if specific asset data unavailable

### FR-4: Aggregator-Optimized Response Format

**Priority**: P0 (Must Have)

- Settlement time data SHALL include confidence indicators for aggregator algorithms
- Response SHALL include sample size for transparency
- Data SHALL be formatted for easy display in aggregator UIs
- Consistent units (minutes) across all responses

### FR-5: Lookup Performance and Fallback Strategy

**Priority**: P0 (Must Have)

- Settlement time lookup SHALL complete in <50ms
- System SHALL use optimized data structure for O(1) route lookups
- **Multi-tier fallback strategy SHALL be implemented**:
  1. **Exact route with specific asset** (highest priority)
  2. **Any available asset data for the route** (medium priority)
  3. **L1/L2 route category averages** (lowest priority)
- Fallback behavior SHALL be defined for missing route/amount/asset combinations
- Support aggregator-scale request volumes

### API Specification

### Current Endpoint

`POST /routes/quote`

### Request Body (Unchanged)

json

`{
  "originChainId": 42161,
  "destinationChainId": 1,
  "asset": "0xa0b86a33e6fe17d1c55c4acb1e7c5e6e1f3f8c2d",
  "amount": "100000000000000000000000"
}`

### Enhanced Response (Adding settlementEstimate to existing structure)

json

`{
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
    "lastUpdated": "2025-08-07"
  },
  "timestamp": "2025-08-07T10:30:00.000Z"
}`

### New Response Field Details

**settlementEstimate** (object, optional)

- **p25Minutes** (number): 25th percentile settlement time in minutes
- **p75Minutes** (number): 75th percentile settlement time in minutes
- **displayRange** (string): Human-readable range for UI display (e.g., "15-49 minutes")
- **confidenceLevel** (string): Data quality indicator ("high", "medium", "low")
- **dataSource** (string): Source of settlement data ("exact_route_with_asset", "route_with_different_asset", "route_category_average")
- **assetSymbol** (string): Asset symbol used for estimation (e.g., "USDC", "WETH", "USDT")
- **sampleSize** (number): Number of transactions used for calculation
- **note** (string, optional): Additional context for fallback estimates
- **lastUpdated** (string): ISO date when settlement data was last refreshed

### Error Handling

- Missing route data: Return existing quote response without `settlementEstimate` field
- Invalid amount: Return estimate for closest available bin
- Missing asset data: Fall back to any available asset data for the route
- Missing route entirely: Use L1/L2 classification averages
- System errors: Gracefully degrade without affecting existing quote functionality
- Aggregator-friendly error responses with clear messaging

### Backward Compatibility

- All existing response fields remain unchanged
- `settlementEstimate` is optional and will be `null` or omitted for routes without sufficient data
- Existing integrations continue to work without modification
- New field can be safely ignored by clients not using settlement data

## Non-Functional Requirements

### Performance Requirements

- **Response Time**: Quote endpoint response time SHALL remain under 200ms (currently ~150ms)
- **Throughput**: Support aggregator-scale load (10x current volume projected)
- **Availability**: 99.9% uptime maintained (critical for aggregator reliability)

### Data Requirements

- **Freshness**: Settlement data SHALL be updated daily
- **Coverage**: Include all 27 supported chains and 3 primary assets (WETH, USDT, USDC)
- **Retention**: Maintain 30-day rolling window of historical data
- **Transparency**: Provide sample sizes and confidence indicators

### Security Requirements

- **Rate Limiting**: Existing API rate limits SHALL apply with consideration for aggregator needs
- **Data Privacy**: No user-identifiable information in settlement calculations
- **Input Validation**: All quote parameters SHALL be validated before processing

## Technical Implementation

### Data Pipeline

1. **Data Collection**: Leverage existing Goldsky/analytics infrastructure
2. **Data Processing**: Daily ETL job to calculate percentiles and update lookup tables
3. **Data Storage**: Optimized JSON structure for fast lookups (as demonstrated in lookup_example.js)
4. **Cache Strategy**: In-memory caching with daily refresh cycle
5. **Aggregator-Scale Optimization**: Ensure performance at 10x current volume

### Integration Points

- **Existing Quote API**: Extend current `/routes/quote` endpoint response
- **Analytics Pipeline**: Connect to existing settlement tracking system
- **Database**: PostgreSQL for data storage, Redis for caching
- **Aggregator Partnerships**: Direct integration support for Li.Fi and other partners

### Fallback Strategy

The system implements a **three-tier fallback strategy** to ensure comprehensive coverage:

1. **Exact Route with Specific Asset** (Highest Priority)
   - Look for exact match: `fromChain -> toChain -> assetSymbol -> amountRange`
   - Provides most accurate estimates based on actual asset data
   - Confidence level: "high"

2. **Any Available Asset Data** (Medium Priority)
   - If specific asset not found, use any available asset data for the route
   - Example: Requesting USDT data but only WETH data available
   - Confidence level: "medium"
   - Includes note explaining which asset data was used

3. **Asset-Specific L1/L2 Route Category Averages** (Lowest Priority)
   - Use asset-specific route category averages (L2→L1, L2→L2, L1→L2, L1→L1)
   - Based on historical performance patterns for specific assets
   - Structure: `route_category -> asset_symbol -> amount_range -> settlement_data`
   - Confidence level: "low" to "medium"
   - Includes note explaining the estimation method and asset used

- If no data available: Return existing quote response without `settlementEstimate`
- If lookup fails: Log error, return base quote functionality
- Graceful degradation to maintain service availability
- Clear communication to aggregators when data is missing

### Chain ID to Chain Name Mapping

- System SHALL convert chainId values from request to chain names for settlement lookup
- Support all existing chainId mappings (42161 = arbitrum, 1 = ethereum, etc.)
- Asset address SHALL be mapped to standardized asset symbols (USDC, USDT, WETH, cbBTC, xPufETH)
- Asset symbol mapping SHALL be used for asset-specific settlement time lookup

## User Experience

### Aggregator Integration Experience

javascript

`*// Li.Fi integration example*
const everclearQuote = await fetch('/routes/quote', {
  method: 'POST',
  body: JSON.stringify({
    originChainId: 42161,  *// Arbitrum*
    destinationChainId: 1, *// Ethereum*
    asset: "0xa0b86a33e6fe17d1c55c4acb1e7c5e6e1f3f8c2d", *// USDC*
    amount: "100000000000000000000000" *// 100k USDC*
  })
});

const response = await everclearQuote.json();
const { fees, settlementEstimate } = response;

*// Aggregator displays in UI:// "Everclear: $90 fee, 15-49 min settlement (based on 180 recent transactions)"*
if (settlementEstimate) {
  displaySettlementTime(settlementEstimate.displayRange, settlementEstimate.sampleSize);
}`

### Retail User Experience (via Jumper.exchange)

- Settlement time displayed prominently alongside fees
- Clear visualization of time vs cost tradeoffs
- Confidence indicators help users understand estimate reliability
- Consistent formatting across all bridge options

### Documentation Updates

- Update API documentation with new response fields
- Provide integration examples for aggregators
- Include best practices for displaying settlement estimates to end users
- Partner integration guides for Li.Fi and other aggregators

## Partnership Integration

### Li.Fi Integration Requirements

- **API Compatibility**: Ensure response format aligns with Li.Fi's aggregation standards
- **Performance Standards**: Meet Li.Fi's latency requirements for real-time quoting
- **Data Quality**: Provide reliability metrics Li.Fi needs for route ranking
- **Support**: Dedicated integration support for smooth rollout

### Retail User Display Standards

- **Clarity**: Settlement ranges must be easily understood by non-technical users
- **Consistency**: Format should match other bridges in aggregator UIs
- **Transparency**: Sample size and confidence indicators build user trust
- **Actionability**: Clear enough for users to make informed decisions

## Risks & Mitigation

### Technical Risks

- **Data Quality**: Insufficient historical data for some routes
    - *Mitigation*: Clearly communicate sample sizes; exclude routes with <3 samples
- **Performance Impact**: Aggregator-scale load affects quote response times
    - *Mitigation*: Optimize lookup with pre-computed data structures; horizontal scaling
- **Cache Invalidation**: Stale data provides inaccurate estimates to millions of users
    - *Mitigation*: Daily automated updates with monitoring alerts; real-time validation

### Business Risks

- **Aggregator Standards**: Our estimates don't meet aggregator display requirements
    - *Mitigation*: Close collaboration with Li.Fi during development; flexible response format
- **Competitive Transparency**: Showing settlement times may highlight weaknesses
    - *Mitigation*: Focus on routes where we perform well; continuous improvement efforts
- **User Expectations**: Retail users expect estimates to be guarantees
    - *Mitigation*: Clear disclaimers; education through aggregator partners

### Partnership Risks

- **Integration Delays**: Li.Fi integration takes longer than expected
    - *Mitigation*: Parallel development with multiple aggregators; phased rollout plan
- **Aggregator Requirements Change**: Standards evolve during development
    - *Mitigation*: Flexible API design; regular stakeholder communication

## Success Criteria & Metrics

### Launch Criteria

- [ ]  API returns settlement estimates for >95% of active routes
- [ ]  Li.Fi integration completed and tested
- [ ]  Response time remains under 200ms at aggregator scale
- [ ]  Documentation and integration guides published
- [ ]  Jumper.exchange UI displaying Everclear settlement times
- [ ]  Backward compatibility maintained for all existing integrations

### Post-Launch KPIs

- **Aggregator Adoption**: Li.Fi + 2 other major aggregators displaying our settlement times
- **Route Selection**: 15% increase in Everclear selection rate on aggregator platforms
- **API Performance**: 99.9% uptime maintained under aggregator load
- **Accuracy**: Actual settlement times within P25-P75 range 75% of time
- **User Satisfaction**: Positive feedback from aggregator partners on data quality

### Long-term Goals

- Integration with all major bridge aggregators
- Real-time settlement predictions using machine learning
- Dynamic pricing based on congestion and settlement time predictions
- Industry standard for settlement time transparency

## Timeline & Dependencies

### Phase 1: Core Implementation

- Data pipeline setup and testing
- Quote endpoint enhancement with backward-compatible response format
- Chain ID to chain name mapping implementation
- Basic lookup functionality

### Phase 2: Aggregator Integration

- Li.Fi partnership integration and testing
- Performance optimization for aggregator-scale load
- Comprehensive testing with staging data

### Phase 3: Launch & Scaling

- Production deployment
- Li.Fi/Jumper.exchange go-live
- Performance monitoring and optimization
- Additional aggregator partnerships

### Dependencies

- **Li.Fi Partnership**: Technical requirements and integration timeline
- **Analytics Team**: Historical data extraction and validation
- **Infrastructure**: Cache setup and scaling for aggregator load
- **Business Development**: Aggregator relationship management

## Appendix

### Data Structure Reference

The system uses optimized JSON structures for fast lookups:

- **Asset-Specific Data**: `settlement_duration_percentiles_with_asset.json`
  - Structure: `origin_chain -> destination_chain -> asset_symbol -> amount_range -> settlement_data`
  - Supports: USDC, WETH, USDT, cbBTC, xPufETH
  - Provides most accurate estimates

- **Asset-Specific Route Category Averages**: `route_category_averages.json`
  - Asset-specific fallback data for unknown routes
  - Structure: `route_category -> asset_symbol -> amount_range -> settlement_data`
  - Categories: L2→L1, L2→L2, L1→L2, L1→L1
  - Supports: USDC, WETH, USDT, cbBTC, xPufETH
  - Used when no asset-specific data available

- **Implementation**: `enhanced_lookup_example.js` and `asset_specific_lookup_example.js`
  - O(1) lookup performance
  - Multi-tier fallback strategy
  - Comprehensive error handling

**Files:**

[lookup_example.jsx](attachment:1af73fca-d357-4075-8c4d-b3a985543a8f:lookup_example.jsx)

[settlement_duration_percentiles.json](attachment:32c9e8d2-48d1-4d11-96c5-dfa956803d8d:settlement_duration_percentiles.json)

### API Migration Guide

Existing integrations require no changes. New `settlementEstimate` field can be optionally consumed by clients wanting settlement time data.

### Competitive Analysis

This feature directly addresses the "settlement time inconsistency" weakness identified in our Porter's Five Forces analysis, particularly against Across.to's superior performance reputation. More importantly, it enables fair competition in aggregator platforms where transparency is key to user selection.

### Customer Validation

Feature aligns with aggregator needs for comprehensive route data and retail user demands for transparent performance metrics. Addresses Li.Fi's specific requirement for settlement time data in their route comparison algorithms.

### Partnership Impact

Success of this feature directly impacts our relationship with Li.Fi and potential for expansion to other major aggregators (1inch, Paraswap, Socket, etc.), representing significant growth opportunity in retail bridge volume.