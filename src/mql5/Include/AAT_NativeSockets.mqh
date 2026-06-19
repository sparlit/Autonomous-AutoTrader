//+------------------------------------------------------------------+
//|                                           AAT_NativeSockets.mqh |
//|                                  Copyright 2024, Jules (God Mode)|
//|                                       https://autonomous trader |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property strict

class CAATNativeSocket
{
private:
   int               m_socket;
   string            m_host;
   int               m_port;
   uint              m_timeout;
   string            m_receive_buffer;

public:
                     CAATNativeSocket();
                    ~CAATNativeSocket();

   bool              Connect(string host, int port, uint timeout_ms=5000);
   void              Disconnect();
   bool              IsConnected();

   bool              Send(string data);
   string            Receive();
};

CAATNativeSocket::CAATNativeSocket() : m_socket(INVALID_HANDLE), m_receive_buffer("") {}
CAATNativeSocket::~CAATNativeSocket() { Disconnect(); }

bool CAATNativeSocket::Connect(string host, int port, uint timeout_ms=5000)
{
   m_host = host; m_port = port; m_timeout = timeout_ms;
   if(m_socket != INVALID_HANDLE) Disconnect();
   m_socket = SocketCreate();
   if(m_socket == INVALID_HANDLE) return false;
   if(!SocketConnect(m_socket, m_host, m_port, m_timeout)) { SocketClose(m_socket); m_socket = INVALID_HANDLE; return false; }
   return true;
}

void CAATNativeSocket::Disconnect() { if(m_socket != INVALID_HANDLE) { SocketClose(m_socket); m_socket = INVALID_HANDLE; m_receive_buffer = ""; } }
bool CAATNativeSocket::IsConnected() { return (m_socket != INVALID_HANDLE); }

bool CAATNativeSocket::Send(string data)
{
   if(m_socket == INVALID_HANDLE) return false;
   string msg = data + "\n";
   uchar buffer[];
   StringToCharArray(msg, buffer, 0, WHOLE_ARRAY, CP_UTF8);
   if(SocketSend(m_socket, buffer, ArraySize(buffer)-1) < 0) { Disconnect(); return false; }
   return true;
}

string CAATNativeSocket::Receive()
{
   if(m_socket == INVALID_HANDLE) return "";
   int end_pos = StringFind(m_receive_buffer, "\n");
   if(end_pos >= 0) { string msg = StringSubstr(m_receive_buffer, 0, end_pos); m_receive_buffer = StringSubstr(m_receive_buffer, end_pos + 1); return msg; }
   uint len = SocketIsReadable(m_socket);
   if(len > 0) {
      uchar buffer[];
      int received = SocketRead(m_socket, buffer, len, 10);
      if(received > 0) {
         m_receive_buffer += CharArrayToString(buffer, 0, received, CP_UTF8);
         end_pos = StringFind(m_receive_buffer, "\n");
         if(end_pos >= 0) { string msg = StringSubstr(m_receive_buffer, 0, end_pos); m_receive_buffer = StringSubstr(m_receive_buffer, end_pos + 1); return msg; }
      } else if(received < 0 && GetLastError() != ERR_NET_SOCKET_NO_DATA) { Disconnect(); }
   }
   return "";
}
