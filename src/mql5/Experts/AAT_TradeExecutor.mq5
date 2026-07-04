#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property version   "4.00"
#property strict

#include <Trade\Trade.mqh>
#include <AAT_Defines.mqh>
#include <AAT_BridgeClient.mqh>
#include <AAT_Protocol.mqh>
#include <AAT_Dashboard.mqh>

input double InpFixedLot = 0.01; // Manual Lot Override (if enabled)

CAATBridgeClient bridge;
CTrade trade;
CAATDashboard dash;
double system_lot = 0.01;
string system_version = "4.0.0-PRO";
double last_dd = 0;
int last_pc = 0;

int OnInit() {
   if(!bridge.Connect("127.0.0.1", 8008)) return INIT_FAILED;
   trade.SetExpertMagicNumber(123456);
   EventSetTimer(1);
   return INIT_SUCCEEDED;
}

void OnTimer() {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   last_dd = (balance > 0) ? (balance - equity) / balance * 100.0 : 0;
   if(last_dd < 0) last_dd = 0;
   last_pc = PositionsTotal();

   bridge.Send(CAATProtocol::BuildHEARTBEAT(_Symbol, equity, last_dd, last_pc, 0));

   // Update MT5 Dashboard
   dash.Render(_Symbol, 0, AccountInfoDouble(ACCOUNT_PROFIT), last_pc, last_dd, system_version);
}

void OnTick() {
   string msg = bridge.Receive();
   if(msg != "") {
      string type = CAATProtocol::GetMsgType(msg);

      if(type == "HEARTBEAT_ACK") {
         system_lot = StringToDouble(CAATProtocol::GetV(msg, "lot"));
         system_version = CAATProtocol::GetV(msg, "v");
      }

      if(type == "DECISION") {
         string symbol = CAATProtocol::GetV(msg, "s");
         string action = CAATProtocol::GetV(msg, "act");
         double lots = StringToDouble(CAATProtocol::GetV(msg, "lts"));
         double sl_pts = StringToDouble(CAATProtocol::GetV(msg, "sl_p"));
         double tp_pts = StringToDouble(CAATProtocol::GetV(msg, "tp_p"));
         int internal_id = (int)StringToInteger(CAATProtocol::GetV(msg, "id"));

         if(lots != system_lot) lots = system_lot;

         double price = (action == "BUY") ? SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
         double pt = SymbolInfoDouble(symbol, SYMBOL_POINT);
         double sl = (action == "BUY") ? price - sl_pts * pt : price + sl_pts * pt;
         double tp = (action == "BUY") ? price + tp_pts * pt : price - tp_pts * pt;

         if(action == "BUY") trade.Buy(lots, symbol, price, sl, tp, "AAT V4.0");
         else trade.Sell(lots, symbol, price, sl, tp, "AAT V4.0");

         ulong ticket = trade.ResultOrder();
         bridge.Send(CAATProtocol::BuildTRADE_ACK(internal_id, (int)ticket, "OK", 0));
      }
   }
}

void OnDeinit(const int reason) {
   dash.Clear();
   bridge.Disconnect();
}
