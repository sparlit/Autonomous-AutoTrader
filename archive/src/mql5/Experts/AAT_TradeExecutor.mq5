#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property version   "3.00"
#property strict
#include <AAT_BridgeClient.mqh>

input string   InpHost   = "127.0.0.1"; // Bridge Host
input int      InpPort   = 8008;        // Bridge Port
input long     InpMagic  = 123456;      // Strategy Magic

CAATBridgeClient bridge;

int OnInit() {
   if(!bridge.Init(InpHost, InpPort, AAT_ROLE_TRADE_EXECUTOR, InpMagic))
      return INIT_FAILED;
   EventSetTimer(1);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { EventKillTimer(); }
void OnTick() { bridge.PerformUpdate(); }
void OnTimer() { bridge.PerformUpdate(); }
