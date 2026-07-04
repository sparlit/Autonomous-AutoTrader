#property copyright "Copyright 2024, Jules (God Mode)"
#property link      "https://github.com/sparlit/Autonomous-AutoTrader"
#property strict

class CAATDashboard
{
private:
   int x_off;
   int y_off;
   color base_color;
   bool m_paused;

public:
   CAATDashboard(int x=10, int y=30) : x_off(x), y_off(y), m_paused(false) {
      base_color = clrDodgerBlue;
   }

   bool Create(string name, int w, int h) {
      return true;
   }

   bool IsPaused() { return m_paused; }

   string OnClick(int x, int y) {
      return "";
   }

   // V4.0 Render
   void Render(string symbol, double spread, double pl, int pc, double dd, string version) {
      CreateLabel("AAT_Header", "AUTONOMOUS AUTOTRADER V" + version, x_off, y_off, 12, "Verdana Bold", clrWhite);
      CreateLabel("AAT_Status", "SYSTEM STATUS: OPTIMAL", x_off, y_off + 25, 10, "Verdana", clrSpringGreen);
      CreateLabel("AAT_L_Spread", "Spread: " + DoubleToString(spread, 1) + " pts", x_off, y_off + 50, 9, "Verdana", clrSkyBlue);
      CreateLabel("AAT_L_PL", "Total P&L: $" + DoubleToString(pl, 2), x_off, y_off + 65, 11, "Verdana Bold", (pl >= 0 ? clrLime : clrRed));
      CreateLabel("AAT_L_DD", "Drawdown: " + DoubleToString(dd, 2) + "%", x_off, y_off + 85, 9, "Verdana", (dd < 5 ? clrSkyBlue : clrOrangeRed));
      CreateLabel("AAT_L_PC", "Positions: " + IntegerToString(pc), x_off, y_off + 100, 9, "Verdana", clrSkyBlue);
      CreateLabel("AAT_Footer", "GOD MODE - INSTITUTIONAL PRO", x_off, y_off + 125, 8, "Verdana", clrGray);
   }

   // V3.3/Internal Status Render
   void Render(string s, string st, double scr, string htf, double dd) {
       CreateLabel("AAT_Status", "SYNC STATUS: " + st, x_off, y_off + 25, 10, "Verdana", clrSpringGreen);
       CreateLabel("AAT_L_DD", "Drawdown: " + DoubleToString(dd, 2) + "%", x_off, y_off + 85, 9, "Verdana", (dd < 5 ? clrSkyBlue : clrOrangeRed));
   }

   void Clear() {
      ObjectsDeleteAll(0, "AAT_");
   }

private:
   void CreateLabel(string name, string text, int x, int y, int size, string font, color clr) {
      if(ObjectFind(0, name) < 0) {
         ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
         ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, name, OBJPROP_ANCHOR, ANCHOR_LEFT_UPPER);
      }
      ObjectSetString(0, name, OBJPROP_TEXT, text);
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
      ObjectSetInteger(0, name, OBJPROP_FONTSIZE, size);
      ObjectSetString(0, name, OBJPROP_FONT, font);
      ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   }
};
