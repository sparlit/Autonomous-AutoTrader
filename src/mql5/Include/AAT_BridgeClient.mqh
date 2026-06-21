#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property strict
#include <AAT_NativeSockets.mqh>
#include <AAT_Protocol.mqh>
#include <Trade\Trade.mqh>
#include <AAT_Dashboard.mqh>

class CAATBridgeClient {
private:
   CAATNativeSocket m_s; CTrade m_t; CAATDashboard m_d;
   string m_h; int m_p; uint m_l_hb, m_l_dp, m_hb_i;
   double m_l_pr, m_p_th; bool m_syn, m_fs, m_u_d;

public:
   CAATBridgeClient() : m_l_hb(0), m_l_dp(0), m_hb_i(10000), m_l_pr(0), m_p_th(0.0005), m_syn(false), m_fs(false), m_u_d(false) {
      m_t.SetExpertMagicNumber(123456);
   }

   bool Init(string h, int p, bool ud=false, int hi=10) {
      m_h=h; m_p=p; m_u_d=ud; m_hb_i=hi*1000; m_l_hb=GetTickCount();
      if(m_u_d) m_d.Create("AAT_Dash", 320, 400);
      return m_s.Connect(m_h, m_p);
   }

   void OnTick() {
      // Tier 1.1 Remediation: Use Timer if possible, but keep OnTick robust
      if(!m_s.IsConnected()) {
         if(m_s.Connect(m_h, m_p)) {
            m_syn=false;
            Print("AAT: Bridge Reconnected.");
         }
         if(GetTickCount()-m_l_hb>60000) ActFS();
         return;
      }

      m_fs=false;

      // Tier 3.1: SYNC Protocol with Adoption
      if(!m_syn) {
         if(m_s.Send(CAATProtocol::BuildSYNC(_Symbol))) m_syn=true;
         return;
      }

      uint n=GetTickCount(); double cp=SymbolInfoDouble(_Symbol, SYMBOL_BID);

      // Periodic Heartbeat
      if(n-m_l_dp>10000) {
         if(m_s.Send(CAATProtocol::BuildHEARTBEAT(_Symbol, AccountInfoDouble(ACCOUNT_EQUITY), 0.0))) m_l_dp=n;
      }

      // Data Push on Threshold or Timeout
      if(m_l_pr==0 || MathAbs(cp-m_l_pr)>=m_p_th || n-m_l_dp>60000) {
         if(m_s.Send(CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 100))) {
            m_l_dp=n; m_l_pr=cp;
         }
      }

