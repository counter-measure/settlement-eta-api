// Enhanced lookup function for asset-specific settlement duration data
const settlementDataWithAsset = require('./settlement_duration_percentiles_with_asset.json');
const chainClassification = require('./chain_classification.json');
const routeCategoryAverages = require('./route_category_averages.json');

/**
 * Enhanced lookup function with asset-specific data and fallback strategy
 * @param {string} fromChain - Source chain name
 * @param {string} toChain - Destination chain name  
 * @param {string} assetSymbol - Asset symbol (USDC, WETH, USDT, etc.)
 * @param {number} amountUsd - Amount in USD
 * @returns {object|null} Settlement duration data or null if not found
 */
function lookupSettlementDurationWithAsset(fromChain, toChain, assetSymbol, amountUsd) {
  try {
    // First, try to find exact route data with asset
    const exactData = lookupExactRouteWithAsset(fromChain, toChain, assetSymbol, amountUsd);
    if (exactData) {
      return {
        ...exactData,
        dataSource: 'exact_route_with_asset',
        confidence: 'high',
        assetSymbol: assetSymbol
      };
    }

    // If no exact data, try to find any asset data for this route
    const anyAssetData = lookupAnyAssetRoute(fromChain, toChain, amountUsd);
    if (anyAssetData) {
      return {
        ...anyAssetData.data,
        dataSource: 'route_with_different_asset',
        confidence: 'medium',
        note: `Estimated using ${anyAssetData.assetSymbol} data for ${fromChain}->${toChain}`,
        assetSymbol: assetSymbol
      };
    }

    // If no asset-specific data, use L1/L2 classification fallback
    const fallbackData = lookupFallbackRoute(fromChain, toChain, assetSymbol, amountUsd);
    if (fallbackData) {
      return {
        ...fallbackData,
        dataSource: 'route_category_average',
        confidence: fallbackData.confidence,
        note: fallbackData.note || `Estimated based on ${fallbackData.description}`,
        assetSymbol: assetSymbol
      };
    }

    return null;
  } catch (error) {
    console.error('Error in asset-specific lookup:', error);
    return null;
  }
}

/**
 * Lookup exact route data with specific asset from settlement_duration_percentiles_with_asset.json
 */
function lookupExactRouteWithAsset(fromChain, toChain, assetSymbol, amountUsd) {
  const chainData = settlementDataWithAsset[fromChain];
  if (!chainData) return null;
  
  const destinationData = chainData[toChain];
  if (!destinationData) return null;
  
  const assetData = destinationData[assetSymbol];
  if (!assetData) return null;
  
  // Find the appropriate amount range
  const amountRanges = Object.keys(assetData);
  
  for (const range of amountRanges) {
    const [min, max] = parseAmountRange(range);
    
    if (amountUsd >= min && (max === null || amountUsd < max)) {
      return assetData[range];
    }
  }
  
  return null;
}

/**
 * Lookup any asset data for the route (fallback when specific asset not found)
 */
function lookupAnyAssetRoute(fromChain, toChain, amountUsd) {
  const chainData = settlementDataWithAsset[fromChain];
  if (!chainData) return null;
  
  const destinationData = chainData[toChain];
  if (!destinationData) return null;
  
  // Try to find any asset with data for this amount range
  const assets = Object.keys(destinationData);
  
  for (const assetSymbol of assets) {
    const assetData = destinationData[assetSymbol];
    const amountRanges = Object.keys(assetData);
    
    for (const range of amountRanges) {
      const [min, max] = parseAmountRange(range);
      
      if (amountUsd >= min && (max === null || amountUsd < max)) {
        return {
          data: assetData[range],
          assetSymbol: assetSymbol
        };
      }
    }
  }
  
  return null;
}

/**
 * Lookup fallback data based on L1/L2 classification with asset-specific data
 */
