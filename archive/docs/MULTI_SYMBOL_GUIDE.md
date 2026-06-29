# AutoTrader Pro - Multi-Symbol Architecture Guide

## Overview
The multi-symbol feature allows the EA to trade multiple symbols simultaneously from a single chart instance, with each symbol having completely independent analysis, indicators, parameters, and position management.

## Architecture Changes Required

### 1. SymbolContext Structure
```mql5
struct SymbolContext {
   string symbol;
   int magicOffset;
   bool active;
   
   AutoParams P;
   PerformanceStats Stats;
   MarketData M;
   MARKET_REGIME Regime;
   SIGNAL_QUALITY LastSignalQuality;
   datetime LastTradeBar;
   datetime LastOptimizeTime;
   datetime LastReviewTime;
   datetime LastAdjustTime;
   int DailyTrades;
   int DailyLosses;
   int ConsecBuyLosses;
   int ConsecSellLosses;
   
   int hFast,hSlow,hTrend,hATR,hADX,hRSI,hROC,hVol;
   int hFastHTF,hSlowHTF,hTrendHTF,hADXHTF;
   int hFastVHTF,hSlowVHTF,hTrendVHTF;
   int hBB,hMACD,hStoch,hCCI,hWPR,hIchimoku;
   int hPSAR,hMFI,hStdDev,hAO,hDeMarker,hBearsPower,hBullsPower,hAC;
   
   ENUM_TIMEFRAMES LTF,HTF,VHTF;
};
```

### 2. Global Arrays
```mql5
SymbolContext Symbols[10];
int SymbolCount = 0;
```

### 3. Key Functions to Rewrite
- `OnInit()` → Initialize all symbols from `SymbolList` input
- `OnTick()` → Loop through all symbols, call per-symbol analysis
- `OnTradeTransaction()` → Match magic number to find correct symbol context
- `OnDeinit()` → Release all symbol indicators
- All analysis/trading functions → Take `SymbolContext &ctx` parameter

### 4. Magic Number Scheme
- Base: 700070
- Symbol 0: 700070
- Symbol 1: 700170
- Symbol 2: 700270
- etc. (offset by 100 per symbol)

### 5. Input Parameters
```mql5
input string SymbolList = "";           // Comma-separated (empty=current)
input bool MultiSymbolMode = false;     // Enable multi-symbol
```

## Implementation Steps
1. Add `SymbolContext` struct and global arrays
2. Rewrite `OnInit()` to parse `SymbolList` and initialize each symbol
3. Create per-symbol versions of all functions (indicators, analysis, trading)
4. Rewrite `OnTick()` to loop through symbols
5. Rewrite `OnTradeTransaction()` to match magic numbers
6. Update panel to show all symbols

## Benefits
- Single EA instance manages multiple symbols
- Each symbol has independent optimization and parameters
- No interference between symbols
- Unified risk management across portfolio
- CSV journal tracks all symbols separately
