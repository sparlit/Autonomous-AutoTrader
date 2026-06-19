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

   static string     GetMsgType(string json);
   static string     GetValue(string json, string key);
};

string CAATProtocol::BuildPING()
{
   return "{\"type\":\"PING\"}";
}

string CAATProtocol::BuildHEARTBEAT(string symbol, double equity, double dd)
{
   return StringFormat("{\"type\":\"HEARTBEAT\",\"symbol\":\"%s\",\"equity\":%.2f,\"drawdown\":%.2f}",
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
      history += StringFormat("{\"o\":%.5f,\"h\":%.5f,\"l\":%.5f,\"c\":%.5f,\"t\":%lld}",
                              rates[i].open, rates[i].high, rates[i].low, rates[i].close, rates[i].time);
      if(i > 0) history += ",";
   }
   history += "]";

   return StringFormat("{\"type\":\"DATA_PUSH\",\"symbol\":\"%s\",\"tf\":%d,\"history\":%s}",
                       symbol, (int)tf, history);
}

string CAATProtocol::GetMsgType(string json)
{
   return GetValue(json, "type");
}

string CAATProtocol::GetValue(string json, string key)
{
   string search = "\"" + key + "\":\"";
   int pos = StringFind(json, search);
   if(pos < 0)
   {
      search = "\"" + key + "\":";
      pos = StringFind(json, search);
      if(pos < 0) return "";
      int start = pos + StringLen(search);
      int end = StringFind(json, ",", start);
      if(end < 0) end = StringFind(json, "}", start);
      if(end < 0) end = StringFind(json, "]", start);
      return StringSubstr(json, start, end - start);
   }

   int start = pos + StringLen(search);
   int end = StringFind(json, "\"", start);
   return StringSubstr(json, start, end - start);
}
