//+------------------------------------------------------------------+
//|                                           AAT_TradeExecutor.mq5 |
//|                                  Copyright 2024, Jules (God Mode)|
//|                                       https://autonomous trader |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property version   "1.20"
#property strict

#include <AAT_BridgeClient.mqh>

input int InpMagicNumber = 123456;

CAATBridgeClient bridge;

int OnInit()
{
   if(!bridge.Init("127.0.0.1", 5555))
   {
      Print("AAT: Failed to connect to Python Brain");
      return INIT_FAILED;
   }
   return INIT_SUCCEEDED;
}

void OnTick()
{
   bridge.OnTick();
}
