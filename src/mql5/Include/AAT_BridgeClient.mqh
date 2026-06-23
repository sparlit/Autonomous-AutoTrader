#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
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
   CAATBridgeClient() : m_l_hb(0), m_l_dp(0), m_hb_i(10000), m_l_pr(0), m_p_th(0.0005), m_syn(false), m_fs(false), m_u_d(false) { m_t.SetExpertMagicNumber(123456); }
   bool Init(string h, int p, bool ud=false, int hi=10) {
      m_h=h; m_p=p; m_u_d=ud; m_hb_i=hi*1000; m_l_hb=GetTickCount();
      if(m_u_d) {
         m_d.Create("AAT_Dash", 320, 450);
         m_d.Render(_Symbol, "INIT", 0.5, "NEUTRAL", 0.0);
      }
      Print("AAT Bridge Client: Connecting to ", m_h, ":", m_p);
      return m_s.Connect(m_h, m_p, 10000);
   }
   void PerformUpdate() {
      if(!m_s.IsConnected()) {
         if(m_s.Connect(m_h, m_p)) { Print("AAT Bridge: Reconnected."); m_syn=false; }
         else {
            if(m_u_d) m_d.Render(_Symbol, "OFFLINE", 0.5, "NEUTRAL", 0.0);
            if(GetTickCount()-m_l_hb>60000) ActFS();
            return;
         }
      }
      m_fs=false;
      if(!m_syn) {
         if(m_s.Send(CAATProtocol::BuildSYNC(_Symbol))) { m_syn=true; Print("AAT Bridge: SYNC Completed."); }
         return;
      }
      uint n=GetTickCount(); double cp=SymbolInfoDouble(_Symbol, SYMBOL_BID);

      if(n-m_l_hb>m_hb_i) {
         double eq = AccountInfoDouble(ACCOUNT_EQUITY);
         double bal = AccountInfoDouble(ACCOUNT_BALANCE);
         double dd = (bal > 0) ? (1.0 - eq/bal) * 100.0 : 0;
         if(m_s.Send(CAATProtocol::BuildHEARTBEAT(_Symbol, eq, dd))) m_l_hb=n;
      }
      if(m_l_pr==0 || MathAbs(cp-m_l_pr)>=m_p_th || n-m_l_dp>60000) {
         if(m_s.Send(CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 100))) { m_l_dp=n; m_l_pr=cp; }
      }

      Proc();
      if(n%500==0) Cln();
   }
   void Proc() {
      int limit=0;
      while(limit < 20) {
         string m=m_s.Receive(); if(m=="") break;
         string t=CAATProtocol::GetMsgType(m);
         if(t=="DECISION") {
            string dr=CAATProtocol::GetV(m, "drw"); if(dr!="") Drw(dr);
            string mg=CAATProtocol::GetV(m, "mgmt"); if(mg!="") HandleMgmt(mg);
            string ac=CAATProtocol::GetV(m, "act"); if(ac!="" && ac!="WAIT") HandleTr(m);
         }
         else if(t=="TELEMETRY") {
            HandleTlm(m);
         }
         limit++;
      }
   }
   void HandleTlm(string m) {
      if(!m_u_d) return;
      string sym = CAATProtocol::GetV(m, "s"); if(sym == "") sym = _Symbol;
      string st = CAATProtocol::GetV(m, "st");
      double scr = StringToDouble(CAATProtocol::GetV(m, "scr"));
      string htf = CAATProtocol::GetV(m, "htf");
      double dd = StringToDouble(CAATProtocol::GetV(m, "dd"));
      m_d.Render(sym, st, scr, htf, dd);
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
      string s=CAATProtocol::GetV(m, "s"); if(s=="") s=_Symbol;
      string a=CAATProtocol::GetV(m, "act"); double l=StringToDouble(CAATProtocol::GetV(m, "lts"));
      int slp=(int)StringToInteger(CAATProtocol::GetV(m, "sl_p")), tpp=(int)StringToInteger(CAATProtocol::GetV(m, "tp_p"));
      double pt=SymbolInfoDouble(s, SYMBOL_POINT);
      double pr=(a=="BUY")?SymbolInfoDouble(s, SYMBOL_ASK):SymbolInfoDouble(s, SYMBOL_BID);
      double sl=(a=="BUY")?pr-slp*pt:pr+slp*pt, tp=(a=="BUY")?pr+tpp*pt:pr-tpp*pt;
      MqlTradeRequest req; ZeroMemory(req); MqlTradeResult res; ZeroMemory(res);
      req.action=TRADE_ACTION_DEAL; req.symbol=s; req.volume=l;
      req.type=(a=="BUY")?ORDER_TYPE_BUY:ORDER_TYPE_SELL; req.price=pr;
      req.sl=NormalizeDouble(sl, (int)SymbolInfoInteger(s, SYMBOL_DIGITS));
      req.tp=NormalizeDouble(tp, (int)SymbolInfoInteger(s, SYMBOL_DIGITS));
      req.magic=123456; req.comment=StringFormat("AAT:%d", id);
      bool r=OrderSendAsync(req, res);
      m_s.Send(CAATProtocol::BuildTRADE_ACK(id, (int)res.order, r?"":IntegerToString(res.retcode)));
   }
   void ActFS() {
      if(m_fs) return;
      for(int i=PositionsTotal()-1; i>=0; i--) {
         ulong tk=PositionGetTicket(i);
         if(PositionSelectByTicket(tk) && PositionGetString(POSITION_SYMBOL)==_Symbol) {
            double en=PositionGetDouble(POSITION_PRICE_OPEN), tp=PositionGetDouble(POSITION_TP), cu=PositionGetDouble(POSITION_PRICE_CURRENT);
            if(PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY && cu>en+50*_Point) m_t.PositionModify(tk, en+10*_Point, tp);
            else if(PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_SELL && cu<en-50*_Point) m_t.PositionModify(tk, en-10*_Point, tp);
         }
      }
      m_fs=true;
   }
   void Cln() { datetime lt=iTime(_Symbol, _Period, 50); for(int i=ObjectsTotal(0)-1; i>=0; i--) { string n=ObjectName(0, i); if(StringFind(n, "OB_")==0 || StringFind(n, "AAT_")==0) { if((datetime)ObjectGetInteger(0, n, OBJPROP_TIME, 0)<lt) ObjectDelete(0, n); } } }
   void Drw(string j) { if(StringFind(j, "RECTANGLE")>=0) { string n=CAATProtocol::GetV(j, "name"); double t=StringToDouble(CAATProtocol::GetV(j, "top")), b=StringToDouble(CAATProtocol::GetV(j, "bottom")); if(!ObjectCreate(0, n, OBJ_RECTANGLE, 0, TimeCurrent(), t, TimeCurrent()-86400, b)) { ObjectMove(0, n, 0, TimeCurrent(), t); ObjectMove(0, n, 1, TimeCurrent()-86400, b); } ObjectSetInteger(0, n, OBJPROP_COLOR, clrDodgerBlue); ObjectSetInteger(0, n, OBJPROP_BACK, true); } }
};
