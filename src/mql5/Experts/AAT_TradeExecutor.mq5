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
   if(msg != "") {
      string type = CAATProtocol::GetMsgType(msg);
      if(type == "DECISION") {
         string symbol = CAATProtocol::GetV(msg, "s");
         string action = CAATProtocol::GetV(msg, "act");
         double lots = StringToDouble(CAATProtocol::GetV(msg, "lts"));
         int id = (int)StringToInteger(CAATProtocol::GetV(msg, "id"));

         if(action == "BUY") trade.Buy(lots, symbol);
         else trade.Sell(lots, symbol);

         ulong ticket = trade.ResultOrder();
         bridge.Send(CAATProtocol::BuildTRADE_ACK(id, (int)ticket, "OK", 0));
      }
   }
}

void OnDeinit(const int reason) {
   dash.Clear();
   bridge.Disconnect();
}
