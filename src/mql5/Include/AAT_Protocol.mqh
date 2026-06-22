#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property strict

class CAATProtocol
{
public:
   static string BuildPING() { return "{\"t\":\"PNG\"}"; }
   static string BuildHEARTBEAT(string s, double e, double d) { return StringFormat("{\"t\":\"HB\",\"s\":\"%s\",\"e\":%.2f,\"d\":%.2f}", s, e, d); }
   static string BuildDATA_PUSH(string s, ENUM_TIMEFRAMES tf, int c) {
      string h_ltf = BuildH(s, tf, c);
      string h_h1 = BuildH(s, PERIOD_H1, 50);
      string h_h4 = BuildH(s, PERIOD_H4, 30);
      return StringFormat("{\"t\":\"DP\",\"s\":\"%s\",\"tf\":%d,\"bi\":%.5f,\"as\":%.5f,\"tv\":%.5f,\"ts\":%.5f,\"ltf\":%s,\"h1\":%s,\"h4\":%s}",
                          s, (int)tf, SymbolInfoDouble(s, SYMBOL_BID), SymbolInfoDouble(s, SYMBOL_ASK),
                          SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE), SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE), h_ltf, h_h1, h_h4);
   }
   static string BuildTRADE_ACK(int id, int tk, string err) { return StringFormat("{\"t\":\"T_ACK\",\"id\":%d,\"tk\":%d,\"err\":\"%s\"}", id, tk, err); }
   static string BuildSYNC(string s) {
      string tks = "["; bool first = true;
      for(int i=0; i<PositionsTotal(); i++) {
         if(PositionGetSymbol(i) == s) {
            if(!first) tks += ","; tks += IntegerToString(PositionGetInteger(POSITION_TICKET)); first = false;
         }
      }
      tks += "]"; return StringFormat("{\"t\":\"SYNC\",\"s\":\"%s\",\"tk\":%s}", s, tks);
   }
   static string GetMsgType(string j) { string t = GetV(j, "t"); return (t=="HB")?"HEARTBEAT":(t=="DP")?"DATA_PUSH":(t=="PNG")?"PING":(t=="DEC")?"DECISION":(t=="T_ACK")?"TRADE_ACK":(t=="SYNC")?"SYNC":t; }
   static string GetV(string j, string k) {
      string s = "\"" + k + "\":"; int p = StringFind(j, s); if(p<0) return "";
      int st = p + StringLen(s); ushort fc = StringGetCharacter(j, st); int e = -1;
      if(fc == '\"') { st++; e = StringFind(j, "\"", st); }
      else if(fc == '[') { int d = 0; for(int i=st; i<StringLen(j); i++) { ushort c=StringGetCharacter(j, i); if(c=='[') d++; if(c==']') d--; if(d==0) {e=i+1; break;} } }
      else { e = StringFind(j, ",", st); if(e<0) e = StringFind(j, "}", st); }
      if(e<0) return ""; string v = StringSubstr(j, st, e-st); StringReplace(v, "\"", ""); return v;
   }
private:
   static string BuildH(string s, ENUM_TIMEFRAMES tf, int c) {
      MqlRates r[]; ArraySetAsSeries(r, true); int cp = CopyRates(s, tf, 0, c, r);
      string h = "["; for(int i=cp-1; i>=0; i--) { h += StringFormat("[%.5f,%.5f,%.5f,%.5f,%lld,%lld]", r[i].open, r[i].high, r[i].low, r[i].close, r[i].time, r[i].tick_volume); if(i>0) h += ","; }
      h += "]"; return h;
   }
};
