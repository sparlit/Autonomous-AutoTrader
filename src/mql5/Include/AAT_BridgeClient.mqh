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
   CAATNativeSocket m_socket;
   ENUM_AAT_ROLE    m_role;
   string           m_host;
   int              m_port;
   uint             m_last_hb;
   uint             m_last_dp;
   long             m_seq_tx;

public:
   CAATBridgeClient() : m_last_hb(0), m_last_dp(0), m_seq_tx(0) {}

   bool Init(string h, int p, ENUM_AAT_ROLE role, long magic=123456, bool d=true) {
      m_h=h; m_p=p; m_role=role; m_u_d=d; m_magic=magic;
      m_t.SetExpertMagicNumber(m_magic);
      if(m_u_d) {
         string d_name = "AAT_Dash_" + _Symbol;
         m_d_created = m_d.Create(d_name, 320, 500);
      }
      return m_s.Connect(m_h, m_p);
   }

   bool Connect(string host, int port) { return m_s.Connect(host, port); }
   bool Send(string data) { return m_s.Send(data); }
   string Receive() { return m_s.Receive(); }
   void Disconnect() { m_s.Disconnect(); }
   bool IsConnected() { return m_s.IsConnected(); }

   void PerformUpdate() { OnTick(); }

   void OnTick() {
      uint n=GetTickCount();
      if(!m_s.IsConnected()) { m_s.Connect(m_h, m_p); m_syn=false; return; }
      if(m_d.IsPaused()) return;

      if(!m_syn) {
         if(m_s.Send(CAATProtocol::BuildSYNC(_Symbol, ++m_seq_tx))) m_syn=true;
         return;
      }

      double cp=SymbolInfoDouble(_Symbol, SYMBOL_BID);

      // Throttled Heartbeat (10s)
      if(n-m_l_hb>10000) {
         double eq = AccountInfoDouble(ACCOUNT_EQUITY);
         double bal = AccountInfoDouble(ACCOUNT_BALANCE);
         double dd = (bal > 0) ? (bal - eq) / bal * 100.0 : 0;
         if(dd < 0) dd = 0;
         if(m_s.Send(CAATProtocol::BuildHEARTBEAT(_Symbol, eq, dd, PositionsTotal(), ++m_seq_tx))) m_l_hb=n;
      }

      // Throttled Data Push (Min 200ms)
      if(n-m_l_dp > 200 && (m_role == AAT_ROLE_DATA_COLLECTOR || m_role == AAT_ROLE_MASTER)) {
         if(m_s.Send(CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 30, ++m_seq_tx))) {
            m_l_dp=n;
         }
      }

      Proc();
   }

   void Proc() {
      string m=m_s.Receive(); if(m=="") return;
      string t=CAATProtocol::GetMsgType(m);
      if(t=="TLM") HandleTlm(m);
      else if(t=="SYNC_REQ") { m_s.Send(CAATProtocol::BuildSYNC(_Symbol, ++m_seq_tx)); }
   }

   void HandleTlm(string j) {
      if(!m_u_d) return;
      m_d.Render(_Symbol, CAATProtocol::GetV(j, "st"), StringToDouble(CAATProtocol::GetV(j, "scr")), CAATProtocol::GetV(j, "htf"), StringToDouble(CAATProtocol::GetV(j, "dd")));
   }
};
