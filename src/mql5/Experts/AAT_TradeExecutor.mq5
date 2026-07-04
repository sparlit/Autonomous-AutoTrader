#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property version   "4.00"
#property strict

#include <Trade\Trade.mqh>
#include <AAT_Defines.mqh>
#include <AAT_BridgeClient.mqh>
#include <AAT_Protocol.mqh>
#include <AAT_Dashboard.mqh>

input double InpFixedLot = 0.01;

CAATBridgeClient bridge;
CTrade trade;
CAATDashboard dash;
double system_lot = 0.01;
string system_version = "4.0.0-PRO";

int OnInit() {
   if(!bridge.Connect("127.0.0.1", 8008)) return INIT_FAILED;
   trade.SetExpertMagicNumber(123456);
   EventSetTimer(1);
   return INIT_SUCCEEDED;
}

void OnTimer() {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double dd = (balance > 0) ? (balance - equity) / balance * 100.0 : 0;
   if(dd < 0) dd = 0;

   bridge.Send(CAATProtocol::BuildHEARTBEAT(_Symbol, equity, dd, PositionsTotal(), 0));
   dash.RenderV4(_Symbol, 0, AccountInfoDouble(ACCOUNT_PROFIT), PositionsTotal(), dd, system_version);
}

void OnTick() {
   string msg = bridge.Receive();
   if(msg == "") return;

   string type = CAATProtocol::GetMsgType(msg);

   if(type == "EXECUTION_ORDER" || type == "DECISION") {
      string sub_type = CAATProtocol::GetV(msg, "t");
      string symbol = CAATProtocol::GetV(msg, "s");
      if(symbol == "") symbol = _Symbol;

      if(sub_type == "DEC") {
         string action = CAATProtocol::GetV(msg, "act");
         double lots = StringToDouble(CAATProtocol::GetV(msg, "lts"));
         double sl_pts = StringToDouble(CAATProtocol::GetV(msg, "sl_p"));
         double tp_pts = StringToDouble(CAATProtocol::GetV(msg, "tp_p"));
         int id = (int)StringToInteger(CAATProtocol::GetV(msg, "id"));

         double price = (action == "BUY") ? SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
         double pt = SymbolInfoDouble(symbol, SYMBOL_POINT);
         double sl = (action == "BUY") ? price - sl_pts * pt : price + sl_pts * pt;
         double tp = (action == "BUY") ? price + tp_pts * pt : price - tp_pts * pt;

         // Ensure prices are normalized
         int digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
         sl = NormalizeDouble(sl, digits);
         tp = NormalizeDouble(tp, digits);

         if(action == "BUY") trade.Buy(lots, symbol, price, sl, tp, "AAT V4.0");
         else trade.Sell(lots, symbol, price, sl, tp, "AAT V4.0");

         ulong ticket = trade.ResultOrder();
         bridge.Send(CAATProtocol::BuildTRADE_ACK(id, (int)ticket, "OK", 0));
      }
      else if(sub_type == "MODIFY_SL") {
         ulong ticket = (ulong)StringToInteger(CAATProtocol::GetV(msg, "tk"));
         double sl = StringToDouble(CAATProtocol::GetV(msg, "sl"));
         if(PositionSelectByTicket(ticket)) {
            trade.PositionModify(ticket, sl, PositionGetDouble(POSITION_TP));
         }
      }
      else if(sub_type == "MODIFY_ALL") {
         ulong ticket = (ulong)StringToInteger(CAATProtocol::GetV(msg, "tk"));
         double sl = StringToDouble(CAATProtocol::GetV(msg, "sl"));
         double tp = StringToDouble(CAATProtocol::GetV(msg, "tp"));
         if(PositionSelectByTicket(ticket)) {
            trade.PositionModify(ticket, sl, tp);
         }
      }
   }
}

void OnDeinit(const int reason) {
   dash.Clear();
   bridge.Disconnect();
}
