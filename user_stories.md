# User Stories: Settlement Time ETA Feature

## Document Information

- **Feature**: Settlement Time ETA Endpoint
- **Document Version**: 1.0
- **Last Updated**: January 27, 2025
- **Related Documents**: PRD.md, asset_specific_lookup_example.js

## Overview

This document contains user stories for the Settlement Time ETA feature, which provides estimated settlement duration ranges for bridge quotes. The feature addresses critical customer pain points around settlement time inconsistency and enables informed decision-making for bridge users.

## User Personas

### Primary Persona: Bridge Aggregators (Li.Fi)
**Profile**: Technical teams building bridge aggregation platforms and APIs
**Business Model**: Route users to optimal bridges based on cost, speed, and reliability
**Integration Needs**: Comprehensive route performance data, standardized API responses, real-time settlement estimates

### Secondary Persona: Retail Bridge Users (via Jumper.exchange)
**Profile**: DeFi users bridging assets between chains via aggregator interfaces
**Behavior**: Price and time sensitive, compare multiple options before bridging
**Needs**: Clear understanding of settlement timeframes, ability to choose between fast/expensive vs slow/cheap options

### Tertiary Persona: DeFi Solvers
**Profile**: Technical teams running automated arbitrage and rebalancing operations
**Needs**: Predictable settlement times for operational planning, ability to compare routes based on time vs. cost tradeoffs

## User Stories

### Epic 1: Core Settlement Time Data Integration

#### Story 1.1: Historical Data Processing
**As a** data engineer  
**I want to** process 30-day rolling settlement duration data  
**So that** I can provide accurate settlement time estimates based on recent performance

**Acceptance Criteria:**
- [ ] System processes settlement data from existing analytics pipeline
- [ ] Data is updated daily with rolling 30-day window
- [ ] Only routes with ≥3 transactions in last 30 days are included
- [ ] Internal solver and market maker addresses are filtered out
- [ ] Asset-specific data is prioritized for accuracy

**Definition of Done:**
- Data pipeline processes settlement_duration_percentiles_with_asset.csv
- Daily ETL job updates lookup tables
- Data quality checks pass (sample sizes, confidence levels)

---

#### Story 1.2: Asset-Specific Data Structure
**As a** developer  
**I want to** store settlement data with asset-specific granularity  
**So that** I can provide more accurate estimates based on the specific asset being bridged

**Acceptance Criteria:**
- [ ] Data structure supports: `origin_chain -> destination_chain -> asset_symbol -> amount_range -> settlement_data`
- [ ] Supports all major assets: USDC, WETH, USDT, cbBTC, xPufETH
- [ ] Amount ranges: $0-50k, $50k-100k, $100k-300k, $300k-400k, $400k-500k, $500k-700k, $700k-1M, $1M+
- [ ] O(1) lookup performance maintained
- [ ] Fallback strategy for missing asset data

**Definition of Done:**
- settlement_duration_percentiles_with_asset.json created
- Lookup functions handle asset-specific queries
- Performance tests show <50ms response times

---

### Epic 2: API Enhancement

#### Story 2.1: Quote Endpoint Enhancement
**As a** bridge aggregator (Li.Fi)  
**I want to** receive settlement time estimates in quote responses  
**So that** I can provide comprehensive route comparisons to my API consumers

**Acceptance Criteria:**
- [ ] `/routes/quote` endpoint returns settlement time estimates for all valid routes
- [ ] Response includes both P25 and P75 percentile values in minutes
- [ ] Settlement time data returned alongside existing quote information
- [ ] API maintains backward compatibility with existing response structure
- [ ] Response format optimized for aggregator consumption

**Definition of Done:**
- Enhanced API response includes settlementEstimate object
- All existing integrations continue to work without modification
- Response time remains under 200ms

---

#### Story 2.2: Asset-Specific Settlement Estimates
**As a** retail bridge user  
**I want to** see settlement time estimates specific to the asset I'm bridging  
**So that** I can make informed decisions about which bridge to use

