#ifndef AAT_BRIDGE_CLIENT_MQH
#define AAT_BRIDGE_CLIENT_MQH

#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property strict

#include <Trade\Trade.mqh>
#include "AAT_Defines.mqh"
#include "AAT_NativeSockets.mqh"
#include "AAT_Protocol.mqh"
#include "AAT_Dashboard.mqh"

class CAATBridgeClient
{
private:
   CAATNativeSocket m_s;
   CTrade           m_t;
   CAATDashboard    m_d;
   string           m_h;
   int              m_p;
   uint             m_l_hb;
   uint             m_l_dp;
   bool             m_u_d;
   bool             m_d_created;
   bool             m_syn;
   ENUM_AAT_ROLE    m_role;
   long             m_magic;
   long             m_seq_tx;

public:
   CAATBridgeClient() {
      m_h = "127.0.0.1";
      m_p = 8008;
      m_l_hb = 0;
      m_l_dp = 0;
      m_u_d = true;
      m_d_created = false;
      m_syn = false;
      m_role = AAT_ROLE_MASTER;
      m_magic = 778899;
      m_seq_tx = 0;
      m_t.SetExpertMagicNumber(m_magic);
   }

   bool Init(string h, int p, ENUM_AAT_ROLE role, long magic=778899, bool d=true) {
      m_h = h; m_p = p; m_role = role; m_u_d = d; m_magic = magic;
      m_t.SetExpertMagicNumber(m_magic);
      if(m_u_d) m_d_created = m_d.Create("AAT_Dash", 320, 500);
      return m_s.Connect(m_h, m_p);
   }

   bool Connect(string host, int port) { return m_s.Connect(host, port); }
   bool Send(string data) { return m_s.Send(data); }
   string Receive() { return m_s.Receive(); }
   void Disconnect() { m_s.Disconnect(); }
   bool IsConnected() { return m_s.IsConnected(); }

   void PerformUpdate() { OnTick(); }

   void OnTick() {
      if(!m_s.IsConnected()) { m_s.Connect(m_h, m_p); m_syn = false; return; }
      if(m_d.IsPaused()) return;

      uint now = GetTickCount();

      if(now - m_l_hb > 5000) {
         double equity = AccountInfoDouble(ACCOUNT_EQUITY);
         double balance = AccountInfoDouble(ACCOUNT_BALANCE);
         double dd = (balance > 0) ? (balance - equity) / balance * 100.0 : 0;
         if(dd < 0) dd = 0;

         if(m_s.Send(CAATProtocol::BuildHEARTBEAT(_Symbol, equity, dd, PositionsTotal(), ++m_seq_tx))) {
            m_l_hb = now;
         }
      }

      if(now - m_l_dp > 200 && (m_role == AAT_ROLE_DATA_COLLECTOR || m_role == AAT_ROLE_MASTER)) {
         if(m_s.Send(CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 30, ++m_seq_tx))) {
            m_l_dp = now;
         }
      }

      string msg;
      while((msg = m_s.Receive()) != "") {
         ProcMsg(msg);
      }
   }

   void ProcMsg(string m) {
      string t = CAATProtocol::GetMsgType(m);
      if(t == "TLM") HandleTlm(m);
      else if(t == "SYNC_REQ") m_s.Send(CAATProtocol::BuildSYNC(_Symbol, ++m_seq_tx));
      else if(t == "DECISION" || t == "EXECUTION_ORDER") HandleDecision(m);
   }

   void HandleDecision(string j) {
      if(m_role != AAT_ROLE_TRADE_EXECUTOR && m_role != AAT_ROLE_MASTER) return;

      string sub_type = CAATProtocol::GetV(j, "t");
      string symbol = CAATProtocol::GetV(j, "s");
      if(symbol == "") symbol = _Symbol;

      if(sub_type == "DEC") {
         string action = CAATProtocol::GetV(j, "act");
         double lots = StringToDouble(CAATProtocol::GetV(j, "lts"));
         double sl_pts = StringToDouble(CAATProtocol::GetV(j, "sl_p"));
         double tp_pts = StringToDouble(CAATProtocol::GetV(j, "tp_p"));
         int internal_id = (int)StringToInteger(CAATProtocol::GetV(j, "id"));
         string comment = CAATProtocol::GetV(j, "comment");

         double price = (action == "BUY") ? SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
         double pt = SymbolInfoDouble(symbol, SYMBOL_POINT);
         double sl = (action == "BUY") ? price - sl_pts * pt : price + sl_pts * pt;
         double tp = (action == "BUY") ? price + tp_pts * pt : price - tp_pts * pt;

         int digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
         sl = NormalizeDouble(sl, digits);
         tp = NormalizeDouble(tp, digits);

         m_t.SetTypeFillingBySymbol(symbol);

         bool success = false;
         if(action == "BUY") success = m_t.Buy(lots, symbol, price, sl, tp, comment);
         else success = m_t.Sell(lots, symbol, price, sl, tp, comment);

         ulong ticket = 0;
         string err_msg = "OK";

         if(success) {
            ticket = m_t.ResultOrder();
         } else {
            err_msg = m_t.ResultRetcodeDescription();
            Print("AAT: [CRITICAL] Trade Failed: ", err_msg, " Symbol: ", symbol, " Action: ", action);
         }

         m_s.Send(CAATProtocol::BuildTRADE_ACK(internal_id, (long)ticket, err_msg, ++m_seq_tx));
      }
      else if(sub_type == "MODIFY_SL") {
         ulong ticket = (ulong)StringToInteger(CAATProtocol::GetV(j, "tk"));
         double sl = StringToDouble(CAATProtocol::GetV(j, "sl"));
         if(PositionSelectByTicket(ticket)) {
            m_t.PositionModify(ticket, sl, PositionGetDouble(POSITION_TP));
         }
      }
      else if(sub_type == "CLOSE_ALL") {
         for(int i=PositionsTotal()-1; i>=0; i--) {
            ulong tk = PositionGetTicket(i);
            if(PositionSelectByTicket(tk) && PositionGetInteger(POSITION_MAGIC) == m_magic) {
               m_t.PositionClose(tk);
            }
         }
      }
   }

   void HandleTlm(string j) {
      if(!m_u_d) return;
      m_d.RenderV4(_Symbol, 0, AccountInfoDouble(ACCOUNT_PROFIT), PositionsTotal(), StringToDouble(CAATProtocol::GetV(j, "dd")), "V4.0-PRO");
   }

   void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam) {
      if(id == CHARTEVENT_CLICK) {
         string cmd = m_d.OnClick((int)lparam, (int)dparam);
         if(cmd == "PAUSE") m_d.SetPaused(!m_d.IsPaused());
      }
   }
};
#endif
