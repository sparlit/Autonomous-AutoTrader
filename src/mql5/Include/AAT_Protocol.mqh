//+------------------------------------------------------------------+
//|                                              AAT_Protocol.mqh |
//|                                  Copyright 2024, Jules (God Mode)|
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property strict

class CAATProtocol
{
public:
   static string     BuildPING();
   static string     BuildHEARTBEAT(string symbol, double equity, double dd);
   static string     BuildOHLC(string symbol, ENUM_TIMEFRAMES tf, double o, double h, double l, double c);

   static string     GetMsgType(string json);
};

string CAATProtocol::BuildPING()
{
   return "{\"type\":\"PING\"}";
}

string CAATProtocol::BuildHEARTBEAT(string symbol, double equity, double dd)
{
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
}

string CAATProtocol::GetMsgType(string json)
{
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
}
