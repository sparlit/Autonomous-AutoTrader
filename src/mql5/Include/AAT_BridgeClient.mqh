//+------------------------------------------------------------------+
//|                                            AAT_BridgeClient.mqh |
//|                                  Copyright 2024, Jules (God Mode)|
//|                                       https://autonomous trader |
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

public:
                     CAATBridgeClient();
                    ~CAATBridgeClient();

   bool              Init(string host, int port, int hb_interval_sec=10);
   void              OnTick();

   bool              SendSignal(string symbol, double o, double h, double l, double c);
   void              ProcessMessages();
};

CAATBridgeClient::CAATBridgeClient() : m_last_heartbeat(0), m_heartbeat_interval(10000)
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

   return m_socket.Connect(m_host, m_port);
}

void CAATBridgeClient::OnTick()
{
   if(!m_socket.IsConnected())
   {
      m_socket.Connect(m_host, m_port);
      return;
   }

   // Heartbeat logic
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
   string msg = m_socket.Receive();
   if(msg != "")
   {
      string type = CAATProtocol::GetMsgType(msg);
      if(type == "PONG" || type == "HEARTBEAT_ACK")
      {
         // Connection alive
      }
      else if(type == "ACK")
      {
         Print("AAT: Python ACK: ", msg);
      }
      else
      {
         Print("AAT: Unknown message from Python: ", msg);
      }
   }
}

bool CAATBridgeClient::SendSignal(string symbol, double o, double h, double l, double c)
{
   string ohlc = CAATProtocol::BuildOHLC(symbol, Period(), o, h, l, c);
   return m_socket.Send(ohlc);
}
