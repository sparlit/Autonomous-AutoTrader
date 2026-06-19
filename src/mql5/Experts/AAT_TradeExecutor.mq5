//+------------------------------------------------------------------+
//|                                           AAT_TradeExecutor.mq5 |
//|                                  Copyright 2024, Jules (God Mode)|
//|                                       https://autonomous trader |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>
#include <AAT_BridgeClient.mqh>

input double InpRiskPercent = 1.0;
input int InpMagicNumber = 123456;
input int InpStopLoss = 200;
input int InpTakeProfit = 400;

CTrade trade;
CAATBridgeClient bridge;

int OnInit()
{
   trade.SetExpertMagicNumber(InpMagicNumber);
   if(!bridge.Init("127.0.0.1", 5555))
   {
      Print("AAT: Failed to connect to Python Brain");
      return INIT_FAILED;
   }
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
}

void OnTick()
{
   bridge.OnTick();

   // Push data to brain
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   if(CopyRates(_Symbol, _Period, 0, 100, rates) > 0)
   {
      // In a real scenario, we'd build a complex JSON with history
      // For this step, we push a trigger check
   }
}

// Handler for Python decisions (called from bridge.ProcessMessages)
void ExecuteAction(string action, string symbol)
{
   if(action == "BUY")
   {
      double price = SymbolInfoDouble(symbol, SYMBOL_ASK);
      double sl = price - InpStopLoss * _Point;
      double tp = price + InpTakeProfit * _Point;
      trade.Buy(0.1, symbol, price, sl, tp, "AAT Buy Signal");
   }
   else if(action == "SELL")
   {
      double price = SymbolInfoDouble(symbol, SYMBOL_BID);
      double sl = price + InpStopLoss * _Point;
      double tp = price - InpTakeProfit * _Point;
      trade.Sell(0.1, symbol, price, sl, tp, "AAT Sell Signal");
   }
}
