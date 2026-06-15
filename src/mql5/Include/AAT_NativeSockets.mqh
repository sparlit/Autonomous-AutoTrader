//+------------------------------------------------------------------+
//|                                           AAT_NativeSockets.mqh |
//|                                  Copyright 2024, Jules (God Mode)|
//|                                       https://autonomous trader |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property strict

// Use MT5's built-in Socket functions - no WinAPI required for modern MT5
// This ensures cross-platform compatibility (Linux/Windows via Wine/MT5)

class CAATNativeSocket
{
private:
   int               m_socket;
   string            m_host;
   int               m_port;
   uint              m_timeout;

public:
                     CAATNativeSocket();
                    ~CAATNativeSocket();

   bool              Connect(string host, int port, uint timeout_ms=5000);
   void              Disconnect();
   bool              IsConnected();

   bool              Send(string data);
   string            Receive();
};

//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CAATNativeSocket::CAATNativeSocket() : m_socket(INVALID_HANDLE)
{
}

//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CAATNativeSocket::~CAATNativeSocket()
{
   Disconnect();
}

//+------------------------------------------------------------------+
//| Connect to Python Server                                         |
//+------------------------------------------------------------------+
bool CAATNativeSocket::Connect(string host, int port, uint timeout_ms=5000)
{
   m_host = host;
   m_port = port;
   m_timeout = timeout_ms;

   m_socket = SocketCreate();
   if(m_socket == INVALID_HANDLE)
   {
      Print("AAT: SocketCreate failed. Error: ", GetLastError());
      return false;
   }

   if(!SocketConnect(m_socket, m_host, m_port, m_timeout))
   {
      Print("AAT: SocketConnect failed to ", m_host, ":", m_port, ". Error: ", GetLastError());
      SocketClose(m_socket);
      m_socket = INVALID_HANDLE;
      return false;
   }

   return true;
}

//+------------------------------------------------------------------+
//| Disconnect socket                                                |
//+------------------------------------------------------------------+
void CAATNativeSocket::Disconnect()
{
   if(m_socket != INVALID_HANDLE)
   {
      SocketClose(m_socket);
      m_socket = INVALID_HANDLE;
   }
}

//+------------------------------------------------------------------+
//| Check connection state                                           |
//+------------------------------------------------------------------+
bool CAATNativeSocket::IsConnected()
{
   if(m_socket == INVALID_HANDLE) return false;

   // MT5 doesn't have an IsConnected check, so we rely on handle validity
   // and error handling during Send/Receive
   return true;
}

//+------------------------------------------------------------------+
//| Send string data over socket                                     |
//+------------------------------------------------------------------+
bool CAATNativeSocket::Send(string data)
{
   if(m_socket == INVALID_HANDLE) return false;

   string msg = data + "\n";
   uchar buffer[];
   StringToCharArray(msg, buffer, 0, WHOLE_ARRAY, CP_UTF8);

   if(SocketSend(m_socket, buffer, ArraySize(buffer)) < 0)
   {
      Print("AAT: SocketSend failed. Error: ", GetLastError());
      Disconnect();
      return false;
   }

   return true;
}

//+------------------------------------------------------------------+
//| Receive string data from socket                                  |
//+------------------------------------------------------------------+
string CAATNativeSocket::Receive()
{
   if(m_socket == INVALID_HANDLE) return "";

   uint len = SocketIsReadable(m_socket);
   if(len == 0) return "";

   uchar buffer[];
   int received = SocketRead(m_socket, buffer, len, m_timeout);

   if(received <= 0)
   {
      if(GetLastError() != ERR_NET_SOCKET_NO_DATA)
      {
         Print("AAT: SocketRead failed. Error: ", GetLastError());
         Disconnect();
      }
      return "";
   }

   return CharArrayToString(buffer, 0, received, CP_UTF8);
}
