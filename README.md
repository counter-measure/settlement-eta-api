# Settlement Time ETA API

A comprehensive settlement time estimation system for bridge quotes, providing asset-specific settlement duration ranges with intelligent fallback strategies.

## 🚀 Overview

The Settlement Time ETA feature addresses critical customer pain points around settlement time inconsistency in bridge operations. It provides estimated settlement duration ranges for bridge quotes, enabling informed decision-making for bridge users and aggregators.

### Key Features

- **Asset-Specific Estimates**: Settlement times based on the specific asset being bridged
- **Multi-Tier Fallback Strategy**: Comprehensive coverage for all routes
- **High Performance**: <50ms lookup times with O(1) complexity
- **Aggregator Optimized**: Designed for Li.Fi and other bridge aggregators
- **100% Route Coverage**: Fallback estimates for unknown routes

## 📁 Project Structure

```
settlement-eta-api/
├── README.md                           # This file
├── .gitignore                          # Git ignore rules
├── prd.md                             # Product Requirements Document
├── user_stories.md                     # User stories and acceptance criteria
├── technical_requirements.md           # Technical specifications
├── settlement_duration_percentiles_final.csv
├── settlement_duration_percentiles_with_asset.csv
├── settlement_duration_percentiles_with_asset.json
├── route_category_averages.json        # Asset-specific fallback data
├── chain_classification.json           # L1/L2 chain classification
└── asset_specific_lookup_example.js   # Implementation example
```

## 🏗️ Architecture

### Data Flow

```
Analytics Pipeline (Goldsky) → ETL Jobs → JSON Storage → API Layer → Cache (Redis)
```

### Fallback Strategy

1. **Exact Route with Asset** (Highest Priority)
   - Look for exact match: `fromChain -> toChain -> assetSymbol -> amountRange`
   - Provides most accurate estimates based on actual asset data

2. **Any Available Asset Data** (Medium Priority)
   - If specific asset not found, use any available asset data for the route
   - Example: Requesting USDT data but only WETH data available

3. **Asset-Specific L1/L2 Route Category Averages** (Lowest Priority)
   - Use route category averages (L2→L1, L2→L2, L1→L2, L1→L1)
   - Based on historical performance patterns for specific assets

## 📊 Data Coverage

### Supported Assets
- **USDC**: Most widely used stablecoin
- **WETH**: Wrapped Ethereum
- **USDT**: Tether stablecoin
- **cbBTC**: Coinbase Bitcoin
- **xPufETH**: Puffer Finance staked ETH

### Supported Chains
- **L1 Chains**: ethereum, bnb, solana, avalanche_c, polygon, ronin
- **L2 Chains**: arbitrum, base, optimism, linea, zksync, unichain, zircuit, blast, berachain, ink

### Amount Ranges
- $0 - $50,000
- $50,000 - $100,000
- $100,000 - $300,000
- $300,000 - $400,000
- $400,000 - $500,000
- $500,000 - $700,000
- $700,000 - $1,000,000
- $1,000,000+

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- Redis (for caching)
- Access to analytics pipeline data

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd settlement-eta-api

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Running the Example

```bash
# Run the asset-specific lookup example
node asset_specific_lookup_example.js
```

### API Usage

```javascript
// Example API request
const response = await fetch('/routes/quote', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    originChainId: 42161,        // Arbitrum
    destinationChainId: 1,        // Ethereum
    asset: "0xa0b86a33e6fe17d1c55c4acb1e7c5e6e1f3f8c2d", // USDC
    amount: "100000000000000000000000" // 100k USDC
  })
});

const data = await response.json();
console.log('Settlement Estimate:', data.settlementEstimate);
```

### Example Response

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
  }
}
```

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
API_PORT=3000
API_HOST=localhost

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# Data Pipeline Configuration
ANALYTICS_PIPELINE_URL=your_analytics_pipeline_url
ETL_SCHEDULE="0 2 * * *"  # Daily at 2 AM

# Monitoring Configuration
MONITORING_ENABLED=true
ALERT_WEBHOOK_URL=your_webhook_url
```

### Data Sources

The system uses the following data files:

- `settlement_duration_percentiles_with_asset.json`: Asset-specific settlement data
- `route_category_averages.json`: Fallback data for unknown routes
- `chain_classification.json`: L1/L2 chain classification

## 📈 Performance

### Response Times
- **Settlement Lookup**: <50ms (O(1) complexity)
- **API Response**: <200ms (currently ~150ms)
- **Cache Performance**: In-memory caching with daily refresh

### Scalability
- **Concurrent Requests**: Support aggregator-scale load
- **Data Volume**: Handle 27 chains × 5 assets × 8 amount ranges
- **Uptime**: 99.9% availability

