#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://autonomous trader"
#property strict
#include <Canvas\Canvas.mqh>

class CAATDashboard {
private:
   CCanvas m_c; int m_w, m_h;
public:
   // Magic: 83001
   void Create(string n, int w, int h) {
      m_w=w; m_h=h;
      if(!m_c.CreateBitmapLabel(n, 10, 30, m_w, m_h, COLOR_FORMAT_ARGB_NORM)) Print("AAT: Dash Fail");
      m_c.FontSet("Courier New", -120);
   }
   // Magic: 83002
   void Render(string s, string st, double sc, string htf, double dd) {
      m_c.Erase(ColorToARGB(clrBlack, 220));
      m_c.FillRectangle(0, 0, m_w, 40, ColorToARGB(clrSteelBlue, 255));
      m_c.TextOut(10, 10, "🦅 PHOENIX ASCENDANT: " + s, ColorToARGB(clrCyan));

      uint st_clr = (st == "HEALTHY") ? clrLime : clrRed;
      m_c.TextOut(10, 60, "STATUS: " + st, ColorToARGB(st_clr));
      m_c.TextOut(10, 90, "NET BIAS: " + DoubleToString(sc, 0), ColorToARGB(clrWhite));
      m_c.TextOut(10, 120, "HTF TREND: " + htf, ColorToARGB(clrGold));
      m_c.TextOut(10, 150, "CURR DRAWDOWN: " + DoubleToString(dd, 2) + "%", ColorToARGB(clrTomato));

      // Proactive Buttons
      m_c.FillRectangle(10, 190, 150, 230, ColorToARGB(clrDarkRed, 255));
      m_c.TextOut(20, 205, "[ KILL ALL ]", ColorToARGB(clrWhite));

      m_c.Update();
   }
   void ~CAATDashboard() { m_c.Destroy(); }
};
