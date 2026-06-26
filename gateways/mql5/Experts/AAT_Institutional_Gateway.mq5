#property copyright "Copyright 2024, Jules (God Mode)"
#property version   "3.12"
#property strict

#include <AAT_Core.mqh>

input string InpHost  = "127.0.0.1"; // Bridge Host
input int    InpPort  = 8008;        // Bridge Port
input long   InpMagic = 2026001;     // Magic Number

CAATGateway gateway;

int OnInit() {
   if(!gateway.Connect(InpHost, InpPort, InpMagic)) {
      Print("AAT: Connection Failed. Initializing background retry.");
   }
   EventSetTimer(1);
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason) {
   EventKillTimer();
}

void OnTick() {
   gateway.PushMarketData(_Symbol);
   string msg = gateway.ReceiveMessage();
   if(msg != "") gateway.HandleOrders(msg);
}

void OnTimer() {
   gateway.PushHeartbeat();
}
