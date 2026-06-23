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
   CAATBridgeClient() : m_l_hb(0), m_l_dp(0), m_hb_i(5000), m_l_pr(0), m_p_th(0.0001), m_syn(false), m_fs(false), m_u_d(false) { m_t.SetExpertMagicNumber(123456); }

   bool Init(string h, int p, bool ud=false, int hi=5) {
      m_h=h; m_p=p; m_u_d=ud; m_hb_i=hi*1000; m_l_hb=GetTickCount();
      if(m_u_d) m_d.Create("AAT_Dash", 320, 450);
      Print("AAT Bridge: Initializing connection to ", m_h, ":", m_p);
      return true;
   }

   void PerformUpdate() {
      if(!m_s.IsConnected()) {
         if(m_s.Connect(m_h, m_p, 5000)) {
            Print("AAT Bridge: Connected to Hive.");
            m_syn=false;
         }
         else {
            if(m_u_d) m_d.Render(_Symbol, "OFFLINE", 0.5, "NEUTRAL", 0.0);
            return;
         }
      }

      if(!m_syn) {
         string sync_msg = CAATProtocol::BuildSYNC(_Symbol);
         if(m_s.Send(sync_msg)) {
            m_syn=true;
            Print("AAT Bridge: SYNC Handshake Completed.");
         }
         return;
      }

      uint n=GetTickCount();
      double cp=SymbolInfoDouble(_Symbol, SYMBOL_BID);

      // Fast Heartbeat (5s)
      if(n-m_l_hb>m_hb_i) {
         double eq=AccountInfoDouble(ACCOUNT_EQUITY), bal=AccountInfoDouble(ACCOUNT_BALANCE);
         double dd=(bal>0)?(1.0-eq/bal)*100.0:0;
         string hb_msg = CAATProtocol::BuildHEARTBEAT(_Symbol, eq, dd);
         if(m_s.Send(hb_msg)) m_l_hb=n;
      }

      // Frequent Data Push (10s or 1 pip change)
      if(m_l_pr==0 || MathAbs(cp-m_l_pr)>=m_p_th || n-m_l_dp>10000) {
         string dp_msg = CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 100);
         if(m_s.Send(dp_msg)) {
            m_l_dp=n;
            m_l_pr=cp;
         }
      }

      Proc();
      if(n%1000==0) Cln();
   }

   void Proc() {
      int limit=0;
      while(limit < 50) {
         string m=m_s.Receive();
         if(m=="") break;

         string t=CAATProtocol::GetMsgType(m);
         if(t=="DECISION") {
            Print("AAT Bridge: Decision received.");
            string dr=CAATProtocol::GetV(m, "drw"); if(dr!="") Drw(dr);
            string mg=CAATProtocol::GetV(m, "mgmt"); if(mg!="") HandleMgmt(mg);
            string ac=CAATProtocol::GetV(m, "act"); if(ac!="" && ac!="WAIT") HandleTr(m);
         }
         else if(t=="TELEMETRY") {
            if(m_u_d) {
               string sym=CAATProtocol::GetV(m, "s"); if(sym=="") sym=_Symbol;
               m_d.Render(sym, CAATProtocol::GetV(m, "st"), StringToDouble(CAATProtocol::GetV(m, "scr")), CAATProtocol::GetV(m, "htf"), StringToDouble(CAATProtocol::GetV(m, "dd")));
            }
         }
         limit++;
      }
   }

   void HandleMgmt(string j) {
      string a=CAATProtocol::GetV(j, "act"); long tk=StringToInteger(CAATProtocol::GetV(j, "tk"));
      if(PositionSelectByTicket(tk)) {
         if(a=="CLOSE_PARTIAL") m_t.PositionClosePartial(tk, PositionGetDouble(POSITION_VOLUME)*StringToDouble(CAATProtocol::GetV(j, "pct")));
         else if(a=="MODIFY_SL") m_t.PositionModify(tk, StringToDouble(CAATProtocol::GetV(j, "sl")), PositionGetDouble(POSITION_TP));
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

      if(!OrderSendAsync(req, res)) {
         Print("AAT Bridge: Trade failed: ", GetLastError());
      }
      m_s.Send(CAATProtocol::BuildTRADE_ACK(id, (int)res.order, IntegerToString(res.retcode)));
   }

   void ActFS() {
      for(int i=PositionsTotal()-1; i>=0; i--) {
         ulong tk=PositionGetTicket(i);
         if(PositionSelectByTicket(tk) && PositionGetString(POSITION_SYMBOL)==_Symbol) {
            double en=PositionGetDouble(POSITION_PRICE_OPEN), tp=PositionGetDouble(POSITION_TP), cu=PositionGetDouble(POSITION_PRICE_CURRENT);
            if(PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY && cu>en+50*_Point) m_t.PositionModify(tk, en+10*_Point, tp);
            else if(PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_SELL && cu<en-50*_Point) m_t.PositionModify(tk, en-10*_Point, tp);
         }
      }
   }

   void Cln() {
      datetime lt=iTime(_Symbol, _Period, 50);
      for(int i=ObjectsTotal(0)-1; i>=0; i--) {
         string n=ObjectName(0, i);
         if(n == "AAT_Dash") continue;
         if(StringFind(n, "OB_")==0 || StringFind(n, "AAT_")==0) {
            if((datetime)ObjectGetInteger(0, n, OBJPROP_TIME, 0)<lt) ObjectDelete(0, n);
         }
      }
   }

   void Drw(string j) {
      if(StringFind(j, "RECTANGLE")>=0) {
         string n=CAATProtocol::GetV(j, "name"); double t=StringToDouble(CAATProtocol::GetV(j, "top")), b=StringToDouble(CAATProtocol::GetV(j, "bottom"));
         if(!ObjectCreate(0, n, OBJ_RECTANGLE, 0, TimeCurrent(), t, TimeCurrent()-86400, b)) { ObjectMove(0, n, 0, TimeCurrent(), t); ObjectMove(0, n, 1, TimeCurrent()-86400, b); }
         ObjectSetInteger(0, n, OBJPROP_COLOR, clrDodgerBlue); ObjectSetInteger(0, n, OBJPROP_BACK, true);
      }
   }
};