**Acceptance Criteria:**
- [ ] Settlement estimates vary based on the specific asset (USDC, WETH, USDT, etc.)
- [ ] Estimates include confidence indicators (high, medium, low)
- [ ] Data source is clearly indicated (exact_route_with_asset, route_with_different_asset, route_category_average)
- [ ] Sample size provided for transparency
- [ ] Human-readable display range included

**Definition of Done:**
- API response includes assetSymbol field
- Confidence levels accurately reflect data quality
- Sample sizes help users understand estimate reliability

---

### Epic 3: Fallback Strategy Implementation

#### Story 3.1: Multi-Tier Fallback System
**As a** bridge aggregator  
**I want to** receive settlement estimates for all possible routes  
**So that** I can provide complete route comparisons even for low-volume routes

**Acceptance Criteria:**
- [ ] Three-tier fallback strategy implemented:
  1. Exact route with specific asset (highest priority)
  2. Any available asset data for the route (medium priority)
  3. Asset-specific L1/L2 route category averages (lowest priority)
- [ ] 100% route coverage achieved
- [ ] Clear indication of data source and confidence level
- [ ] Graceful degradation when no data available

**Definition of Done:**
- All 27 supported chains have settlement estimates
- Fallback strategy provides reasonable estimates for unknown routes
- API never returns null for valid route requests

---

#### Story 3.2: Asset-Specific Route Category Averages
**As a** DeFi solver  
**I want to** receive asset-specific fallback estimates  
**So that** I can make more accurate operational decisions

**Acceptance Criteria:**
- [ ] Route category averages include asset-specific data
- [ ] Structure: `route_category -> asset_symbol -> amount_range -> settlement_data`
- [ ] Supports all major assets in each route category
- [ ] Weighted averages based on sample sizes
- [ ] Clear documentation of calculation method

**Definition of Done:**
- route_category_averages.json includes asset-specific data
- All route categories (L1→L1, L1→L2, L2→L1, L2→L2) have asset coverage
- Calculation method documented and transparent

---

### Epic 4: Performance and Reliability

#### Story 4.1: Fast Lookup Performance
**As a** bridge aggregator  
**I want to** receive settlement estimates quickly  
**So that** I can provide real-time route comparisons without delays

**Acceptance Criteria:**
- [ ] Settlement time lookup completes in <50ms
- [ ] O(1) route lookups using optimized data structure
- [ ] Support for aggregator-scale request volumes (10x current volume)
- [ ] In-memory caching with daily refresh cycle

**Definition of Done:**
- Performance tests show <50ms response times
- Load testing validates aggregator-scale throughput
- Cache strategy implemented and tested

---

#### Story 4.2: Data Freshness and Reliability
**As a** retail bridge user  
**I want to** see up-to-date settlement time estimates  
**So that** I can trust the estimates reflect current network conditions

**Acceptance Criteria:**
- [ ] Settlement data updated daily
- [ ] Rolling 30-day window maintained
- [ ] Data freshness indicators in API response
- [ ] Monitoring alerts for stale data
- [ ] Graceful error handling for data pipeline failures

**Definition of Done:**
- Daily automated updates working
- Monitoring dashboard shows data freshness
- Error handling prevents service degradation

---

### Epic 5: User Experience and Integration

#### Story 5.1: Aggregator Integration Experience
**As a** bridge aggregator (Li.Fi)  
**I want to** easily integrate settlement time data into my platform  
**So that** I can provide comprehensive route comparisons to my users

**Acceptance Criteria:**
- [ ] Standardized API response format
- [ ] Clear documentation and integration examples
- [ ] Backward compatibility maintained
- [ ] Error handling for missing data
- [ ] Support for all major aggregators

**Definition of Done:**
- Integration documentation published
- Li.Fi integration completed and tested
- Error handling prevents service disruption

---

#### Story 5.2: Retail User Display
**As a** retail bridge user (via Jumper.exchange)  
**I want to** see settlement time ranges alongside fees  
**So that** I can make informed decisions between speed and cost

