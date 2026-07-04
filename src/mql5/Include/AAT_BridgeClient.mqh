#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property strict

#include "AAT_NativeSockets.mqh"
#include "AAT_Protocol.mqh"
#include "AAT_Dashboard.mqh"

class CAATBridgeClient
{
private:
   CAATNativeSocket m_socket;
   ENUM_AAT_ROLE    m_role;
   string           m_host;
   int              m_port;
   uint             m_last_hb;
   uint             m_last_dp;
   long             m_seq_tx;

public:
   CAATBridgeClient() : m_last_hb(0), m_last_dp(0), m_seq_tx(0) {}

   bool Init(string host, int port, ENUM_AAT_ROLE role, long magic=123456) {
      m_host = host;
      m_port = port;
      m_role = role;
      return m_socket.Connect(m_host, m_port);
   }

   bool Connect(string host, int port) {
      return m_socket.Connect(host, port);
   }

   bool Send(string data) {
      return m_socket.Send(data);
   }

   string Receive() {
      return m_socket.Receive();
   }

   void Disconnect() {
      m_socket.Disconnect();
   }

   bool IsConnected() {
      return m_socket.IsConnected();
   }

   void PerformUpdate() {
      if(!m_socket.IsConnected()) {
         m_socket.Connect(m_host, m_port);
         return;
      }

      uint now = GetTickCount();

      // Periodic Heartbeat
      if(now - m_last_hb > 5000) {
         m_socket.Send(CAATProtocol::BuildHEARTBEAT(_Symbol, AccountInfoDouble(ACCOUNT_EQUITY), 0, PositionsTotal(), ++m_seq_tx));
         m_last_hb = now;
      }

      // Role-specific Logic
      if(m_role == AAT_ROLE_DATA_COLLECTOR || m_role == AAT_ROLE_MASTER) {
         if(now - m_last_dp > 200) { // 200ms throttle for data push
            m_socket.Send(CAATProtocol::BuildDATA_PUSH(_Symbol, _Period, 30, ++m_seq_tx));
            m_last_dp = now;
         }
      }
   }
};