## 🧪 Testing

### Unit Tests

```bash
# Run unit tests
npm test

# Run specific test suite
npm test -- --grep "settlement lookup"
```

### Integration Tests

```bash
# Run integration tests
npm run test:integration

# Test API endpoints
npm run test:api
```

### Load Tests

```bash
# Run load tests
npm run test:load

# Test aggregator-scale load
npm run test:load:aggregator
```

## 📊 Monitoring

### Key Metrics

- **API Response Time**: Target <200ms
- **Settlement Lookup Time**: Target <50ms
- **Data Freshness**: Daily updates
- **Cache Hit Ratio**: Target >95%
- **Error Rate**: Target <0.1%

### Alerts

- Data pipeline failures
- API response time degradation
- Cache miss rate increases
- Data freshness issues

## 🔄 Data Pipeline

### Daily ETL Process

1. **Data Collection**: Extract settlement data from analytics pipeline
2. **Data Processing**: Calculate P25/P75 percentiles for each route/asset/amount
3. **Data Validation**: Filter routes with <3 transactions, validate sample sizes
4. **Data Storage**: Update JSON files with new settlement data
5. **Cache Refresh**: Update Redis cache with fresh data

### Data Quality Checks

- Sample size validation (minimum 3 transactions)
- Confidence level calculation
- Data freshness monitoring
- Error handling for missing data

## 🤝 Integration

### Aggregator Integration

The system is designed for easy integration with bridge aggregators:

- **Li.Fi**: Primary aggregator partner
- **Standardized API**: Compatible with aggregator requirements
- **Documentation**: Integration guides and examples
- **Support**: Dedicated integration support

### Backward Compatibility

- All existing response fields remain unchanged
- `settlementEstimate` is optional and can be safely ignored
- Existing integrations continue to work without modification

## 📚 Documentation

### Related Documents

- [Product Requirements Document](prd.md) - Business requirements and specifications
- [User Stories](user_stories.md) - User stories and acceptance criteria
- [Technical Requirements](technical_requirements.md) - Technical specifications

### API Documentation

- **Endpoint**: `POST /routes/quote`
- **Request Format**: JSON with chain IDs and asset address
- **Response Format**: Enhanced JSON with settlement estimates
- **Error Handling**: Graceful degradation with clear messaging

## 🚀 Deployment

### Environment Setup

```bash
# Development
npm run dev

# Staging
npm run start:staging

# Production
npm run start:production
```

### Docker Deployment

```bash
# Build image
docker build -t settlement-eta-api .

# Run container
docker run -p 3000:3000 settlement-eta-api
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: settlement-eta-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: settlement-eta-api
  template:
    metadata:
      labels:
        app: settlement-eta-api
    spec:
      containers:
      - name: settlement-eta-api
        image: settlement-eta-api:latest
        ports:
        - containerPort: 3000
```

## 🤝 Contributing

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards

- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation for API changes
- Ensure backward compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Check the docs folder for detailed guides
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions for questions and ideas

### Contact

- **Technical Support**: tech-support@everclear.com
- **Business Inquiries**: partnerships@everclear.com
- **Security Issues**: security@everclear.com

## 🎯 Roadmap

### Phase 1: Core Implementation (Weeks 1-4)
- [x] Data pipeline setup and testing
- [x] Asset-specific data structure implementation
- [x] Basic lookup functionality
- [x] Unit testing and validation

### Phase 2: API Enhancement (Weeks 5-8)
- [ ] Quote endpoint enhancement
- [ ] Fallback strategy implementation
- [ ] Performance optimization
- [ ] Integration testing

### Phase 3: Aggregator Integration (Weeks 9-12)
- [ ] Li.Fi partnership integration
- [ ] Load testing and optimization
- [ ] Documentation and guides
- [ ] Production deployment

### Phase 4: Launch and Scaling (Weeks 13-16)
- [ ] Production deployment
- [ ] Monitoring and alerting setup
- [ ] Additional aggregator partnerships
- [ ] Performance monitoring and optimization

## 📊 Success Metrics

### Technical Metrics
- **API Performance**: 99.9% uptime, <200ms response time
- **Data Accuracy**: Settlement times within P25-P75 range 75% of time
- **Coverage**: 100% route coverage with fallback estimates

### Business Metrics
- **Aggregator Adoption**: Li.Fi + 2 other major aggregators
- **Route Selection**: 15% increase in Everclear selection rate
- **Customer Satisfaction**: 50% reduction in settlement-time tickets

---

**Built with ❤️ by the Everclear Team**
