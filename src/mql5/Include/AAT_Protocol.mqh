#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property strict

class CAATProtocol
{
public:
   static string BuildHEARTBEAT(string s, double e, double d) {
      double spread = SymbolInfoDouble(s, SYMBOL_ASK) - SymbolInfoDouble(s, SYMBOL_BID);
      double pt = SymbolInfoDouble(s, SYMBOL_POINT);
      double spread_pts = (pt > 0) ? spread / pt : 0;
      datetime candle_end = (datetime)SeriesInfoInteger(s, _Period, SERIES_LASTBAR_DATE) + PeriodSeconds(_Period);
      long remaining = (long)candle_end - (long)TimeCurrent();
      if(remaining < 0) remaining = 0;
      string timer = StringFormat("%02d:%02d", (int)(remaining / 60), (int)(remaining % 60));

      int pos_count = 0;
      for(int i=0; i<PositionsTotal(); i++) {
         ulong tk = PositionGetTicket(i);
         if(PositionSelectByTicket(tk) && PositionGetString(POSITION_SYMBOL) == s) pos_count++;
      }

      string res = "{\"t\":\"HB\",\"s\":\"";
      res += s;
      res += "\",\"e\":";
      res += DoubleToString(e, 2);
      res += ",\"d\":";
      res += DoubleToString(d, 2);
      res += ",\"sp\":";
      res += DoubleToString(spread_pts, 1);
      res += ",\"ct\":\"";
      res += timer;
      res += "\",\"pc\":";
      res += IntegerToString(pos_count);
      res += "}";
      return res;
   }

   static string BuildDATA_PUSH(string s, ENUM_TIMEFRAMES tf, int c) {
      string h_ltf = BuildH(s, tf, c);
      string h_h1 = BuildH(s, PERIOD_H1, 50);
      string h_h4 = BuildH(s, PERIOD_H4, 30);
      double pt = SymbolInfoDouble(s, SYMBOL_POINT);
      double spread = (pt > 0) ? (SymbolInfoDouble(s, SYMBOL_ASK) - SymbolInfoDouble(s, SYMBOL_BID)) / pt : 0;

      string res = "{\"t\":\"DP\",\"s\":\"";
      res += s;
      res += "\",\"tf\":";
      res += IntegerToString((int)tf);
      res += ",\"bi\":";
      res += DoubleToString(SymbolInfoDouble(s, SYMBOL_BID), 5);
      res += ",\"as\":";
      res += DoubleToString(SymbolInfoDouble(s, SYMBOL_ASK), 5);
      res += ",\"sp\":";
      res += DoubleToString(spread, 1);
      res += ",\"tv\":";
      res += DoubleToString(SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE), 5);
      res += ",\"ts\":";
      res += DoubleToString(SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE), 5);
      res += ",\"ltf\":";
      res += h_ltf;
      res += ",\"h1\":";
      res += h_h1;
      res += ",\"h4\":";
      res += h_h4;
      res += "}";
      return res;
   }

   static string BuildTRADE_ACK(int id, int tk, string err) {
      string res = "{\"t\":\"T_ACK\",\"id\":";
      res += IntegerToString(id);
      res += ",\"tk\":";
      res += IntegerToString(tk);
      res += ",\"err\":\"";
      res += err;
      res += "\"}";
      return res;
   }

   static string BuildSYNC(string s) {
      string tks = "["; bool first = true;
      for(int i=0; i<PositionsTotal(); i++) {
         ulong tk = PositionGetTicket(i);
         if(PositionSelectByTicket(tk) && PositionGetString(POSITION_SYMBOL) == s) {
            if(!first) tks += ",";
            string p_str = "{\"tk\":";
            p_str += IntegerToString((long)tk);
            p_str += ",\"type\":";
            p_str += IntegerToString((int)PositionGetInteger(POSITION_TYPE));
            p_str += ",\"vol\":";
            p_str += DoubleToString(PositionGetDouble(POSITION_VOLUME), 2);
            p_str += ",\"tp\":";
            p_str += DoubleToString(PositionGetDouble(POSITION_TP), 5);
            p_str += ",\"sl\":";
            p_str += DoubleToString(PositionGetDouble(POSITION_SL), 5);
            p_str += "}";
            tks += p_str;
            first = false;
         }
      }
      tks += "]";
      string res = "{\"t\":\"SYNC\",\"s\":\"";
      res += s;
      res += "\",\"tk\":";
      res += tks;
      res += "}";
      return res;
   }

   static string GetMsgType(string j) {
      string t = GetV(j, "t");
      if(t == "HB") return "HEARTBEAT";
      if(t == "DP") return "DATA_PUSH";
      if(t == "DEC") return "DECISION";
      if(t == "TLM") return "TELEMETRY";
      if(t == "T_ACK") return "TRADE_ACK";
      if(t == "SYNC") return "SYNC";
      return t;
   }

   static string GetV(string j, string k) {
      string s = "\"" + k + "\":"; int p = StringFind(j, s); if(p<0) return "";
      int st = p + StringLen(s); if(st >= StringLen(j)) return "";
      ushort fc = StringGetCharacter(j, st);
      while((fc == ' ' || fc == '\t' || fc == '\r' || fc == '\n') && st < StringLen(j)-1) { st++; fc = StringGetCharacter(j, st); }
      int e = -1;
      if(fc == '\"') { st++; e = StringFind(j, "\"", st); }
      else if(fc == '[') { int d = 0; for(int i=st; i<StringLen(j); i++) { ushort c=StringGetCharacter(j, i); if(c=='[') d++; if(c==']') d--; if(d==0) {e=i+1; break;} } }
      else if(fc == '{') { int d = 0; for(int i=st; i<StringLen(j); i++) { ushort c=StringGetCharacter(j, i); if(c=='{') d++; if(c=='}') d--; if(d==0) {e=i+1; break;} } }
      else { e = StringFind(j, ",", st); if(e<0) e = StringFind(j, "}", st); }
      if(e<0) return ""; string v = StringSubstr(j, st, e-st); return v;
   }

private:
   static string BuildH(string s, ENUM_TIMEFRAMES tf, int c) {
      MqlRates r[]; ArraySetAsSeries(r, true); int cp = CopyRates(s, tf, 0, c, r);
      string h = "["; for(int i=cp-1; i>=0; i--) {
         string b_str = "[";
         b_str += DoubleToString(r[i].open, 5) + ",";
         b_str += DoubleToString(r[i].high, 5) + ",";
         b_str += DoubleToString(r[i].low, 5) + ",";
         b_str += DoubleToString(r[i].close, 5) + ",";
         b_str += IntegerToString((long)r[i].time) + ",";
         b_str += IntegerToString((long)r[i].tick_volume) + "]";
         h += b_str;
         if(i>0) h += ",";
      }
      h += "]"; return h;
   }
};