**Acceptance Criteria:**
- [ ] Settlement time displayed prominently in UI
- [ ] Clear visualization of time vs cost tradeoffs
- [ ] Confidence indicators help users understand estimate reliability
- [ ] Consistent formatting across all bridge options
- [ ] Human-readable display ranges (e.g., "15-49 minutes")

**Definition of Done:**
- Jumper.exchange UI displaying settlement times
- User testing shows improved decision-making
- Consistent formatting across aggregator platforms

---

#### Story 5.3: DeFi Solver Integration
**As a** DeFi solver  
**I want to** programmatically access settlement time estimates  
**So that** my automated systems can optimize for both cost and settlement speed

**Acceptance Criteria:**
- [ ] API provides machine-readable settlement data
- [ ] Confidence levels help with risk assessment
- [ ] Asset-specific data enables better optimization
- [ ] Sample sizes help with statistical analysis
- [ ] Integration examples for automated systems

**Definition of Done:**
- API documentation includes solver integration examples
- Machine-readable response format validated
- Automated system integration tested

---

### Epic 6: Business Impact and Success Metrics

#### Story 6.1: Aggregator Adoption
**As a** business development team  
**I want to** see Li.Fi and other aggregators displaying our settlement times  
**So that** we can increase our selection rate in aggregator UIs

**Acceptance Criteria:**
- [ ] Li.Fi integration completed and live
- [ ] 2+ other major aggregators displaying our settlement times
- [ ] 15% increase in Everclear selection rate on aggregator platforms
- [ ] Positive feedback from aggregator partners

**Definition of Done:**
- Li.Fi integration live in production
- Additional aggregator partnerships secured
- Selection rate metrics showing improvement

---

#### Story 6.2: Customer Satisfaction
**As a** customer success team  
**I want to** see reduced settlement-time related support tickets  
**So that** we can improve overall customer satisfaction

**Acceptance Criteria:**
- [ ] 50% reduction in settlement-time related support tickets
- [ ] Positive feedback from retail users
- [ ] Improved customer satisfaction scores
- [ ] Clear communication about estimate reliability

**Definition of Done:**
- Support ticket metrics showing improvement
- Customer feedback surveys completed
- Communication strategy implemented

---

#### Story 6.3: Competitive Positioning
**As a** product team  
**I want to** address the "settlement time inconsistency" weakness  
**So that** we can compete more effectively against Across.to and other bridges

**Acceptance Criteria:**
- [ ] Settlement time transparency improves competitive positioning
- [ ] Actual settlement times within P25-P75 range 75% of time
- [ ] Industry recognition for settlement time transparency
- [ ] Improved market share in aggregator platforms

**Definition of Done:**
- Competitive analysis shows improved positioning
- Accuracy metrics meet targets
- Market share metrics showing growth

---

## Success Metrics

### Technical Metrics
- **API Performance**: 99.9% uptime, <200ms response time
- **Data Accuracy**: Settlement times within P25-P75 range 75% of time
- **Coverage**: 100% route coverage with fallback estimates
- **Freshness**: Daily data updates with monitoring

### Business Metrics
- **Aggregator Adoption**: Li.Fi + 2 other major aggregators
- **Route Selection**: 15% increase in Everclear selection rate
- **Customer Satisfaction**: 50% reduction in settlement-time tickets
- **Market Share**: Improved competitive positioning

### User Experience Metrics
- **API Adoption**: 90% of quote requests include settlement time data
- **User Understanding**: Clear comprehension of settlement estimates
- **Decision Quality**: Improved route selection based on time vs cost

## Definition of Ready

A user story is ready for development when:
- [ ] Acceptance criteria are clearly defined
- [ ] Technical requirements are understood
- [ ] Dependencies are identified
- [ ] Success metrics are measurable
- [ ] User personas are clearly defined
- [ ] Related documentation is available

## Definition of Done

A user story is complete when:
- [ ] All acceptance criteria are met
- [ ] Code is reviewed and tested
- [ ] Documentation is updated
- [ ] Performance requirements are validated
- [ ] Integration testing is complete
- [ ] Success metrics are tracked
- [ ] User feedback is collected
