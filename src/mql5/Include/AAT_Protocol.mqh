//+------------------------------------------------------------------+
//|                                              AAT_Protocol.mqh |
//|                                  Copyright 2024, Jules (God Mode)|
//|                                       https://autonomous trader |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property strict

class CAATProtocol
{
public:
   static string     BuildPING();
   static string     BuildHEARTBEAT(string symbol, double equity, double dd);
   static string     BuildDATA_PUSH(string symbol, ENUM_TIMEFRAMES tf, int count);
   static string     BuildTRADE_ACK(int id, int ticket, string err);

   static string     GetMsgType(string json);
   static string     GetValue(string json, string key);

private:
   static string     CleanValue(string val);
};

string CAATProtocol::BuildPING()
{
   return "{\"t\":\"PNG\"}";
}

string CAATProtocol::BuildHEARTBEAT(string symbol, double equity, double dd)
{
   return StringFormat("{\"t\":\"HB\",\"s\":\"%s\",\"e\":%.2f,\"d\":%.2f}",
                       symbol, equity, dd);
}

string CAATProtocol::BuildDATA_PUSH(string symbol, ENUM_TIMEFRAMES tf, int count)
{
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(symbol, tf, 0, count, rates);

   string history = "[";
   for(int i=copied-1; i>=0; i--)
   {
      history += StringFormat("[%.5f,%.5f,%.5f,%.5f,%lld]",
                              rates[i].open, rates[i].high, rates[i].low, rates[i].close, rates[i].time);
      if(i > 0) history += ",";
   }
   history += "]";

   return StringFormat("{\"t\":\"DP\",\"s\":\"%s\",\"tf\":%d,\"bi\":%.5f,\"as\":%.5f,\"h\":%s}",
                       symbol, (int)tf, SymbolInfoDouble(symbol, SYMBOL_BID), SymbolInfoDouble(symbol, SYMBOL_ASK), history);
}

string CAATProtocol::BuildTRADE_ACK(int id, int ticket, string err)
{
   return StringFormat("{\"t\":\"T_ACK\",\"id\":%d,\"tk\":%d,\"err\":\"%s\"}", id, ticket, err);
}

string CAATProtocol::GetMsgType(string json)
{
   string t = GetValue(json, "t");
   if(t == "HB") return "HEARTBEAT";
   if(t == "DP") return "DATA_PUSH";
   if(t == "PNG") return "PING";
   if(t == "DEC") return "DECISION";
   if(t == "T_ACK") return "TRADE_ACK";
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
   if(first_char == '\"')
   {
      start++;
      end = StringFind(json, "\"", start);
   }
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
}
