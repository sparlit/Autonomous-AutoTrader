//+------------------------------------------------------------------+
//|                                              AAT_Protocol.mqh |
//|                                  Copyright 2024, Jules (God Mode)|
<<<<<<< HEAD
//|                                       https://autonomous trader |
=======
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property strict

class CAATProtocol
{
public:
   static string     BuildPING();
   static string     BuildHEARTBEAT(string symbol, double equity, double dd);
<<<<<<< HEAD
   static string     BuildDATA_PUSH(string symbol, ENUM_TIMEFRAMES ltf, int count);
   static string     BuildTRADE_ACK(int id, int ticket, string err);
   static string     BuildSYNC(string symbol);

   static string     GetMsgType(string json);
   static string     GetValue(string json, string key);

private:
   static string     BuildHistoryJSON(string symbol, ENUM_TIMEFRAMES tf, int count);
   static string     CleanValue(string val);
=======
   static string     BuildOHLC(string symbol, ENUM_TIMEFRAMES tf, double o, double h, double l, double c);

   static string     GetMsgType(string json);
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
};

string CAATProtocol::BuildPING()
{
<<<<<<< HEAD
   return "{\"t\":\"PNG\"}";
=======
   return "{\"type\":\"PING\"}";
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
}

string CAATProtocol::BuildHEARTBEAT(string symbol, double equity, double dd)
{
<<<<<<< HEAD
   return StringFormat("{\"t\":\"HB\",\"s\":\"%s\",\"e\":%.2f,\"d\":%.2f}",
                       symbol, equity, dd);
}

string CAATProtocol::BuildHistoryJSON(string symbol, ENUM_TIMEFRAMES tf, int count)
{
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(symbol, tf, 0, count, rates);

   string history = "[";
   for(int i=copied-1; i>=0; i--)
   {
      history += StringFormat("[%.5f,%.5f,%.5f,%.5f,%lld,%lld]",
                              rates[i].open, rates[i].high, rates[i].low, rates[i].close, rates[i].time, rates[i].tick_volume);
      if(i > 0) history += ",";
   }
   history += "]";
   return history;
}

string CAATProtocol::BuildDATA_PUSH(string symbol, ENUM_TIMEFRAMES ltf, int count)
{
   string h_ltf = BuildHistoryJSON(symbol, ltf, count);
   string h_h1 = BuildHistoryJSON(symbol, PERIOD_H1, 50);
   string h_h4 = BuildHistoryJSON(symbol, PERIOD_H4, 30);

   double tick_val = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
   double tick_size = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);

   return StringFormat("{\"t\":\"DP\",\"s\":\"%s\",\"tf\":%d,\"bi\":%.5f,\"as\":%.5f,\"tv\":%.5f,\"ts\":%.5f,\"ltf\":%s,\"h1\":%s,\"h4\":%s}",
                       symbol, (int)ltf, SymbolInfoDouble(symbol, SYMBOL_BID), SymbolInfoDouble(symbol, SYMBOL_ASK),
                       tick_val, tick_size, h_ltf, h_h1, h_h4);
}

string CAATProtocol::BuildTRADE_ACK(int id, int ticket, string err)
{
   return StringFormat("{\"t\":\"T_ACK\",\"id\":%d,\"tk\":%d,\"err\":\"%s\"}", id, ticket, err);
}

string CAATProtocol::BuildSYNC(string symbol)
{
   string tickets = "[";
   bool first = true;
   for(int i=0; i<PositionsTotal(); i++)
   {
      if(PositionGetSymbol(i) == symbol)
      {
         if(!first) tickets += ",";
         tickets += IntegerToString(PositionGetInteger(POSITION_TICKET));
         first = false;
      }
   }
   tickets += "]";
   return StringFormat("{\"t\":\"SYNC\",\"s\":\"%s\",\"tk\":%s}", symbol, tickets);
=======
   return "{\"type\":\"HEARTBEAT\",\"symbol\":\""+symbol+"\","+
          "\"equity\":"+DoubleToString(equity, 2)+","+
          "\"drawdown\":"+DoubleToString(dd, 2)+"}";
}

string CAATProtocol::BuildOHLC(string symbol, ENUM_TIMEFRAMES tf, double o, double h, double l, double c)
{
   return "{\"type\":\"OHLC_PUSH\",\"symbol\":\""+symbol+"\","+
          "\"tf\":"+IntegerToString((int)tf)+","+
          "\"o\":"+DoubleToString(o, 5)+","+
          "\"h\":"+DoubleToString(h, 5)+","+
          "\"l\":"+DoubleToString(l, 5)+","+
          "\"c\":"+DoubleToString(c, 5)+"}";
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
}

string CAATProtocol::GetMsgType(string json)
{
<<<<<<< HEAD
   string t = GetValue(json, "t");
   if(t == "HB") return "HEARTBEAT";
   if(t == "DP") return "DATA_PUSH";
   if(t == "PNG") return "PING";
   if(t == "DEC") return "DECISION";
   if(t == "T_ACK") return "TRADE_ACK";
   if(t == "SYNC") return "SYNC";
   return t;
}

string CAATProtocol::GetValue(string json, string key)
{
   string search = "\"" + key + "\":";
   int pos = StringFind(json, search);
   if(pos < 0) return "";
   int start = pos + StringLen(search);
   uchar first_char = StringGetCharacter(json, start);
   int end = -1;
   if(first_char == '\"') { start++; end = StringFind(json, "\"", start); }
   else if(first_char == '[')
   {
      int depth = 0;
      for(int i = start; i < StringLen(json); i++)
      {
         uchar c = StringGetCharacter(json, i);
         if(c == '[') depth++;
         if(c == ']') depth--;
         if(depth == 0) { end = i + 1; break; }
      }
   }
   else
   {
      end = StringFind(json, ",", start);
      if(end < 0) end = StringFind(json, "}", start);
   }
   if(end < 0) return "";
   return CleanValue(StringSubstr(json, start, end - start));
}

string CAATProtocol::CleanValue(string val)
{
   string cleaned = val;
   StringReplace(cleaned, "\"", "");
   return cleaned;
=======
   int key_pos = StringFind(json, "\"type\":\"");
   if(key_pos < 0) return "";

   int val_start = key_pos + 8;
   int val_end = StringFind(json, "\"", val_start);
   if(val_end < 0) return "";

   string type = StringSubstr(json, val_start, val_end - val_start);

   bool valid = false;
   if(key_pos == 1) valid = true;
   else {
      string prev = StringSubstr(json, key_pos - 1, 1);
      if(prev == "," || prev == "{") valid = true;
   }

   return valid ? type : "";
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
}
