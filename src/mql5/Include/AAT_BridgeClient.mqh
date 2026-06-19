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
#include <AAT_Dashboard.mqh>

class CAATBridgeClient
{
private:
   CAATNativeSocket  m_socket;
   CTrade            m_trade;
   CAATDashboard     m_dash;
   string            m_host;
   int               m_port;
   uint              m_last_heartbeat_rx;
   uint              m_last_data_push;
   uint              m_heartbeat_interval;
   double            m_last_push_price;
   double            m_push_threshold;
   bool              m_synced;
   bool              m_failsafe_active;
   bool              m_use_dash;

public:
                     CAATBridgeClient();
                    ~CAATBridgeClient();

   bool              Init(string host, int port, bool use_dash=false, int hb_interval_sec=10);
   void              OnTick();
   void              ProcessMessages();
   void              DrawObjects(string draw_json);
   void              HandleTrade(string msg);
   void              HandleManagement(string mgmt_json);
   void              HandleTelemetry(string tlm_json);
   void              ActivateFailsafe();
   void              CleanupObjects();
   bool              ShouldPushData(double current_price);
};

CAATBridgeClient::CAATBridgeClient() : m_last_heartbeat_rx(0), m_last_data_push(0), m_heartbeat_interval(10000), m_last_push_price(0), m_push_threshold(0.0005), m_synced(false), m_failsafe_active(false), m_use_dash(false)
{
   m_trade.SetExpertMagicNumber(123456);
}

CAATBridgeClient::~CAATBridgeClient() {}

bool CAATBridgeClient::Init(string host, int port, bool use_dash=false, int hb_interval_sec=10)
{
   m_host = host; m_port = port; m_use_dash = use_dash;
   m_heartbeat_interval = hb_interval_sec * 1000;
   m_last_heartbeat_rx = GetTickCount();
   if(m_use_dash) m_dash.Create("AAT_Dash", 320, 400);
   return m_socket.Connect(m_host, m_port);
}

void CAATBridgeClient::ActivateFailsafe()
{
   if(m_failsafe_active) return;
   Print("AAT: !!! FAILSAFE ACTIVATED !!!");
   for(int i=PositionsTotal()-1; i>=0; i--)
   {
      if(PositionGetSymbol(i) == _Symbol)
      {
         ulong ticket = PositionGetInteger(POSITION_TICKET);
         double entry = PositionGetDouble(POSITION_PRICE_OPEN);
         double tp = PositionGetDouble(POSITION_TP);
         double cur = PositionGetDouble(POSITION_PRICE_CURRENT);
         if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY && cur > entry + 50*_Point)
            m_trade.PositionModify(ticket, entry + 10*_Point, tp);
         else if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL && cur < entry - 50*_Point)
            m_trade.PositionModify(ticket, entry - 10*_Point, tp);
      }
   }
   m_failsafe_active = true;
}

void CAATBridgeClient::CleanupObjects()
{
   datetime limit = iTime(_Symbol, _Period, 50);
   for(int i=ObjectsTotal(0)-1; i>=0; i--)
   {
      string name = ObjectName(0, i);
      if(StringFind(name, "OB_") == 0 || StringFind(name, "AAT_") == 0)
      {
         datetime obj_time = (datetime)ObjectGetInteger(0, name, OBJPROP_TIME, 0);
         if(obj_time < limit) ObjectDelete(0, name);
      }
   }
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
      if(GetTickCount() - m_last_heartbeat_rx > 60000) ActivateFailsafe();
      return;
   }

   m_failsafe_active = false;
   if(!m_synced)
   {
      string sync = CAATProtocol::BuildSYNC(_Symbol);
      if(m_socket.Send(sync)) m_synced = true;
      return;
   }

   uint now = GetTickCount();
   double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   if(now - m_last_data_push > 10000)
   {
      string hb = CAATProtocol::BuildHEARTBEAT(_Symbol, AccountInfoDouble(ACCOUNT_EQUITY), 0.0);
      if(m_socket.Send(hb)) m_last_data_push = now;
   }

   if(ShouldPushData(current_price))
   {
      string data = CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 100);
      if(m_socket.Send(data)) { m_last_data_push = now; m_last_push_price = current_price; }
   }

   ProcessMessages();
   if(GetTickCount() % 500 == 0) CleanupObjects();
}

void CAATBridgeClient::ProcessMessages()
{
   string msg = m_socket.Receive();
   if(msg != "")
   {
      m_last_heartbeat_rx = GetTickCount();
      string type = CAATProtocol::GetMsgType(msg);
      if(type == "DECISION")
      {
         string draw = CAATProtocol::GetValue(msg, "drw");
         if(draw != "") DrawObjects(draw);

         string tlm = CAATProtocol::GetValue(msg, "tlm");
         if(tlm != "") HandleTelemetry(tlm);

         string mgmt = CAATProtocol::GetValue(msg, "mgmt");
         if(mgmt != "") HandleManagement(mgmt);

         string action = CAATProtocol::GetValue(msg, "act");
         if(action != "WAIT" && action != "") HandleTrade(msg);
      }
   }
}

void CAATBridgeClient::HandleTelemetry(string tlm_json)
{
   if(!m_use_dash) return;
   double score = StringToDouble(CAATProtocol::GetValue(tlm_json, "scr"));
   string htf = CAATProtocol::GetValue(tlm_json, "htf");
   string st = CAATProtocol::GetValue(tlm_json, "st");
   double dd = StringToDouble(CAATProtocol::GetValue(tlm_json, "dd"));
   m_dash.Render(_Symbol, st, score, htf, dd);
}

void CAATBridgeClient::HandleManagement(string mgmt_json)
{
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
   int sl_p = (int)StringToInteger(CAATProtocol::GetValue(msg, "sl_p"));
   int tp_p = (int)StringToInteger(CAATProtocol::GetValue(msg, "tp_p"));

   double entry = (action == "BUY") ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double sl = (action == "BUY") ? entry - sl_p * _Point : entry + sl_p * _Point;
   double tp = (action == "BUY") ? entry + tp_p * _Point : entry - tp_p * _Point;

   MqlTradeRequest request={0}; MqlTradeResult result={0};
   request.action = TRADE_ACTION_DEAL; request.symbol = _Symbol; request.volume = lots;
   request.type = (action == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   request.price = entry; request.sl = sl; request.tp = tp;
   request.deviation = 10; request.magic = 123456; request.comment = StringFormat("AAT:%d", id);

   bool res = OrderSendAsync(request, result);
   string ack = CAATProtocol::BuildTRADE_ACK(id, (int)result.order, res ? "" : IntegerToString(result.retcode));
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
