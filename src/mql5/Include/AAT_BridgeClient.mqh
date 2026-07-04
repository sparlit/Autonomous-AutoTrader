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
   CAATBridgeClient() : m_h("127.0.0.1"), m_p(8008), m_l_hb(0), m_l_dp(0), m_u_d(true), m_d_created(false), m_syn(false), m_role(AAT_ROLE_MASTER), m_magic(123456), m_seq_tx(0) {
      m_t.SetExpertMagicNumber(m_magic);
   }

   bool Init(string h, int p, ENUM_AAT_ROLE role, long magic=123456, bool d=true) {
      m_h=h; m_p=p; m_role=role; m_u_d=d; m_magic=magic;
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
      if(!m_s.IsConnected()) { m_s.Connect(m_h, m_p); m_syn=false; return; }
      if(m_d.IsPaused()) return;

      uint now = GetTickCount();

      if(now - m_l_hb > 5000) {
         m_s.Send(CAATProtocol::BuildHEARTBEAT(_Symbol, AccountInfoDouble(ACCOUNT_EQUITY), 0, PositionsTotal(), ++m_seq_tx));
         m_l_hb = now;
      }

      if(now - m_l_dp > 200 && (m_role == AAT_ROLE_DATA_COLLECTOR || m_role == AAT_ROLE_MASTER)) {
         if(m_s.Send(CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 30, ++m_seq_tx))) m_l_dp = now;
      }

      Proc();
   }

   void Proc() {
      string m=m_s.Receive(); if(m=="") return;
      string t=CAATProtocol::GetMsgType(m);
      if(t=="TLM") HandleTlm(m);
      else if(t=="SYNC_REQ") m_s.Send(CAATProtocol::BuildSYNC(_Symbol, ++m_seq_tx));
   }

   void HandleTlm(string j) {
      if(!m_u_d) return;
      m_d.RenderV3(_Symbol, CAATProtocol::GetV(j, "st"), StringToDouble(CAATProtocol::GetV(j, "scr")), CAATProtocol::GetV(j, "htf"), StringToDouble(CAATProtocol::GetV(j, "dd")));
   }
};
#endif
