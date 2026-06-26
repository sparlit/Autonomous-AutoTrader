#property copyright "Copyright 2024, Jules (God Mode)"
#property strict

#include <Trade\Trade.mqh>

class CAATGateway
{
private:
   int m_socket;
   string m_host;
   int m_port;
   CTrade m_trade;

public:
   CAATGateway() : m_socket(INVALID_HANDLE) {}

   bool Connect(string host, int port) {
      m_host = host; m_port = port;
      m_socket = SocketCreate();
      if(m_socket == INVALID_HANDLE) return false;
      return SocketConnect(m_socket, host, port, 1000);
   }

   bool SendMessage(string json) {
      if(m_socket == INVALID_HANDLE) return false;
      string msg = json + "\n";
      uchar data[];
      StringToCharArray(msg, data);
      return (SocketSend(m_socket, data, ArraySize(data)) > 0);
   }

   string ReceiveMessage() {
      if(m_socket == INVALID_HANDLE) return "";
      uint len = SocketIsReadable(m_socket);
      if(len == 0) return "";
      uchar data[];
      SocketRead(m_socket, data, len, 50);
      return CharArrayToString(data);
   }

   void PushHeartbeat() {
      string hb = StringFormat("{\"t\":\"HB\",\"e\":%f,\"d\":%f}",
         AccountInfoDouble(ACCOUNT_EQUITY),
         100.0 * (1.0 - AccountInfoDouble(ACCOUNT_EQUITY)/AccountInfoDouble(ACCOUNT_BALANCE)));
      SendMessage(hb);
   }

   void PushMarketData(string sym) {
      string data = StringFormat("{\"t\":\"DATA\",\"s\":\"%s\",\"b\":%f,\"a\":%f,\"v\":%f}",
         sym, SymbolInfoDouble(sym, SYMBOL_BID), SymbolInfoDouble(sym, SYMBOL_ASK), SymbolInfoDouble(sym, SYMBOL_VOLUME));
      SendMessage(data);
   }

   void HandleOrders(string json) {
      // Basic institutional execution logic
      // In a real scenario, use a proper JSON parser. For now, simple string checks.
      if(StringFind(json, "\"act\":\"BUY\"") >= 0) Execute(ORDER_TYPE_BUY, json);
      else if(StringFind(json, "\"act\":\"SELL\"") >= 0) Execute(ORDER_TYPE_SELL, json);
   }

private:
   void Execute(ENUM_ORDER_TYPE type, string params) {
      // Implementation for institutional trade execution
      double vol = 0.01; // Sourced from params in full version
      if(type == ORDER_TYPE_BUY) m_trade.Buy(vol, _Symbol);
      else m_trade.Sell(vol, _Symbol);
   }
};