function lookupFallbackRoute(fromChain, toChain, assetSymbol, amountUsd) {
  // Determine chain types
  const fromChainType = getChainType(fromChain);
  const toChainType = getChainType(toChain);
  
  if (!fromChainType || !toChainType) {
    return null;
  }
  
  // Determine route category
  const routeCategory = `${fromChainType}_to_${toChainType}`;
  const categoryData = routeCategoryAverages[routeCategory];
  
  if (!categoryData) {
    return null;
  }
  
  // First try to find asset-specific data in the category
  const assetData = categoryData[assetSymbol];
  if (assetData) {
    // Find appropriate amount range for this asset
    const amountRanges = Object.keys(assetData);
    
    for (const range of amountRanges) {
      const [min, max] = parseAmountRange(range);
      
      if (amountUsd >= min && (max === null || amountUsd < max)) {
        return assetData[range];
      }
    }
    
    // If no exact range match, return the closest available range for this asset
    return findClosestAmountRange(assetData, amountUsd);
  }
  
  // If no asset-specific data, try any available asset in the category
  const availableAssets = Object.keys(categoryData).filter(key => key !== 'metadata');
  
  for (const availableAsset of availableAssets) {
    const availableAssetData = categoryData[availableAsset];
    const amountRanges = Object.keys(availableAssetData);
    
    for (const range of amountRanges) {
      const [min, max] = parseAmountRange(range);
      
      if (amountUsd >= min && (max === null || amountUsd < max)) {
        return {
          ...availableAssetData[range],
          note: `Estimated using ${availableAsset} category data for ${fromChain}->${toChain}`
        };
      }
    }
  }
  
  return null;
}

/**
 * Get chain type (L1 or L2)
 */
function getChainType(chainName) {
  if (chainClassification.L1.includes(chainName)) {
    return 'L1';
  } else if (chainClassification.L2.includes(chainName)) {
    return 'L2';
  }
  return null;
}

/**
 * Parse amount range string (e.g., "0-50000", "1000000+")
 */
function parseAmountRange(range) {
  if (range.endsWith('+')) {
    const min = parseInt(range.slice(0, -1));
    return [min, null]; // null means no upper limit
  }
  
  const [min, max] = range.split('-').map(Number);
  return [min, max];
}

/**
 * Find the closest amount range when exact match is not available
 */
function findClosestAmountRange(categoryData, amountUsd) {
  const amountRanges = Object.keys(categoryData).filter(key => key !== 'metadata');
  
  if (amountRanges.length === 0) return null;
  
  // Sort ranges by minimum amount
  const sortedRanges = amountRanges.sort((a, b) => {
    const [minA] = parseAmountRange(a);
    const [minB] = parseAmountRange(b);
    return minA - minB;
  });
  
  // Find the range where amountUsd falls
  for (const range of sortedRanges) {
    const [min, max] = parseAmountRange(range);
    if (amountUsd >= min && (max === null || amountUsd < max)) {
      return categoryData[range];
    }
  }
  
  // If amount is higher than all ranges, return the highest range
  const highestRange = sortedRanges[sortedRanges.length - 1];
  return categoryData[highestRange];
}

// Example usage:
console.log('Asset-specific lookup examples:');

// Example 1: Known route with specific asset (should use exact data)
const result1 = lookupSettlementDurationWithAsset('arbitrum', 'ethereum', 'WETH', 25000);
console.log('arbitrum -> ethereum, WETH, $25,000 (known route):', result1);
if (result1) {
  console.log(`  P25: ${result1.settlement_duration_minutes_p25}, P75: ${result1.settlement_duration_minutes_p75}, Source: ${result1.dataSource}`);
}

// Example 2: Known route but different asset (should use any asset data)
const result2 = lookupSettlementDurationWithAsset('arbitrum', 'ethereum', 'USDT', 25000);
console.log('arbitrum -> ethereum, USDT, $25,000 (different asset):', result2);
if (result2) {
  console.log(`  P25: ${result2.settlement_duration_minutes_p25}, P75: ${result2.settlement_duration_minutes_p75}, Source: ${result2.dataSource}`);
}

