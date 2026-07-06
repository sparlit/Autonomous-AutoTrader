#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property strict

class CAATProtocol
{
public:
   static string BuildHEARTBEAT(string s, double e, double d, int pc, long seq) {
      double spread = SymbolInfoDouble(s, SYMBOL_ASK) - SymbolInfoDouble(s, SYMBOL_BID);
      double pt = SymbolInfoDouble(s, SYMBOL_POINT);
      double spread_pts = (pt > 0) ? spread / pt : 0;
      datetime candle_end = (datetime)SeriesInfoInteger(s, _Period, SERIES_LASTBAR_DATE) + PeriodSeconds(_Period);
      long remaining = (long)candle_end - (long)TimeCurrent();
      if(remaining < 0) remaining = 0;
      string timer = StringFormat("%02d:%02d", (int)(remaining / 60), (int)(remaining % 60));

      return StringFormat("{\"t\":\"HB\",\"s\":\"%s\",\"eq\":%.2f,\"ba\":%.2f,\"dd\":%.2f,\"pc\":%d,\"sp\":%.1f,\"ct\":\"%s\",\"seq\":%lld}", s, e, AccountInfoDouble(ACCOUNT_BALANCE), d, pc, spread_pts, timer, seq);
   }

   static string BuildDATA_PUSH(string s, ENUM_TIMEFRAMES tf, int c, long seq) {
      // V4.0: Parallel MTF Data Map (M1 to MN1)
      string h_ltf = BuildH(s, tf, 50);

      // Build the MTF Map for the Parallel Engine
      string mtf_map = "{";
      mtf_map += "\"m1\":" + BuildH(s, PERIOD_M1, 30) + ",";
      mtf_map += "\"m5\":" + BuildH(s, PERIOD_M5, 30) + ",";
      mtf_map += "\"m15\":" + BuildH(s, PERIOD_M15, 30) + ",";
      mtf_map += "\"m30\":" + BuildH(s, PERIOD_M30, 30) + ",";
      mtf_map += "\"h1\":" + BuildH(s, PERIOD_H1, 30) + ",";
      mtf_map += "\"h4\":" + BuildH(s, PERIOD_H4, 20) + ",";
      mtf_map += "\"d1\":" + BuildH(s, PERIOD_D1, 15) + ",";
      mtf_map += "\"w1\":" + BuildH(s, PERIOD_W1, 10) + ",";
      mtf_map += "\"mn1\":" + BuildH(s, PERIOD_MN1, 5);
      mtf_map += "}";

      double pt = SymbolInfoDouble(s, SYMBOL_POINT);
      double spread = (pt > 0) ? (SymbolInfoDouble(s, SYMBOL_ASK) - SymbolInfoDouble(s, SYMBOL_BID)) / pt : 0;
      double atr = CalculateATR(s, tf, 14);

      return StringFormat("{\"t\":\"DP\",\"s\":\"%s\",\"tf\":%d,\"bi\":%.5f,\"as\":%.5f,\"sp\":%.1f,\"tv\":%.5f,\"ts\":%.5f,\"atr\":%.5f,\"ltf\":%s,\"mtf\":%s,\"seq\":%lld}",
                          s, (int)tf, SymbolInfoDouble(s, SYMBOL_BID), SymbolInfoDouble(s, SYMBOL_ASK), spread,
                          SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE), SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE),
                          atr, h_ltf, mtf_map, seq);
   }

   static string BuildTRADE_ACK(int id, long tk, string err, long seq) {
      return StringFormat("{\"t\":\"T_ACK\",\"id\":%d,\"tk\":%lld,\"err\":\"%s\",\"seq\":%lld}", id, tk, err, seq);
   }

   static string BuildSYNC(string s, long seq) {
      string tks = "["; bool first = true;
      for(int i=0; i<PositionsTotal(); i++) {
         ulong tk = PositionGetTicket(i);
         if(PositionSelectByTicket(tk) && PositionGetString(POSITION_SYMBOL) == s) {
            if(!first) tks += ",";
            string act = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? "BUY" : "SELL";
            tks += StringFormat("{\"tk\":%lld,\"s\":\"%s\",\"act\":\"%s\",\"vol\":%.2f,\"en\":%.5f,\"tp\":%.5f,\"sl\":%.5f}",
               tk, s, act,
               PositionGetDouble(POSITION_VOLUME),
               PositionGetDouble(POSITION_PRICE_OPEN),
               PositionGetDouble(POSITION_TP),
               PositionGetDouble(POSITION_SL));
            first = false;
         }
      }
      tks += "]"; return StringFormat("{\"t\":\"SYNC\",\"s\":\"%s\",\"tk\":%s,\"seq\":%lld}", s, tks, seq);
   }

   static string GetMsgType(string j) {
      string t = GetV(j, "t");
      if(t == "HB") return "HEARTBEAT";
      if(t == "DP") return "DATA_PUSH";
      if(t == "DEC") return "DECISION";
      if(t == "TLM") return "TELEMETRY";
      if(t == "T_ACK") return "TRADE_ACK";
      if(t == "SYNC") return "SYNC";
      if(t == "SYNC_REQ") return "SYNC_REQ";
      return t;
   }

   static string GetV(string j, string k) {
      string s = "\"" + k + "\":"; int p = StringFind(j, s); if(p<0) return "";
      int st = p + StringLen(s); if(st >= StringLen(j)) return "";

      ushort fc = StringGetCharacter(j, st);
      while(st < StringLen(j)-1 && (fc == ' ' || fc == '\t' || fc == '\r' || fc == '\n' || fc == ':')) {
         st++; fc = StringGetCharacter(j, st);
      }

      int e = -1;
      if(fc == '\"') {
         st++; e = st;
         while(e < StringLen(j)) {
            e = StringFind(j, "\"", e);
            if(e < 0) break;
            if(StringGetCharacter(j, e-1) != 92) break;
            e++;
         }
      }
      else if(fc == '[') {
         int d = 0; for(int i=st; i<StringLen(j); i++) { ushort c=StringGetCharacter(j, i); if(c=='[') d++; if(c==']') d--; if(d==0) {e=i+1; break;} }
      }
      else if(fc == '{') {
         int d = 0; for(int i=st; i<StringLen(j); i++) { ushort c=StringGetCharacter(j, i); if(c=='{') d++; if(c=='}') d--; if(d==0) {e=i+1; break;} }
      }
      else {
         e = StringFind(j, ",", st);
         int end_obj = StringFind(j, "}", st);
         if(e < 0 || (end_obj >= 0 && end_obj < e)) e = end_obj;
      }

      if(e<0) return "";
      string v = StringSubstr(j, st, e-st);
      StringTrimRight(v); StringTrimLeft(v); return v;
   }

private:
   static string BuildH(string s, ENUM_TIMEFRAMES tf, int c) {
      MqlRates r[]; ArraySetAsSeries(r, true); int cp = CopyRates(s, tf, 0, c, r);
      string h = "["; for(int i=cp-1; i>=0; i--) { h += StringFormat("[%.5f,%.5f,%.5f,%.5f,%lld,%lld]", r[i].open, r[i].high, r[i].low, r[i].close, (long)r[i].time, r[i].tick_volume); if(i>0) h += ","; }
      h += "]"; return h;
   }

   static double CalculateATR(string s, ENUM_TIMEFRAMES tf, int period) {
      double buffer[]; ArraySetAsSeries(buffer, true);
      int handle = iATR(s, tf, period);
      if(handle == INVALID_HANDLE) return 0;
      if(CopyBuffer(handle, 0, 0, 1, buffer) > 0) return buffer[0];
      return 0;
   }
};
