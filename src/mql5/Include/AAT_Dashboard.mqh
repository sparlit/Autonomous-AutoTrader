//+------------------------------------------------------------------+
//|                                              AAT_Dashboard.mqh |
//|                                  Copyright 2024, Jules (God Mode)|
//|                                       https://autonomous trader |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
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
   color             m_clr_neon_green;
   color             m_clr_neon_red;
   color             m_clr_text;

public:
                     CAATDashboard();
                    ~CAATDashboard();

   bool              Create(string name, int w, int h);
   void              Render(string symbol, string status, double score, string htf_trend, double drawdown);
   void              DrawHeader();
   void              DrawSection(int x, int y, string title, string val, color clr);
};

CAATDashboard::CAATDashboard() : m_name("AAT_Dash"), m_width(300), m_height(400)
{
   m_clr_bg = C'20,20,20';
   m_clr_neon_green = C'57,255,20';
   m_clr_neon_red = C'FF,49,18';
   m_clr_text = clrWhite;
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
   m_canvas.Erase(ColorToARGB(m_clr_bg, 230));

   DrawHeader();

   int y = 50;
   DrawSection(20, y, "SYMBOL", symbol, m_clr_text); y += 40;

   color signal_clr = (score > 0) ? m_clr_neon_green : (score < 0 ? m_clr_neon_red : m_clr_text);
   DrawSection(20, y, "SIGNAL", (score > 0 ? "BUY" : (score < 0 ? "SELL" : "WAIT")), signal_clr); y += 40;

   DrawSection(20, y, "CONFIDENCE", DoubleToString(MathAbs(score), 1) + "/4.0", signal_clr); y += 40;

   color htf_clr = (htf_trend == "BULLISH") ? m_clr_neon_green : (htf_trend == "BEARISH" ? m_clr_neon_red : m_clr_text);
   DrawSection(20, y, "HTF TREND", htf_trend, htf_clr); y += 40;

   color dd_clr = (drawdown < 2.0) ? m_clr_neon_green : m_clr_neon_red;
   DrawSection(20, y, "DRAWDOWN", DoubleToString(drawdown, 2) + "%", dd_clr); y += 40;

   DrawSection(20, y, "ENGINE", status, m_clr_neon_green);

   m_canvas.Update();
}

void CAATDashboard::DrawHeader()
{
   m_canvas.FillRectangle(0, 0, m_width, 40, ColorToARGB(clrSlateGray, 255));
   m_canvas.TextOut(m_width/2, 20, "PHOENIX GAUNTLET V1.9", ColorToARGB(m_clr_text), TA_CENTER|TA_VCENTER);
}

void CAATDashboard::DrawSection(int x, int y, string title, string val, color clr)
{
   m_canvas.FontSet("Lucida Console", -12, FW_BOLD);
   m_canvas.TextOut(x, y, title + ":", ColorToARGB(clrDimGray));
   m_canvas.FontSet("Lucida Console", -14, FW_BOLD);
   m_canvas.TextOut(x + 120, y - 2, val, ColorToARGB(clr));
}
