//+------------------------------------------------------------------+
//|                                         AAT_ConnectivityTest.mqh |
//|                                  Copyright 2024, Jules (God Mode)|
//+------------------------------------------------------------------+
#include <AAT_BridgeClient.mqh>

void RunConnectivityTest()
{
   CAATBridgeClient client;
   Print("AAT: Starting Connectivity Test...");

   if(client.Init("127.0.0.1", 8008))
   {
      Print("AAT: Initialized. Waiting for heartbeat handshake...");
      for(int i=0; i<5; i++)
      {
         client.OnTick();
         Sleep(1000);
      }
      Print("AAT: Connectivity Test Finished.");
   }
   else
   {
      Print("AAT: Initialization FAILED.");
   }
}
