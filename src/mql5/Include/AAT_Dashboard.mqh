#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property strict
#include <Canvas\Canvas.mqh>

class CAATDashboard
{
private:
   CCanvas m_canvas;
   int m_width, m_height;
   string m_name;
   color m_bg, m_hdr, m_grn, m_red, m_txt, m_dim;

public:
   CAATDashboard() : m_name("AAT_Dash"), m_width(320), m_height(450) {
      m_bg = C'15,20,30'; m_hdr = C'30,40,60'; m_grn = C'57,255,20'; m_red = C'FF,49,18'; m_txt = clrWhite; m_dim = clrGray;
   }
   ~CAATDashboard() { m_canvas.Destroy(); }

   bool Create(string name, int w, int h) {
      m_name = name; m_width = w; m_height = h;
      if(!m_canvas.CreateBitmapLabel(m_name, 10, 30, m_width, m_height, COLOR_FORMAT_XRGB_NOALPHA)) return false;
      m_canvas.Erase(ColorToARGB(m_bg, 255));
      m_canvas.Update();
      return true;
   }

   void Render(string symbol, string status, double score, string htf_trend, double drawdown) {
      if(!m_canvas.IsCreate()) return;
      m_canvas.Erase(ColorToARGB(m_bg, 255));
      m_canvas.FillRectangle(0, 0, m_width, 45, ColorToARGB(m_hdr, 255));
      m_canvas.FontSet("Lucida Console", -14, FW_BOLD);
      m_canvas.TextOut(m_width/2, 22, "PHOENIX GAUNTLET PRO", ColorToARGB(m_txt), TA_CENTER|TA_VCENTER);

      int y = 60;
      DrawS(20, y, "SYMBOL", symbol + " [" + EnumToString(_Period) + "]", m_txt); y += 35;
      double pt = SymbolInfoDouble(symbol, SYMBOL_POINT);
      double sp = (pt > 0) ? (SymbolInfoDouble(symbol, SYMBOL_ASK) - SymbolInfoDouble(symbol, SYMBOL_BID)) / pt : 0;
      DrawS(20, y, "SPREAD", DoubleToString(sp, 1) + " pts", (sp > 20 ? m_red : m_txt)); y += 35;

      datetime last_bar = (datetime)SeriesInfoInteger(symbol, _Period, SERIES_LASTBAR_DATE);
      long rem = (long)last_bar + PeriodSeconds(_Period) - (long)TimeCurrent();
      if(rem < 0) rem = 0;
      DrawS(20, y, "CANDLE", StringFormat("%02d:%02d", (int)(rem/60), (int)(rem%60)), clrCyan); y += 35;
      m_canvas.Line(10, y, m_width-10, y, ColorToARGB(m_hdr)); y += 20;

      color s_clr = (score > 0.55) ? m_grn : (score < 0.45 ? m_red : m_txt);
      string bias = (score > 0.55) ? "BULLISH BIAS" : (score < 0.45 ? "BEARISH BIAS" : "NEUTRAL");
      DrawS(20, y, "SIGNAL", bias, s_clr); y += 35;
      DrawS(20, y, "POSTERIOR", DoubleToString(score, 2), s_clr); y += 35;
      color h_clr = (htf_trend == "BULLISH") ? m_grn : (htf_trend == "BEARISH" ? m_red : m_txt);
      DrawS(20, y, "HTF ALIGN", htf_trend, h_clr); y += 35;
      m_canvas.Line(10, y, m_width-10, y, ColorToARGB(m_hdr)); y += 20;

      m_canvas.FontSet("Lucida Console", -11, FW_BOLD);
      m_canvas.TextOut(20, y, "ACCOUNT TELEMETRY", ColorToARGB(m_dim)); y += 25;
      m_canvas.TextOut(20, y, "EQUITY: $" + DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2), ColorToARGB(m_txt)); y += 20;
      m_canvas.TextOut(20, y, "DRAWDOWN: " + DoubleToString(drawdown, 2) + "%", ColorToARGB(drawdown > 2 ? m_red : m_grn)); y += 40;

      m_canvas.FontSet("Lucida Console", -10, FW_NORMAL);
      m_canvas.TextOut(m_width/2, m_height - 15, "ENGINE: " + status, (status == "ACTIVE" ? ColorToARGB(m_grn) : ColorToARGB(m_red)), TA_CENTER);
      m_canvas.Update();
   }

   void DrawS(int x, int y, string t, string v, color c) {
      m_canvas.FontSet("Lucida Console", -11, FW_NORMAL);
      m_canvas.TextOut(x, y, t + ":", ColorToARGB(m_dim));
      m_canvas.FontSet("Lucida Console", -13, FW_BOLD);
      m_canvas.TextOut(x + 110, y - 1, v, ColorToARGB(c));
   }
};
