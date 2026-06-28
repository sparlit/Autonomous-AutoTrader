#property copyright "Copyright 2024, Jules (God Mode)"
#property strict
class CAATProtocol {
public:
   static string BuildHEARTBEAT(string s, double e, double d) {
      double spread = SymbolInfoDouble(s, SYMBOL_ASK) - SymbolInfoDouble(s, SYMBOL_BID);
      double pt = SymbolInfoDouble(s, SYMBOL_POINT);
      datetime candle_end = (datetime)SeriesInfoInteger(s, _Period, SERIES_LASTBAR_DATE) + PeriodSeconds(_Period);
      long remaining = (long)candle_end - (long)TimeCurrent();
      if(remaining < 0) remaining = 0;
      string timer = StringFormat("%02d:%02d", (int)(remaining / 60), (int)(remaining % 60));
      return StringFormat("{\"t\":\"HB\",\"s\":\"%s\",\"e\":%.2f,\"d\":%.2f,\"sp\":%.1f,\"ct\":\"%s\"}", s, e, d, (pt>0?spread/pt:0), timer);
   }
   static string BuildDATA_PUSH(string s, ENUM_TIMEFRAMES tf, int c) {
      string h_ltf = BuildH(s, tf, c);
      double pt = SymbolInfoDouble(s, SYMBOL_POINT);
      double spr = (pt > 0) ? (SymbolInfoDouble(s, SYMBOL_ASK) - SymbolInfoDouble(s, SYMBOL_BID)) / pt : 0;
      double tv = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE);
      double ts = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE);
      return StringFormat("{\"t\":\"DP\",\"s\":\"%s\",\"tf\":%d,\"bi\":%.5f,\"as\":%.5f,\"sp\":%.1f,\"tv\":%.5f,\"ts\":%.5f,\"ltf\":%s}", s, (int)tf, SymbolInfoDouble(s, SYMBOL_BID), SymbolInfoDouble(s, SYMBOL_ASK), spr, tv, ts, h_ltf);
   }
   static string BuildSYNC(string s) {
      string tks = "["; bool first = true;
      for(int i=0; i<PositionsTotal(); i++) {
         ulong tk = PositionGetTicket(i);
         if(PositionSelectByTicket(tk) && PositionGetString(POSITION_SYMBOL) == s) {
            if(!first) tks += ",";
            tks += StringFormat("{\"tk\":%lld,\"type\":%d,\"vol\":%.2f,\"tp\":%.5f,\"sl\":%.5f}", PositionGetInteger(POSITION_TICKET), PositionGetInteger(POSITION_TYPE), PositionGetDouble(POSITION_VOLUME), PositionGetDouble(POSITION_TP), PositionGetDouble(POSITION_SL));
            first = false;
         }
      }
      tks += "]"; return StringFormat("{\"t\":\"SYNC\",\"s\":\"%s\",\"tk\":%s}", s, tks);
   }
   static string GetMsgType(string j) {
      string t = GetV(j, "t");
      if(t == "HB") return "HEARTBEAT";
      if(t == "DP") return "DATA_PUSH";
      if(t == "DEC") return "DECISION";
      if(t == "TLM") return "TELEMETRY";
      if(t == "SYNC") return "SYNC";
      if(t == "SYNC_REQ") return "SYNC_REQ";
      return t;
   }
   static string GetV(string j, string k) {
      string s = "\"" + k + "\":"; int p = StringFind(j, s); if(p<0) return "";
      int st = p + StringLen(s); while(st < StringLen(j) && (StringGetCharacter(j, st) == ' ' || StringGetCharacter(j, st) == '\"')) st++;
      int e = StringFind(j, ",", st); if(e<0) e = StringFind(j, "}", st);
      if(e<0) return ""; int len = e - st;
      while(len > 0 && (StringGetCharacter(j, st+len-1) == ' ' || StringGetCharacter(j, st+len-1) == '\"')) len--;
      return StringSubstr(j, st, len);
   }
private:
   static string BuildH(string s, ENUM_TIMEFRAMES tf, int c) {
      MqlRates r[]; ArraySetAsSeries(r, true); int cp = CopyRates(s, tf, 0, c, r);
      string h = "[";
      for(int i=cp-1; i>=0; i--) {
         h += StringFormat("{\"o\":%.5f,\"h\":%.5f,\"l\":%.5f,\"c\":%.5f,\"t\":%lld,\"v\":%lld}", r[i].open, r[i].high, r[i].low, r[i].close, (long)r[i].time, r[i].tick_volume);
         if(i>0) h += ",";
      }
      h += "]"; return h;
   }
};
