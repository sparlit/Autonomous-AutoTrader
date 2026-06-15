//+------------------------------------------------------------------+
//|                                              AAT_Protocol.mqh |
//|                                  Copyright 2024, Jules (God Mode)|
//|                                       https://autonomous trader |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property strict

// Basic Protocol Definitions
// Minimal JSON-like string builders for zero-dependency serialization

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
   return StringFormat("{\"type\":\"HEARTBEAT\",\"symbol\":\"%s\",\"equity\":%.2f,\"drawdown\":%.2f}",
                       symbol, equity, dd);
}

string CAATProtocol::BuildOHLC(string symbol, ENUM_TIMEFRAMES tf, double o, double h, double l, double c)
{
   return StringFormat("{\"type\":\"OHLC_PUSH\",\"symbol\":\"%s\",\"tf\":%d,\"o\":%.5f,\"h\":%.5f,\"l\":%.5f,\"c\":%.5f}",
                       symbol, (int)tf, o, h, l, c);
}

string CAATProtocol::GetMsgType(string json)
{
   // Very basic type extraction for zero-stub parser
   int pos = StringFind(json, "\"type\":\"");
   if(pos < 0) return "";

   int start = pos + 8;
   int end = StringFind(json, "\"", start);
   if(end < 0) return "";

   return StringSubstr(json, start, end - start);
}
