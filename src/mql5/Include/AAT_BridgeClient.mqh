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
#include <Trade\Trade.mqh>

class CAATBridgeClient
{
private:
   CAATNativeSocket  m_socket;
   CTrade            m_trade;
   string            m_host;
   int               m_port;
   uint              m_last_heartbeat;
   uint              m_last_data_push;
   uint              m_heartbeat_interval;
   double            m_last_push_price;
   double            m_push_threshold;
   bool              m_synced;

public:
                     CAATBridgeClient();
                    ~CAATBridgeClient();

   bool              Init(string host, int port, int hb_interval_sec=10);
   void              OnTick();
   void              ProcessMessages();
   void              DrawObjects(string draw_json);
   void              HandleTrade(string msg);
   void              HandleManagement(string mgmt_json);
   bool              ShouldPushData(double current_price);
};

CAATBridgeClient::CAATBridgeClient() : m_last_heartbeat(0), m_last_data_push(0), m_heartbeat_interval(10000), m_last_push_price(0), m_push_threshold(0.0005), m_synced(false)
{
   m_trade.SetExpertMagicNumber(123456);
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

bool CAATBridgeClient::ShouldPushData(double current_price)
{
   if(m_last_push_price == 0) return true;
   if(MathAbs(current_price - m_last_push_price) >= m_push_threshold) return true;
   if(GetTickCount() - m_last_data_push > 60000) return true;
   return false;
}

void CAATBridgeClient::OnTick()
{
   if(!m_socket.IsConnected())
   {
      m_socket.Connect(m_host, m_port);
      m_synced = false;
      return;
   }

   if(!m_synced)
   {
      string sync = CAATProtocol::BuildSYNC(_Symbol);
      if(m_socket.Send(sync)) m_synced = true;
      return;
   }

   uint now = GetTickCount();
   double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   if(now - m_last_heartbeat > m_heartbeat_interval)
   {
      string hb = CAATProtocol::BuildHEARTBEAT(_Symbol, AccountInfoDouble(ACCOUNT_EQUITY), 0.0);
      if(m_socket.Send(hb)) m_last_heartbeat = now;
   }

   if(ShouldPushData(current_price))
   {
      string data = CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 100);
      if(m_socket.Send(data))
      {
         m_last_data_push = now;
         m_last_push_price = current_price;
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
      if(type == "DECISION")
      {
         string draw = CAATProtocol::GetValue(msg, "drw");
         if(draw != "") DrawObjects(draw);

         string mgmt = CAATProtocol::GetValue(msg, "mgmt");
         if(mgmt != "") HandleManagement(mgmt);

         string action = CAATProtocol::GetValue(msg, "act");
         if(action != "WAIT" && action != "")
         {
            HandleTrade(msg);
         }
      }
   }
}

void CAATBridgeClient::HandleManagement(string mgmt_json)
{
   // Basic management parser (mvp handles one command per push)
   string act = CAATProtocol::GetValue(mgmt_json, "act");
   long ticket = StringToInteger(CAATProtocol::GetValue(mgmt_json, "tk"));

   if(PositionSelectByTicket(ticket))
   {
      if(act == "CLOSE_PARTIAL")
      {
         double vol = PositionGetDouble(POSITION_VOLUME);
         double pct = StringToDouble(CAATProtocol::GetValue(mgmt_json, "pct"));
         m_trade.PositionClosePartial(ticket, vol * pct);
      }
      else if(act == "MODIFY_SL")
      {
         double sl = StringToDouble(CAATProtocol::GetValue(mgmt_json, "sl"));
         double tp = PositionGetDouble(POSITION_TP);
         m_trade.PositionModify(ticket, sl, tp);
      }
   }
}

void CAATBridgeClient::HandleTrade(string msg)
{
   int id = (int)StringToInteger(CAATProtocol::GetValue(msg, "id"));
   string action = CAATProtocol::GetValue(msg, "act");
   double lots = StringToDouble(CAATProtocol::GetValue(msg, "lts"));
   double sl = StringToDouble(CAATProtocol::GetValue(msg, "sl"));
   double tp = StringToDouble(CAATProtocol::GetValue(msg, "tp"));

   bool res = false;
   if(action == "BUY")
      res = m_trade.Buy(lots, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_ASK), sl, tp, StringFormat("AAT:%d", id));
   else if(action == "SELL")
      res = m_trade.Sell(lots, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_BID), sl, tp, StringFormat("AAT:%d", id));

   uint ticket = (uint)m_trade.ResultDeal();
   if(ticket == 0) ticket = (uint)m_trade.ResultOrder();

   string err = "";
   if(!res) err = IntegerToString(m_trade.ResultRetcode());

   string ack = CAATProtocol::BuildTRADE_ACK(id, (int)ticket, err);
   m_socket.Send(ack);
}

void CAATBridgeClient::DrawObjects(string draw_json)
{
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