// Example 3: Unknown route (should use L2->L1 fallback)
const result3 = lookupSettlementDurationWithAsset('zksync', 'bnb', 'USDC', 50000);
console.log('zksync -> bnb, USDC, $50,000 (unknown route, L2->L1 fallback):', result3);
if (result3) {
  console.log(`  P25: ${result3.settlement_duration_minutes_p25}, P75: ${result3.settlement_duration_minutes_p75}, Source: ${result3.dataSource}`);
}

// Example 4: Unknown route (should use L1->L1 fallback)
const result4 = lookupSettlementDurationWithAsset('polygon', 'solana', 'WETH', 100000);
console.log('polygon -> solana, WETH, $100,000 (unknown route, L1->L1 fallback):', result4);
if (result4) {
  console.log(`  P25: ${result4.settlement_duration_minutes_p25}, P75: ${result4.settlement_duration_minutes_p75}, Source: ${result4.dataSource}`);
}

// Example 5: Non-existent chains (should return null)
const result5 = lookupSettlementDurationWithAsset('nonexistent', 'unknown', 'USDC', 10000);
console.log('nonexistent -> unknown, USDC, $10,000 (invalid chains):', result5);

// Example 6: Unknown route (should use L2->L1 fallback)
const result6 = lookupSettlementDurationWithAsset('berachain', 'arbitrum', 'USDC', 10000);
console.log('berachain -> arbitrum, USDC, $10,000 (unknown route, L2->L1 fallback):', result6);
if (result6) {
  console.log(`  P25: ${result6.settlement_duration_minutes_p25}, P75: ${result6.settlement_duration_minutes_p75}, Source: ${result6.dataSource}`);
}


// Performance test
console.log('\nPerformance test with asset-specific lookup:');
const startTime = Date.now();
for (let i = 0; i < 10000; i++) {
  lookupSettlementDurationWithAsset('arbitrum', 'ethereum', 'WETH', 25000);
}
const endTime = Date.now();
console.log(`10,000 asset-specific lookups completed in ${endTime - startTime}ms`);

// Test asset coverage
console.log('\nAsset coverage test:');
const testRoutes = [
  { from: 'arbitrum', to: 'ethereum', asset: 'WETH', amount: 25000, expected: 'exact' },
  { from: 'arbitrum', to: 'ethereum', asset: 'USDC', amount: 25000, expected: 'exact' },
  { from: 'base', to: 'ethereum', asset: 'cbBTC', amount: 150000, expected: 'exact' },
  { from: 'zksync', to: 'bnb', asset: 'USDC', amount: 50000, expected: 'L2->L1' },
  { from: 'polygon', to: 'solana', asset: 'WETH', amount: 100000, expected: 'L1->L1' },
  { from: 'berachain', to: 'zircuit', asset: 'USDC', amount: 100000, expected: 'L2->L2' }
];

testRoutes.forEach(route => {
  const result = lookupSettlementDurationWithAsset(route.from, route.to, route.asset, route.amount);
  if (result) {
    console.log(`${route.from} -> ${route.to}, ${route.asset}, $${route.amount.toLocaleString()}: ${result.dataSource} (P25: ${result.settlement_duration_minutes_p25}, P75: ${result.settlement_duration_minutes_p75}) (expected: ${route.expected})`);
  } else {
    console.log(`${route.from} -> ${route.to}, ${route.asset}, $${route.amount.toLocaleString()}: null (expected: ${route.expected})`);
  }
});

// Asset availability analysis
console.log('\nAsset availability analysis:');
const assets = ['USDC', 'WETH', 'USDT', 'cbBTC', 'xPufETH'];
const testChain = 'arbitrum';
const testDestination = 'ethereum';

assets.forEach(asset => {
  const result = lookupSettlementDurationWithAsset(testChain, testDestination, asset, 25000);
  if (result) {
    console.log(`${testChain} -> ${testDestination}, ${asset}: ${result.dataSource} (P25: ${result.settlement_duration_minutes_p25}, P75: ${result.settlement_duration_minutes_p75})`);
  } else {
    console.log(`${testChain} -> ${testDestination}, ${asset}: No data available`);
  }
});
