#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property version   "3.00"
#property strict
#include <AAT_BridgeClient.mqh>
CAATBridgeClient bridge;
int OnInit() { if(!bridge.Init("127.0.0.1", 8008, AAT_ROLE_MASTER)) return INIT_FAILED; EventSetTimer(1); return INIT_SUCCEEDED; }
void OnDeinit(const int reason) { EventKillTimer(); }
void OnTick() { bridge.PerformUpdate(); }
void OnTimer() { bridge.PerformUpdate(); }
