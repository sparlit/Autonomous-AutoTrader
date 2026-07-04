#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property strict

#include "AAT_NativeSockets.mqh"
#include "AAT_Protocol.mqh"
#include "AAT_Dashboard.mqh"

class CAATBridgeClient
{
private:
   CAATNativeSocket m_socket;

public:
   CAATBridgeClient() {}

   bool Connect(string host, int port) {
      return m_socket.Connect(host, port);
   }

   bool Send(string data) {
      return m_socket.Send(data);
   }

   string Receive() {
      return m_socket.Receive();
   }

   void Disconnect() {
      m_socket.Disconnect();
   }

   bool IsConnected() {
      return m_socket.IsConnected();
   }
};
