#ifndef AAT_DASHBOARD_MQH
#define AAT_DASHBOARD_MQH

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

   bool Create(string name, int w, int h) { return true; }
   bool IsPaused() { return m_paused; }
   void SetPaused(bool p) { m_paused = p; }
   string OnClick(int x, int y) { return ""; }

   // V4.0 Institutional Render
   void RenderV4(string symbol, double spread, double pl, int pc, double dd, string version) {
      CreateLabel("AAT_Header", "AAT V" + version + " PRO", x_off, y_off, 12, "Verdana Bold", clrWhite);
      CreateLabel("AAT_L_PL", "P&L: $" + DoubleToString(pl, 2), x_off, y_off + 65, 11, "Verdana Bold", (pl >= 0 ? clrLime : clrRed));
      CreateLabel("AAT_L_DD", "DD: " + DoubleToString(dd, 2) + "%", x_off, y_off + 85, 9, "Verdana", (dd < 5 ? clrSkyBlue : clrOrangeRed));
   }

   // V3.3 Legacy/Internal Render
   void RenderV3(string symbol, string status, double score, string htf, double dd) {
       CreateLabel("AAT_Status", "SYNC: " + status, x_off, y_off + 25, 10, "Verdana", clrSpringGreen);
       CreateLabel("AAT_L_DD", "DD: " + DoubleToString(dd, 2) + "%", x_off, y_off + 85, 9, "Verdana", (dd < 5 ? clrSkyBlue : clrOrangeRed));
   }

   void Clear() { ObjectsDeleteAll(0, "AAT_"); }

private:
   void CreateLabel(string name, string text, int x, int y, int size, string font, color clr) {
      if(ObjectFind(0, name) < 0) ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetString(0, name, OBJPROP_TEXT, text);
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
      ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   }
};
#endif
