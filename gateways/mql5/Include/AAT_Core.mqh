#property copyright "Copyright 2024, Jules (God Mode)"
#property strict
#property version   "3.12"

#include <Trade\Trade.mqh>

class CAATGateway
{
private:
   int m_socket;
   string m_host;
   int m_port;
   CTrade m_trade;
   long m_magic;

public:
   CAATGateway() : m_socket(INVALID_HANDLE), m_magic(2026001) {}

   bool Connect(string host, int port, long magic) {
      m_host = host; m_port = port; m_magic = magic;
      m_trade.SetExpertMagicNumber(m_magic);
      m_socket = SocketCreate();
      if(m_socket == INVALID_HANDLE) return false;
      return SocketConnect(m_socket, host, port, 1000);
   }

   bool SendMessage(string json) {
      if(m_socket == INVALID_HANDLE || !SocketIsConnected(m_socket)) return false;
      string msg = json + "\n";
      uchar data[];
      StringToCharArray(msg, data);
      return (SocketSend(m_socket, data, ArraySize(data)) > 0);
   }

   string ReceiveMessage() {
      if(m_socket == INVALID_HANDLE || !SocketIsConnected(m_socket)) return "";
      uint len = SocketIsReadable(m_socket);
      if(len == 0) return "";
      uchar data[];
      int read = SocketRead(m_socket, data, len, 100);
      if(read <= 0) return "";
      return CharArrayToString(data);
   }

   void PushHeartbeat() {
      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double dd = (balance > 0) ? 100.0 * (1.0 - equity/balance) : 0;
      string hb = "{\"t\":\"HB\",\"e\":" + DoubleToString(equity, 2) + ",\"d\":" + DoubleToString(dd, 2) + "}";
      SendMessage(hb);
   }

   void PushMarketData(string sym) {
      double bid=0, ask=0, vol=0;
      SymbolInfoDouble(sym, SYMBOL_BID, bid);
      SymbolInfoDouble(sym, SYMBOL_ASK, ask);
      SymbolInfoDouble(sym, SYMBOL_VOLUME_REAL, vol);

      string data = "{\"t\":\"DATA\",\"s\":\"" + sym + "\",\"b\":" + DoubleToString(bid, (int)SymbolInfoInteger(sym, SYMBOL_DIGITS)) +
                    ",\"a\":" + DoubleToString(ask, (int)SymbolInfoInteger(sym, SYMBOL_DIGITS)) + ",\"v\":" + DoubleToString(vol, 2) + "}";
      SendMessage(data);
   }

   void HandleOrders(string json_str) {
      if(StringFind(json_str, "\"t\":\"ORD\"") < 0) return;

      string sym = GetJsonValue(json_str, "\"s\":\"");
      string act = GetJsonValue(json_str, "\"act\":\"");
      string v_str = GetJsonValue(json_str, "\"v\":");
      double vol = StringToDouble(v_str);

      if(vol <= 0) vol = 0.01;

      if(act == "BUY") m_trade.Buy(vol, sym);
      else if(act == "SELL") m_trade.Sell(vol, sym);
   }

private:
   string GetJsonValue(string json, string key) {
      int start = StringFind(json, key);
      if(start < 0) return "";
      start += StringLen(key);
      int end = StringFind(json, "\"", start);
      int end_comma = StringFind(json, ",", start);
      int end_brace = StringFind(json, "}", start);

      int final_end = -1;
      if(end > 0) final_end = end;
      if(end_comma > 0 && (final_end == -1 || end_comma < final_end)) final_end = end_comma;
      if(end_brace > 0 && (final_end == -1 || end_brace < final_end)) final_end = end_brace;

      if(final_end < 0) return "";
      return StringSubstr(json, start, final_end - start);
   }
};
