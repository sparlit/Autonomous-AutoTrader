//+------------------------------------------------------------------+
//|                                            AAT_BridgeClient.mqh |
//|                                  Copyright 2024, Jules (God Mode)|
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property strict

#include <AAT_NativeSockets.mqh>
#include <AAT_Protocol.mqh>

class CAATBridgeClient
{
private:
   CAATNativeSocket  m_socket;
   string            m_host;
   int               m_port;

   uint              m_last_heartbeat;
   uint              m_heartbeat_interval;

   uint              m_last_reconnect_attempt;
   uint              m_reconnect_delay;
   uint              m_reconnect_count;

   bool              TryConnect();

public:
                     CAATBridgeClient();
                    ~CAATBridgeClient();

   bool              Init(string host, int port, int hb_interval_sec=10);
   void              OnTick();

   bool              SendSignal(string symbol, double o, double h, double l, double c);
   void              ProcessMessages();
};

CAATBridgeClient::CAATBridgeClient() :
   m_last_heartbeat(0),
   m_heartbeat_interval(10000),
   m_last_reconnect_attempt(0),
   m_reconnect_delay(1000),
   m_reconnect_count(0)
{
}

CAATBridgeClient::~CAATBridgeClient()
{
}

bool CAATBridgeClient::Init(string host, int port, int hb_interval_sec=10)
{
   m_host = host;
   m_port = port;
   m_heartbeat_interval = hb_interval_sec * 1000;

   return TryConnect();
}

bool CAATBridgeClient::TryConnect()
{
   uint now = GetTickCount();
   if(now - m_last_reconnect_attempt < m_reconnect_delay) return false;

   m_last_reconnect_attempt = now;
   Print("AAT: Attempting to connect to Python Hive at ", m_host, ":", m_port, " (Attempt ", m_reconnect_count + 1, ")");

   if(m_socket.Connect(m_host, m_port, 1000))
   {
      Print("AAT: Connected successfully.");
      m_reconnect_delay = 1000;
      m_reconnect_count = 0;
      return true;
   }

   m_reconnect_count++;
   m_reconnect_delay = (uint)fmin(1000 * MathPow(2, m_reconnect_count), 30000);
   return false;
}

void CAATBridgeClient::OnTick()
{
   if(!m_socket.IsConnected())
   {
      TryConnect();
      return;
   }

   uint now = GetTickCount();
   if(now - m_last_heartbeat > m_heartbeat_interval)
   {
      string hb = CAATProtocol::BuildHEARTBEAT(_Symbol, AccountInfoDouble(ACCOUNT_EQUITY), 0.0);
      if(m_socket.Send(hb))
      {
         m_last_heartbeat = now;
      }
   }

   ProcessMessages();
}

void CAATBridgeClient::ProcessMessages()
{
   string msg;
   while((msg = m_socket.ReceiveMessage()) != "")
   {
      string type = CAATProtocol::GetMsgType(msg);
      if(type == "PONG" || type == "HEARTBEAT_ACK") { /* OK */ }
      else if(type == "ACK") Print("AAT: Python ACK: ", msg);
      else Print("AAT: Received: ", msg);
   }
}

bool CAATBridgeClient::SendSignal(string symbol, double o, double h, double l, double c)
{
   if(!m_socket.IsConnected()) return false;
   string ohlc = CAATProtocol::BuildOHLC(symbol, Period(), o, h, l, c);
   return m_socket.Send(ohlc);
}
