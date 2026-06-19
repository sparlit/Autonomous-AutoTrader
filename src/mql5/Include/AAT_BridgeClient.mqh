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
   uint              m_last_data_push;
   uint              m_heartbeat_interval;

public:
                     CAATBridgeClient();
                    ~CAATBridgeClient();

   bool              Init(string host, int port, int hb_interval_sec=10);
   void              OnTick();
   void              ProcessMessages();
   void              DrawObjects(string draw_json);
};

CAATBridgeClient::CAATBridgeClient() : m_last_heartbeat(0), m_last_data_push(0), m_heartbeat_interval(10000)
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

   uint now = GetTickCount();

   if(now - m_last_heartbeat > m_heartbeat_interval)
   {
      string hb = CAATProtocol::BuildHEARTBEAT(_Symbol, AccountInfoDouble(ACCOUNT_EQUITY), 0.0);
      if(m_socket.Send(hb)) m_last_heartbeat = now;
   }

   if(now - m_last_data_push > 5000)
   {
      string data = CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 100);
      if(m_socket.Send(data)) m_last_data_push = now;
   }

   ProcessMessages();
}

void CAATBridgeClient::ProcessMessages()
{
   string msg = m_socket.Receive();
   if(msg != "")
   {
      string type = CAATProtocol::GetMsgType(msg);
      if(type == "DECISION")
      {
         string draw = CAATProtocol::GetValue(msg, "drw");
         if(draw != "") DrawObjects(draw);

         string action = CAATProtocol::GetValue(msg, "act");
         if(action != "WAIT" && action != "")
         {
            Print("AAT TRADE Decision: ", action, " Lots: ", CAATProtocol::GetValue(msg, "lts"));
         }
      }
   }
}

void CAATBridgeClient::DrawObjects(string draw_json)
{
   // Basic drawing logic: if it contains RECTANGLE
   if(StringFind(draw_json, "RECTANGLE") >= 0)
   {
      string name = CAATProtocol::GetValue(draw_json, "name");
      double top = StringToDouble(CAATProtocol::GetValue(draw_json, "top"));
      double bottom = StringToDouble(CAATProtocol::GetValue(draw_json, "bottom"));

      if(!ObjectCreate(0, name, OBJ_RECTANGLE, 0, TimeCurrent(), top, TimeCurrent() - 3600*24, bottom))
      {
         ObjectMove(0, name, 0, TimeCurrent(), top);
         ObjectMove(0, name, 1, TimeCurrent() - 3600*24, bottom);
      }
      ObjectSetInteger(0, name, OBJPROP_COLOR, clrDodgerBlue);
      ObjectSetInteger(0, name, OBJPROP_BACK, true);
   }
}
