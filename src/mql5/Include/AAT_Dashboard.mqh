#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property strict
#include <Canvas\Canvas.mqh>

struct Rect { int x1, y1, x2, y2; };

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
   color             m_clr_neon_yellow;
   color             m_clr_text;
   color             m_clr_dim;

   Rect              m_btn_panic;
   Rect              m_btn_pause;
   bool              m_paused;

   double            m_equity_history[];
   int               m_hist_ptr;

public:
                     CAATDashboard();
                    ~CAATDashboard();

   bool              Create(string name, int w, int h);
   void              Render(string symbol, string status, double score, string htf_trend, double drawdown);
   void              DrawHeader();
   void              DrawSection(int x, int y, string title, string val, color clr);
   void              DrawAccountSection(int y);
   void              DrawEquityCurve(int x, int y, int w, int h);
   void              DrawButton(Rect &r, string text, color bg);

   string            OnClick(int x, int y);
   bool              IsPaused() { return m_paused; }
};

CAATDashboard::CAATDashboard() : m_name("AAT_Dash"), m_width(320), m_height(550), m_paused(false), m_hist_ptr(0)
{
   m_clr_bg = C'15,20,30';
   m_clr_header = C'30,40,60';
   m_clr_neon_green = C'57,255,20';
   m_clr_neon_red = C'FF,49,18';
   m_clr_neon_yellow = C'FF,E7,00';
   m_clr_text = clrWhite;
   m_clr_dim = clrGray;
   ArrayResize(m_equity_history, 100);
   ArrayInitialize(m_equity_history, 0);
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

   DrawAccountSection(y); y += 65;

   DrawEquityCurve(20, y, m_width - 40, 60); y += 80;

   m_canvas.Line(10, y, m_width-10, y, ColorToARGB(m_clr_header)); y += 15;

   // Interaction Layer: Buttons
   m_btn_panic.x1 = 20; m_btn_panic.y1 = y; m_btn_panic.x2 = m_width/2 - 10; m_btn_panic.y2 = y + 30;
   DrawButton(m_btn_panic, "PANIC CLOSE", m_clr_neon_red);

   m_btn_pause.x1 = m_width/2 + 10; m_btn_pause.y1 = y; m_btn_pause.x2 = m_width - 20; m_btn_pause.y2 = y + 30;
   DrawButton(m_btn_pause, m_paused ? "RESUME" : "PAUSE BRAIN", m_paused ? m_clr_neon_green : m_clr_neon_yellow);

   y += 45;
   m_canvas.FontSet("Lucida Console", -10, FW_NORMAL);
   m_canvas.TextOut(m_width/2, m_height - 15, "ENGINE: " + status + (m_paused ? " [PAUSED]" : ""), m_clr_neon_green, TA_CENTER);

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

   m_equity_history[m_hist_ptr] = equity;
   m_hist_ptr = (m_hist_ptr + 1) % 100;

   m_canvas.FontSet("Lucida Console", -11, FW_BOLD);
   m_canvas.TextOut(20, y, "ACCOUNT TELEMETRY", ColorToARGB(m_clr_dim));

   y += 25;
   m_canvas.TextOut(20, y, "EQUITY:  $" + DoubleToString(equity, 2), ColorToARGB(m_clr_text));
   y += 20;
   m_canvas.TextOut(20, y, "DRAWDOWN: " + DoubleToString(dd, 2) + "%", ColorToARGB(dd > 2 ? m_clr_neon_red : m_clr_neon_green));
}

void CAATDashboard::DrawEquityCurve(int x, int y, int w, int h)
{
   m_canvas.Rectangle(x, y, x + w, y + h, ColorToARGB(m_clr_header));
   double min_e = m_equity_history[0], max_e = m_equity_history[0];
   for(int i=0; i<100; i++) { if(m_equity_history[i]>0) { min_e = MathMin(min_e, m_equity_history[i]); max_e = MathMax(max_e, m_equity_history[i]); } }
   if(max_e == min_e) return;

   int last_px = -1, last_py = -1;
   for(int i=0; i<100; i++) {
      int idx = (m_hist_ptr + i) % 100;
      if(m_equity_history[idx] == 0) continue;
      int px = x + (int)((double)i / 100.0 * w);
      int py = y + h - (int)((m_equity_history[idx] - min_e) / (max_e - min_e) * h);
      if(last_px != -1) m_canvas.Line(last_px, last_py, px, py, ColorToARGB(m_clr_neon_green));
      last_px = px; last_py = py;
   }
}

void CAATDashboard::DrawButton(Rect &r, string text, color bg)
{
   m_canvas.FillRectangle(r.x1, r.y1, r.x2, r.y2, ColorToARGB(bg, 180));
   m_canvas.FontSet("Lucida Console", -10, FW_BOLD);
   m_canvas.TextOut((r.x1 + r.x2)/2, (r.y1 + r.y2)/2, text, ColorToARGB(m_clr_text), TA_CENTER|TA_VCENTER);
}

string CAATDashboard::OnClick(int x, int y)
{
   // Offset from chart corner (10, 30) - see Create()
   int ox = x - 10, oy = y - 30;
   if(ox >= m_btn_panic.x1 && ox <= m_btn_panic.x2 && oy >= m_btn_panic.y1 && oy <= m_btn_panic.y2) return "PANIC";
   if(ox >= m_btn_pause.x1 && ox <= m_btn_pause.x2 && oy >= m_btn_pause.y1 && oy <= m_btn_pause.y2) { m_paused = !m_paused; return "PAUSE"; }
   return "";
}