      Proc();
      if(n%500==0) Cln();
   }

   void Proc() {
      // Drain entire buffer to handle Tier 1.1 multiple message flaw
      string m;
      while((m = m_s.Receive()) != "") {
         m_l_hb=GetTickCount();
         string t=CAATProtocol::GetMsgType(m);
         if(t=="DECISION") {
            string dr=CAATProtocol::GetV(m, "drw"); if(dr!="") Drw(dr);
            string tl=CAATProtocol::GetV(m, "tlm"); if(tl!="") HandleTlm(tl);
            string mg=CAATProtocol::GetV(m, "mgmt"); if(mg!="") HandleMgmt(mg);
            string ac=CAATProtocol::GetV(m, "act");
            if(ac!="" && ac!="WAIT") HandleTr(m);
         }
      }
   }

   void HandleTlm(string j) {
      if(!m_u_d) return;
      m_d.Render(_Symbol, CAATProtocol::GetV(j, "st"), StringToDouble(CAATProtocol::GetV(j, "scr")), CAATProtocol::GetV(j, "htf"), StringToDouble(CAATProtocol::GetV(j, "dd")));
   }

   void HandleMgmt(string j) {
      string a=CAATProtocol::GetV(j, "act"); long tk=StringToInteger(CAATProtocol::GetV(j, "tk"));
      if(PositionSelectByTicket(tk)) {
         if(a=="CLOSE_PARTIAL") m_t.PositionClosePartial(tk, PositionGetDouble(POSITION_VOLUME)*StringToDouble(CAATProtocol::GetV(j, "pct")));
         else if(a=="MODIFY_SL") m_t.PositionModify(tk, StringToDouble(CAATProtocol::GetV(j, "sl")), PositionGetDouble(POSITION_TP));
      }
   }

   void HandleTr(string m) {
      int id=(int)StringToInteger(CAATProtocol::GetV(m, "id"));
      string a=CAATProtocol::GetV(m, "act");
      double l=StringToDouble(CAATProtocol::GetV(m, "lts"));
      int slp=(int)StringToInteger(CAATProtocol::GetV(m, "sl_p")), tpp=(int)StringToInteger(CAATProtocol::GetV(m, "tp_p"));

      double pr=(a=="BUY")?SymbolInfoDouble(_Symbol, SYMBOL_ASK):SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl=(a=="BUY")?pr-slp*_Point:pr+slp*_Point, tp=(a=="BUY")?pr+tpp*_Point:pr-tpp*_Point;

      MqlTradeRequest req={0}; MqlTradeResult res={0};
      req.action=TRADE_ACTION_DEAL;
      req.symbol=_Symbol;
      req.volume=l;
      req.type=(a=="BUY")?ORDER_TYPE_BUY:ORDER_TYPE_SELL;
      req.price=pr;
      req.sl=sl;
      req.tp=tp;
      req.magic=123456;
      req.comment=StringFormat("AAT:%d", id);

      if(OrderSendAsync(req, res)) {
         // Even if async, we send what we have. SYNC will fix it later if ticket isn't back yet.
         m_s.Send(CAATProtocol::BuildTRADE_ACK(id, (int)res.order, ""));
      } else {
         m_s.Send(CAATProtocol::BuildTRADE_ACK(id, 0, 0.0, IntegerToString(res.retcode)));
      }
   }

   void ActFS() {
      if(m_fs) return;
      for(int i=PositionsTotal()-1; i>=0; i--) {
         if(PositionGetSymbol(i)==_Symbol) {
            ulong tk=PositionGetInteger(POSITION_TICKET);
            double en=PositionGetDouble(POSITION_PRICE_OPEN), tp=PositionGetDouble(POSITION_TP), cu=PositionGetDouble(POSITION_PRICE_CURRENT);
            if(PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY && cu>en+50*_Point) m_t.PositionModify(tk, en+10*_Point, tp);
            else if(PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_SELL && cu<en-50*_Point) m_t.PositionModify(tk, en-10*_Point, tp);
         }
      }
      m_fs=true;
      Print("AAT: FAILSAFE ACTIVATED. TRADES PROTECTED.");
   }

   void Cln() {
      datetime lt=iTime(_Symbol, _Period, 50);
      for(int i=ObjectsTotal(0)-1; i>=0; i--) {
         string n=ObjectName(0, i);
         if(StringFind(n, "OB_")==0 || StringFind(n, "AAT_")==0) {
            if((datetime)ObjectGetInteger(0, n, OBJPROP_TIME, 0)<lt) ObjectDelete(0, n);
         }
      }
   }

   void Drw(string j) {
      if(StringFind(j, "RECTANGLE")>=0) {
         string n=CAATProtocol::GetV(j, "name");
         double t=StringToDouble(CAATProtocol::GetV(j, "top")), b=StringToDouble(CAATProtocol::GetV(j, "bottom"));
         if(!ObjectCreate(0, n, OBJ_RECTANGLE, 0, TimeCurrent(), t, TimeCurrent()-86400, b)) {
            ObjectMove(0, n, 0, TimeCurrent(), t);
            ObjectMove(0, n, 1, TimeCurrent()-86400, b);
         }
         ObjectSetInteger(0, n, OBJPROP_COLOR, clrDodgerBlue);
         ObjectSetInteger(0, n, OBJPROP_BACK, true);
      }
   }
};
