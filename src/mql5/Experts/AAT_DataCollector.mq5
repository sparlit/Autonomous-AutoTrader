#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property version   "4.00"
#property strict

#include <AAT_Defines.mqh>
#include <AAT_BridgeClient.mqh>

input string   InpHost = "127.0.0.1";
input int      InpPort = 8008;

CAATBridgeClient bridge;

int OnInit() {
   if(!bridge.Init(InpHost, InpPort, AAT_ROLE_DATA_COLLECTOR)) return INIT_FAILED;
   EventSetTimer(1);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int r) { EventKillTimer(); bridge.Disconnect(); }
void OnTick() { bridge.PerformUpdate(); }
void OnTimer() { bridge.PerformUpdate(); }
