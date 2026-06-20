//+------------------------------------------------------------------+
//|                                           AAT_DataCollector.mq5 |
//|                                  Copyright 2024, Jules (God Mode)|
//|                                       https://autonomous trader |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property version   "1.10"
#property strict

#include <AAT_NativeSockets.mqh>
#include <AAT_Protocol.mqh>

input int InpPushThresholdPips = 5;

CAATNativeSocket socket;
uint last_push = 0;
double last_price = 0;
bool warmup_done = false;

int OnInit()
{
   if(!socket.Connect("127.0.0.1", 5555)) return INIT_FAILED;
   return INIT_SUCCEEDED;
}

void OnTick()
{
   if(!socket.IsConnected()) { socket.Connect("127.0.0.1", 5555); warmup_done = false; return; }

   // Institutional Warmup: Push 1000 bars once on connect
   if(!warmup_done)
   {
      string data = CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 1000);
      if(socket.Send(data)) warmup_done = true;
      return;
   }

   double price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(MathAbs(price - last_price) >= InpPushThresholdPips * _Point || GetTickCount() - last_push > 60000)
   {
      string data = CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 100);
      if(socket.Send(data)) { last_push = GetTickCount(); last_price = price; }
   }
   string msg = socket.Receive();
}
