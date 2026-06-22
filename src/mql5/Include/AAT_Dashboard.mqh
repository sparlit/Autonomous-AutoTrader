#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property strict

#include <Canvas\Canvas.mqh>

class CAATDashboard
{
private:
   CCanvas           m_canvas;
   int               m_width;
   int               m_height;
   string            m_name;

   color             m_clr_bg;
   color             m_clr_header;
   color             m_clr_neon_green;
   color             m_clr_neon_red;
   color             m_clr_text;
   color             m_clr_dim;

public:
                     CAATDashboard();
                    ~CAATDashboard();

   bool              Create(string name, int w, int h);
   void              Render(string symbol, string status, double score, string htf_trend, double drawdown);
   void              DrawHeader();
   void              DrawSection(int x, int y, string title, string val, color clr);
   void              DrawAccountSection(int y);
};

CAATDashboard::CAATDashboard() : m_name("AAT_Dash"), m_width(320), m_height(450)
{
   m_clr_bg = C'15,20,30';
   m_clr_header = C'30,40,60';
   m_clr_neon_green = C'57,255,20';
   m_clr_neon_red = C'FF,49,18';
   m_clr_text = clrWhite;
   m_clr_dim = clrGray;
}

CAATDashboard::~CAATDashboard()
{
   m_canvas.Destroy();
}

bool CAATDashboard::Create(string name, int w, int h)
{
   m_name = name; m_width = w; m_height = h;
   if(!m_canvas.CreateBitmapLabel(m_name, 10, 30, m_width, m_height, COLOR_FORMAT_ARGB_NORMALIZE)) return false;
   return true;
}

void CAATDashboard::Render(string symbol, string status, double score, string htf_trend, double drawdown)
{
   m_canvas.Erase(ColorToARGB(m_clr_bg, 240));

   DrawHeader();

   int y = 60;
   DrawSection(20, y, "SYMBOL", symbol + " [" + EnumToString(_Period) + "]", m_clr_text); y += 35;

   double spread = (SymbolInfoDouble(symbol, SYMBOL_ASK) - SymbolInfoDouble(symbol, SYMBOL_BID)) / SymbolInfoDouble(symbol, SYMBOL_POINT);
   DrawSection(20, y, "SPREAD", DoubleToString(spread, 1) + " pts", (spread > 20 ? m_clr_neon_red : m_clr_text)); y += 35;

   datetime candle_end = (datetime)SeriesInfoInteger(symbol, _Period, SERIES_LASTBAR_DATE) + PeriodSeconds(_Period);
   long remaining = candle_end - TimeCurrent();
   string timer = StringFormat("%02d:%02d", remaining / 60, remaining % 60);
   DrawSection(20, y, "CANDLE", timer, clrCyan); y += 35;

   m_canvas.Line(10, y, m_width-10, y, ColorToARGB(m_clr_header)); y += 20;

   color signal_clr = (score > 0) ? m_clr_neon_green : (score < 0 ? m_clr_neon_red : m_clr_text);
   DrawSection(20, y, "SIGNAL", (score > 0 ? "BULLISH BIAS" : (score < 0 ? "BEARISH BIAS" : "NEUTRAL")), signal_clr); y += 35;

   DrawSection(20, y, "POSTERIOR", DoubleToString(MathAbs(score), 2), signal_clr); y += 35;

   color htf_clr = (htf_trend == "BULLISH") ? m_clr_neon_green : (htf_trend == "BEARISH" ? m_clr_neon_red : m_clr_text);
   DrawSection(20, y, "HTF ALIGN", htf_trend, htf_clr); y += 35;

   m_canvas.Line(10, y, m_width-10, y, ColorToARGB(m_clr_header)); y += 20;

   DrawAccountSection(y); y += 70;

   m_canvas.FontSet("Lucida Console", -10, FW_NORMAL);
   m_canvas.TextOut(m_width/2, m_height - 15, "ENGINE: " + status, ColorToARGB(m_clr_neon_green), TA_CENTER);

   m_canvas.Update();
}

void CAATDashboard::DrawHeader()
{
   m_canvas.FillRectangle(0, 0, m_width, 45, ColorToARGB(m_clr_header, 255));
   m_canvas.FontSet("Lucida Console", -14, FW_BOLD);
   m_canvas.TextOut(m_width/2, 22, "PHOENIX GAUNTLET PRO", ColorToARGB(m_clr_text), TA_CENTER|TA_VCENTER);
}

void CAATDashboard::DrawSection(int x, int y, string title, string val, color clr)
{
   m_canvas.FontSet("Lucida Console", -11, FW_NORMAL);
   m_canvas.TextOut(x, y, title + ":", ColorToARGB(m_clr_dim));
   m_canvas.FontSet("Lucida Console", -13, FW_BOLD);
   m_canvas.TextOut(x + 110, y - 1, val, ColorToARGB(clr));
}

void CAATDashboard::DrawAccountSection(int y)
{
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double dd = (balance > 0) ? (1.0 - equity/balance) * 100.0 : 0;

   m_canvas.FontSet("Lucida Console", -11, FW_BOLD);
   m_canvas.TextOut(20, y, "ACCOUNT TELEMETRY", ColorToARGB(m_clr_dim));

   y += 25;
   m_canvas.TextOut(20, y, "EQUITY:  $" + DoubleToString(equity, 2), ColorToARGB(m_clr_text));
   y += 20;
   m_canvas.TextOut(20, y, "DRAWDOWN: " + DoubleToString(dd, 2) + "%", ColorToARGB(dd > 2 ? m_clr_neon_red : m_clr_neon_green));
}
