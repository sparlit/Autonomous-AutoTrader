//+------------------------------------------------------------------+
//|                                           AAT_NativeSockets.mqh |
//|                                  Copyright 2024, Jules (God Mode)|
<<<<<<< HEAD
//|                                       https://autonomous trader |
=======
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property strict

<<<<<<< HEAD
// Use MT5's built-in Socket functions - no WinAPI required for modern MT5
// This ensures cross-platform compatibility (Linux/Windows via Wine/MT5)

=======
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
class CAATNativeSocket
{
private:
   int               m_socket;
   string            m_host;
   int               m_port;
   uint              m_timeout;
<<<<<<< HEAD
=======
   string            m_receive_buffer;
>>>>>>> origin/aat-phase1-design-final-8550167587809497732

public:
                     CAATNativeSocket();
                    ~CAATNativeSocket();

   bool              Connect(string host, int port, uint timeout_ms=5000);
   void              Disconnect();
   bool              IsConnected();

   bool              Send(string data);
<<<<<<< HEAD
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
=======
   string            ReceiveMessage(); // Returns one complete message from the buffer
};

CAATNativeSocket::CAATNativeSocket() : m_socket(INVALID_HANDLE), m_receive_buffer("")
{
}

>>>>>>> origin/aat-phase1-design-final-8550167587809497732
CAATNativeSocket::~CAATNativeSocket()
{
   Disconnect();
}

<<<<<<< HEAD
//+------------------------------------------------------------------+
//| Connect to Python Server                                         |
//+------------------------------------------------------------------+
=======
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
bool CAATNativeSocket::Connect(string host, int port, uint timeout_ms=5000)
{
   m_host = host;
   m_port = port;
   m_timeout = timeout_ms;

<<<<<<< HEAD
   m_socket = SocketCreate();
   if(m_socket == INVALID_HANDLE)
   {
      Print("AAT: SocketCreate failed. Error: ", GetLastError());
      return false;
   }

   if(!SocketConnect(m_socket, m_host, m_port, m_timeout))
   {
      Print("AAT: SocketConnect failed to ", m_host, ":", m_port, ". Error: ", GetLastError());
=======
   if(m_socket != INVALID_HANDLE) Disconnect();

   m_socket = SocketCreate();
   if(m_socket == INVALID_HANDLE) return false;

   if(!SocketConnect(m_socket, m_host, m_port, m_timeout))
   {
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
      SocketClose(m_socket);
      m_socket = INVALID_HANDLE;
      return false;
   }

   return true;
}

<<<<<<< HEAD
//+------------------------------------------------------------------+
//| Disconnect socket                                                |
//+------------------------------------------------------------------+
=======
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
void CAATNativeSocket::Disconnect()
{
   if(m_socket != INVALID_HANDLE)
   {
      SocketClose(m_socket);
      m_socket = INVALID_HANDLE;
<<<<<<< HEAD
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
=======
      m_receive_buffer = "";
   }
}

bool CAATNativeSocket::IsConnected()
{
   return (m_socket != INVALID_HANDLE);
}

>>>>>>> origin/aat-phase1-design-final-8550167587809497732
bool CAATNativeSocket::Send(string data)
{
   if(m_socket == INVALID_HANDLE) return false;

   string msg = data + "\n";
   uchar buffer[];
   StringToCharArray(msg, buffer, 0, WHOLE_ARRAY, CP_UTF8);

<<<<<<< HEAD
   if(SocketSend(m_socket, buffer, ArraySize(buffer)) < 0)
   {
      Print("AAT: SocketSend failed. Error: ", GetLastError());
=======
   // MT5 StringToCharArray includes null terminator, we don't want it in the stream
   if(SocketSend(m_socket, buffer, ArraySize(buffer)-1) < 0)
   {
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
      Disconnect();
      return false;
   }

   return true;
}

<<<<<<< HEAD
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
=======
string CAATNativeSocket::ReceiveMessage()
{
   if(m_socket == INVALID_HANDLE) return "";

   // 1. Check for existing complete message in buffer
   int end_pos = StringFind(m_receive_buffer, "\n");
   if(end_pos >= 0)
   {
      string msg = StringSubstr(m_receive_buffer, 0, end_pos);
      m_receive_buffer = StringSubstr(m_receive_buffer, end_pos + 1);
      return msg;
   }

   // 2. Read from socket if readable
   uint len = SocketIsReadable(m_socket);
   if(len > 0)
   {
      uchar buffer[];
      int received = SocketRead(m_socket, buffer, len, 10);
      if(received > 0)
      {
         string chunk = CharArrayToString(buffer, 0, received, CP_UTF8);
         m_receive_buffer += chunk;

         end_pos = StringFind(m_receive_buffer, "\n");
         if(end_pos >= 0)
         {
            string msg = StringSubstr(m_receive_buffer, 0, end_pos);
            m_receive_buffer = StringSubstr(m_receive_buffer, end_pos + 1);
            return msg;
         }
      }
      else if(received < 0 && GetLastError() != ERR_NET_SOCKET_NO_DATA)
      {
         Disconnect();
      }
   }

   return "";
>>>>>>> origin/aat-phase1-design-final-8550167587809497732
}
