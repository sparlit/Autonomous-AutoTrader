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
   color m_bg, m_hdr, m_grn, m_red, m_txt, m_dim, m_blu;

public:
   CAATDashboard() : m_name("AAT_Dash"), m_width(320), m_height(500) {
      m_bg = C'15,20,30'; m_hdr = C'30,40,60'; m_grn = C'57,255,20'; m_red = C'FF,49,18'; m_txt = clrWhite; m_dim = clrGray; m_blu = C'0,242,255';
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
      m_canvas.Erase(ColorToARGB(m_bg, 255));
      m_canvas.FillRectangle(0, 0, m_width, 45, ColorToARGB(m_hdr, 255));
      m_canvas.FontSet("Lucida Console", -14, FW_BOLD);
      m_canvas.TextOut(m_width/2, 22, "PHOENIX GAUNTLET V3", ColorToARGB(m_txt), TA_CENTER|TA_VCENTER);

      int y = 60;
      DrawS(20, y, "SYMBOL", symbol + " [" + EnumToString(_Period) + "]", m_blu); y += 30;
      double pt = SymbolInfoDouble(symbol, SYMBOL_POINT);
      double sp = (pt > 0) ? (SymbolInfoDouble(symbol, SYMBOL_ASK) - SymbolInfoDouble(symbol, SYMBOL_BID)) / pt : 0;
      DrawS(20, y, "SPREAD", DoubleToString(sp, 1) + " pts", (sp > 20 ? m_red : m_txt)); y += 30;

      datetime last_bar = (datetime)SeriesInfoInteger(symbol, _Period, SERIES_LASTBAR_DATE);
      long rem = (long)last_bar + PeriodSeconds(_Period) - (long)TimeCurrent();
      if(rem < 0) rem = 0;
      DrawS(20, y, "CANDLE", StringFormat("%02d:%02d", (int)(rem/60), (int)(rem%60)), clrCyan); y += 30;

      // Progress bar for candle
      int bar_w = (int)(m_width - 40);
      double progress = 1.0 - (double)rem / PeriodSeconds(_Period);
      m_canvas.FillRectangle(20, y, 20 + bar_w, y + 5, ColorToARGB(m_hdr));
      m_canvas.FillRectangle(20, y, 20 + (int)(bar_w * progress), y + 5, ColorToARGB(m_blu));
      y += 15;

      m_canvas.Line(10, y, m_width-10, y, ColorToARGB(m_hdr)); y += 15;

      color s_clr = (score > 0.55) ? m_grn : (score < 0.45 ? m_red : m_txt);
      string bias = (score > 0.55) ? "BULLISH BIAS" : (score < 0.45 ? "BEARISH BIAS" : "NEUTRAL");
      DrawS(20, y, "CONFLUENCE", bias, s_clr); y += 30;
      DrawS(20, y, "POSTERIOR", DoubleToString(score, 2), s_clr); y += 30;
      color h_clr = (htf_trend == "BULLISH") ? m_grn : (htf_trend == "BEARISH" ? m_red : m_txt);
      DrawS(20, y, "HTF ALIGN", htf_trend, h_clr); y += 30;
      m_canvas.Line(10, y, m_width-10, y, ColorToARGB(m_hdr)); y += 15;

      m_canvas.FontSet("Lucida Console", -11, FW_BOLD);
      m_canvas.TextOut(20, y, "ACCOUNT ACTUALS", ColorToARGB(m_dim)); y += 25;

      double eq = AccountInfoDouble(ACCOUNT_EQUITY);
      double bal = AccountInfoDouble(ACCOUNT_BALANCE);
      double dd = (bal > 0) ? (1.0 - eq/bal) * 100.0 : 0;
      double ppl = AccountInfoDouble(ACCOUNT_PROFIT);

      DrawS(20, y, "EQUITY", "$" + DoubleToString(eq, 2), m_txt); y += 25;
      DrawS(20, y, "FLOATING", (ppl >= 0 ? "+" : "") + DoubleToString(ppl, 2), (ppl >= 0 ? m_grn : m_red)); y += 25;
      DrawS(20, y, "DRAWDOWN", DoubleToString(dd, 2) + "%", (dd > 2 ? m_red : m_grn)); y += 25;

      // Exposure
      int total_pos = PositionsTotal();
      DrawS(20, y, "POSITIONS", IntegerToString(total_pos), m_blu); y += 35;

      m_canvas.FontSet("Lucida Console", -10, FW_NORMAL);
      m_canvas.TextOut(m_width/2, m_height - 15, "SYSTEM: " + status, (status == "ACTIVE" || status == "OPTIMAL" ? ColorToARGB(m_grn) : ColorToARGB(m_red)), TA_CENTER);
      m_canvas.Update();
   }

   void DrawS(int x, int y, string t, string v, color c) {
      m_canvas.FontSet("Lucida Console", -10, FW_NORMAL);
      m_canvas.TextOut(x, y, t + ":", ColorToARGB(m_dim));
      m_canvas.FontSet("Lucida Console", -11, FW_BOLD);
      m_canvas.TextOut(x + 100, y - 1, v, ColorToARGB(c));
   }
};
