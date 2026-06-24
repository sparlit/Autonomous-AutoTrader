#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property strict
#include <Trade\Trade.mqh>
#include "AAT_NativeSockets.mqh"
#include "AAT_Protocol.mqh"
#include "AAT_Dashboard.mqh"

enum ENUM_AAT_ROLE {
   AAT_ROLE_DATA_COLLECTOR,
   AAT_ROLE_TRADE_EXECUTOR,
   AAT_ROLE_MASTER
};

class CAATBridgeClient
{
private:
   CAATNativeSocket m_s;
   CTrade m_t;
   CAATDashboard m_d;
   string m_h, m_u_s;
   int m_p;
   datetime m_l_hb, m_l_dp;
   double m_l_pr, m_p_th;
   bool m_u_d;
   bool m_d_created;
   ENUM_AAT_ROLE m_role;

public:
   CAATBridgeClient() : m_h("127.0.0.1"), m_p(5555), m_l_hb(0), m_l_dp(0), m_l_pr(0), m_p_th(0.0001), m_u_d(true), m_d_created(false), m_role(AAT_ROLE_MASTER) {
      m_t.SetExpertMagicNumber(123456);
   }

   bool Init(string h, int p, ENUM_AAT_ROLE role, bool d=true) {
      m_h=h; m_p=p; m_role=role; m_u_d=d;
      if(m_u_d) {
         string d_name = "AAT_Dash_" + _Symbol;
         m_d_created = m_d.Create(d_name, 320, 500);
         if(!m_d_created) Print("AAT: Dashboard creation failed for ", _Symbol);
      }
      m_s.Connect(m_h, m_p);
      return true;
   }

   void PerformUpdate() { OnTick(); }

   void OnTick() {
      if(!m_s.IsConnected()) {
         if(!m_s.Connect(m_h, m_p)) return;
      }

      datetime n=TimeCurrent(); double cp=SymbolInfoDouble(_Symbol, SYMBOL_BID);

      // Heartbeat is sent by all roles to maintain connection and update account info
      if(n-m_l_hb>10) {
         double eq=AccountInfoDouble(ACCOUNT_EQUITY), bal=AccountInfoDouble(ACCOUNT_BALANCE);
         double dd=(bal>0)?(1.0-eq/bal)*100.0:0;
         string hb_msg = CAATProtocol::BuildHEARTBEAT(_Symbol, eq, dd);
         if(m_s.Send(hb_msg)) m_l_hb=n;
      }

      // Data Push is only done by DataCollector or Master
      if(m_role != AAT_ROLE_TRADE_EXECUTOR) {
         if(m_l_pr==0 || MathAbs(cp-m_l_pr)>=m_p_th || n-m_l_dp>10) {
            string dp_msg = CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 100);
            if(m_s.Send(dp_msg)) { m_l_dp=n; m_l_pr=cp; }
         }
      }

      Proc();
   }

   void Proc() {
      int limit=0;
      while(limit < 20) {
         string m=m_s.Receive(); if(m=="") break;
         string t=CAATProtocol::GetMsgType(m);

         // Trade Decisions are only processed by TradeExecutor or Master
         if(t=="DECISION" && m_role != AAT_ROLE_DATA_COLLECTOR) {
            string ac=CAATProtocol::GetV(m, "act");
            if(ac!="" && ac!="WAIT") HandleTr(m);
         }
         else if(t=="TELEMETRY") {
            if(m_u_d && m_d_created) {
               string sym=CAATProtocol::GetV(m, "s");
               if(sym == _Symbol || sym == "GLOBAL") {
                  m_d.Render(_Symbol, CAATProtocol::GetV(m, "st"), StringToDouble(CAATProtocol::GetV(m, "scr")), CAATProtocol::GetV(m, "htf"), StringToDouble(CAATProtocol::GetV(m, "dd")));
               }
            }
         }
         limit++;
      }
   }

   void HandleTr(string m) {
      int id=(int)StringToInteger(CAATProtocol::GetV(m, "id")); string s=CAATProtocol::GetV(m, "s"); if(s=="") s=_Symbol;
      string a=CAATProtocol::GetV(m, "act"); double l=StringToDouble(CAATProtocol::GetV(m, "lts"));
      int slp=(int)StringToInteger(CAATProtocol::GetV(m, "sl_p")), tpp=(int)StringToInteger(CAATProtocol::GetV(m, "tp_p"));
      double pt=SymbolInfoDouble(s, SYMBOL_POINT), pr=(a=="BUY")?SymbolInfoDouble(s, SYMBOL_ASK):SymbolInfoDouble(s, SYMBOL_BID);
      double sl=(a=="BUY")?pr-slp*pt:pr+slp*pt, tp=(a=="BUY")?pr+tpp*pt:pr-tpp*pt;
      MqlTradeRequest req; ZeroMemory(req); MqlTradeResult res; ZeroMemory(res);
      req.action=TRADE_ACTION_DEAL; req.symbol=s; req.volume=l; req.type=(a=="BUY")?ORDER_TYPE_BUY:ORDER_TYPE_SELL; req.price=pr;
      req.sl=NormalizeDouble(sl, (int)SymbolInfoInteger(s, SYMBOL_DIGITS)); req.tp=NormalizeDouble(tp, (int)SymbolInfoInteger(s, SYMBOL_DIGITS));
      req.magic=123456; req.comment=StringFormat("AAT:%d", id);
      if(!OrderSendAsync(req, res)) { Print("AAT: OrderSendAsync failed"); }
      m_s.Send(CAATProtocol::BuildTRADE_ACK(id, (int)res.order, IntegerToString(res.retcode)));
   }
};
