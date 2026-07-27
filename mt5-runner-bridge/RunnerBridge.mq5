//+------------------------------------------------------------------+
//|  RunnerBridge.mq5 — nhận tín hiệu Runner CBR+VWAP từ Quantower    |
//|  và vào lệnh trên MT5 (Exness). Cầu nối = FILE.                   |
//+------------------------------------------------------------------+
//  LUỒNG:
//    Quantower/RunnerSignal.cs  ──ghi──►  <Common>\Files\runner_cmd.jsonl
//    EA này (chart XAUUSD)      ──đọc──►  OrderSend  ──ghi──►  runner_ack.csv
//                                                    ──ghi──►  runner_done.txt (id đã xử lý)
//
//  QUAN TRỌNG — KHÔNG dùng giá tuyệt đối của Quantower:
//    Quantower chạy GC/MGC futures, MT5 chạy XAUUSD spot → lệch basis vài chục USD và
//    còn trôi + đảo hợp đồng. Nhưng CẢ HAI báo giá USD/oz nên KHOẢNG CÁCH chuyển 1:1.
//    Vì vậy tín hiệu chỉ mang: hướng + sl_dist (USD/oz) + rr. EA vào MARKET, rồi đặt
//    SL/TP theo GIÁ KHỚP THẬT. Trường src_* chỉ để ghi log đối chiếu, KHÔNG dùng để đặt lệnh.
//
//  AN TOÀN — 3 lớp độc lập:
//    1) Quantower: input "MT5: dry-run" → mỗi dòng có cờ "dry":true → EA chỉ log.
//    2) EA: InpEnableTrading = false (mặc định) → chỉ log.
//    3) EA: chặn lot min vượt InpMaxRiskPct (cực quan trọng với tài khoản cent nhỏ),
//       chặn spread rộng, chặn quá nhiều vị thế, chặn lỗ ngày, chặn tín hiệu cũ.
//+------------------------------------------------------------------+
#property copyright "footprint-tpo"
#property version   "1.00"
#property description "Cau noi Quantower RunnerSignal -> MT5. Doc runner_cmd.jsonl, vao lenh market + SL/TP theo fill."

#include <Trade\Trade.mqh>

enum ENUM_RISK_MODE
  {
   RISK_MIN_LOT  = 0,  // Lot nho nhat cua broker (chay thu)
   RISK_PERCENT  = 1,  // % equity moi lenh
   RISK_FIXED    = 2,  // Lot co dinh
   RISK_MONEY    = 3   // So TIEN co dinh moi lenh (don vi tien tai khoan)
  };

input group "=== CONG TAC CHINH ==="
input bool            InpEnableTrading   = false;              // BAT vao lenh that (false = chi ghi log)
input long            InpMagic           = 20260728;           // Magic number
input bool            InpMarkExistingDone= true;               // Danh dau cac dong dang co la "da xu ly" khi khoi dong

input group "=== FILE CAU NOI ==="
input string          InpCmdFile         = "runner_cmd.jsonl"; // File lenh (Quantower ghi)
input string          InpAckFile         = "runner_ack.csv";   // File ack (EA ghi)
input string          InpDoneFile        = "runner_done.txt";  // File id da xu ly
input bool            InpUseCommonFolder = true;               // Dung thu muc Common\Files (khop mac dinh Quantower)

input group "=== KHOI LUONG / RUI RO ==="
input ENUM_RISK_MODE  InpRiskMode        = RISK_MIN_LOT;       // Cach tinh lot
input double          InpRiskPercent     = 1.0;                // % equity moi lenh (che do RISK_PERCENT)
input double          InpFixedLot        = 0.01;               // Lot co dinh (che do RISK_FIXED)
input double          InpRiskMoney       = 50.0;               // So TIEN rui ro moi lenh (che do RISK_MONEY, don vi tk)
input double          InpMaxRiskPct      = 3.0;                // TRAN CUNG: bo lenh neu rui ro > % equity nay

input group "=== BO LOC AN TOAN ==="
input double          InpMaxSpread       = 0.50;               // Spread toi da (USD/oz), 0 = bo qua
input double          InpMaxSpreadPctOfR = 15.0;               // Bo lenh neu spread > % cua khoang cach SL (chong SL chat)
input int             InpMaxAgeSec       = 120;                // Tuoi tin hieu toi da (giay)
input int             InpDeviationPts    = 300;                // Truot gia cho phep (POINTS, khong phai USD)
input int             InpMaxPositions    = 1;                  // So vi the toi da cua EA
input double          InpMaxDailyLossPct = 6.0;                // Dung giao dich khi lo ngay vuot % (0 = tat)
input bool            InpAllowBuy        = true;               // Cho phep BUY
input bool            InpAllowSell       = true;               // Cho phep SELL
input bool            InpTakeCbr         = true;               // Nhan nhanh CBR (3R)
input bool            InpTakeRev         = true;               // Nhan nhanh QUAY DAU (1.5R)
input bool            InpOnlyGradeA      = false;              // Chi nhan grade A

CTrade   trade;
string   g_done[];
ulong    g_lastSize = 0;
string   g_lastMsg  = "chua co tin hieu";
int      g_traded   = 0;
int      g_skipped  = 0;
bool     g_specWarn = false;

//+------------------------------------------------------------------+
int OnInit()
  {
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpDeviationPts);
   trade.SetTypeFillingBySymbol(_Symbol);

   ArrayResize(g_done, 0);
   LoadDone();
   if(InpMarkExistingDone)
      MarkExistingDone();

   PrintSpec();
   EventSetMillisecondTimer(250);
   ShowPanel();
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   Comment("");
  }

void OnTimer()
  {
   ProcessCmdFile();
   ShowPanel();
  }

//+------------------------------------------------------------------+
//| Doc file lenh — chi doc lai khi kich thuoc doi                    |
//+------------------------------------------------------------------+
void ProcessCmdFile()
  {
   int flags = FILE_READ|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE;
   if(InpUseCommonFolder) flags |= FILE_COMMON;

   int h = FileOpen(InpCmdFile, flags);
   if(h == INVALID_HANDLE)
      return;

   ulong sz = FileSize(h);
   if(sz == g_lastSize) { FileClose(h); return; }
   g_lastSize = sz;

   while(!FileIsEnding(h))
     {
      string line = FileReadString(h);
      if(StringLen(line) < 10) continue;
      string id = JStr(line, "id");
      if(id == "") continue;
      if(IsDone(id)) continue;
      HandleCmd(line, id);
     }
   FileClose(h);
  }

//+------------------------------------------------------------------+
//| Xu ly 1 lenh                                                      |
//+------------------------------------------------------------------+
void HandleCmd(const string line, const string id)
  {
   string  branch  = JStr(line, "branch");
   string  side    = JStr(line, "side");
   string  grade   = JStr(line, "grade");
   string  src     = JStr(line, "src");
   string  ts      = JStr(line, "ts_utc");
   double  slDist  = JNum(line, "sl_dist", 0.0);
   double  rr      = JNum(line, "rr", 0.0);
   bool    dry     = JBool(line, "dry");
   bool    isBuy   = (side == "BUY");

   // --- kiem tra noi dung ---
   if(slDist <= 0.0 || rr <= 0.0 || (side != "BUY" && side != "SELL"))
     { Reject(id, line, "du lieu tin hieu khong hop le"); return; }

   // --- loc nhanh / huong / grade ---
   if(branch == "CBR" && !InpTakeCbr)   { Reject(id, line, "tat nhanh CBR");      return; }
   if(branch == "REV" && !InpTakeRev)   { Reject(id, line, "tat nhanh QUAY DAU"); return; }
   if(isBuy  && !InpAllowBuy)           { Reject(id, line, "tat BUY");            return; }
   if(!isBuy && !InpAllowSell)          { Reject(id, line, "tat SELL");           return; }
   if(InpOnlyGradeA && grade != "A")    { Reject(id, line, "chi nhan grade A");   return; }

   // --- tuoi tin hieu (kiem lai o phia MT5, doc lap voi Quantower) ---
   string tsdot = ts;
   StringReplace(tsdot, "-", ".");
   datetime tsig = StringToTime(tsdot);
   long age = (long)TimeGMT() - (long)tsig;
   if(tsig > 0 && (age > InpMaxAgeSec || age < -InpMaxAgeSec))
     { Reject(id, line, StringFormat("tin hieu cu/lech dong ho %d s", (int)age)); return; }

   // --- dry-run (tu Quantower) hoac EA chua bat ---
   if(dry || !InpEnableTrading)
     {
      string why = dry ? "DRY tu Quantower" : "EA chua bat vao lenh";
      Ack(id, branch, side, "LOG", 0.0, 0.0, 0.0, CurSpread(), 0.0, 0.0, 0.0, why, src, slDist, rr);
      MarkDone(id);
      g_skipped++;
      g_lastMsg = StringFormat("%s %s %s SL %.1f %.1fR -> chi LOG (%s)", ts, branch, side, slDist, rr, why);
      return;
     }

   // --- moi truong giao dich ---
   bool envOk = (TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) != 0)
             && (MQLInfoInteger(MQL_TRADE_ALLOWED) != 0)
             && (AccountInfoInteger(ACCOUNT_TRADE_EXPERT) != 0)
             && (AccountInfoInteger(ACCOUNT_TRADE_ALLOWED) != 0);
   if(!envOk)
     { Reject(id, line, "terminal/tai khoan chua cho phep auto-trade"); return; }

   // --- spread ---
   double spr = CurSpread();
   if(InpMaxSpread > 0.0 && spr > InpMaxSpread)
     { Reject(id, line, StringFormat("spread %.2f > tran %.2f", spr, InpMaxSpread)); return; }
   // Chot quan trong voi nhanh QUAY DAU: SL co the chi 1.1 USD -> spread 0.20 = 18% cua R.
   // Do tren data 5-7/2026: spread 0.20 lam nhanh nay tu +10R xuong +5R.
   if(InpMaxSpreadPctOfR > 0.0 && spr > slDist*InpMaxSpreadPctOfR/100.0)
     {
      Reject(id, line, StringFormat("spread %.2f = %.0f%% cua SL %.2f > tran %.0f%%",
                                    spr, 100.0*spr/slDist, slDist, InpMaxSpreadPctOfR));
      return;
     }

   // --- symbol co cho mo lenh khong (phien dong / chi cho dong lenh) ---
   long tmode = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE);
   if(tmode != SYMBOL_TRADE_MODE_FULL)
     { Reject(id, line, StringFormat("symbol khong cho mo lenh luc nay (trade mode %d)", (int)tmode)); return; }

   // --- so vi the ---
   if(CountMyPositions() >= InpMaxPositions)
     { Reject(id, line, "da du so vi the"); return; }

   // --- lo ngay ---
   double pnlToday = RealizedToday();
   double balance  = AccountInfoDouble(ACCOUNT_BALANCE);
   double dayStart = balance - pnlToday;
   if(InpMaxDailyLossPct > 0.0 && dayStart > 0.0 && pnlToday <= -(InpMaxDailyLossPct/100.0)*dayStart)
     { Reject(id, line, StringFormat("cham tran lo ngay (%.2f)", pnlToday)); return; }

   // --- khoang cach SL toi thieu cua broker ---
   double point   = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   long   stopLvl = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   if(stopLvl > 0 && slDist < stopLvl*point)
     { Reject(id, line, StringFormat("SL %.2f < stops level %.2f", slDist, stopLvl*point)); return; }

   // --- tinh lot ---
   double riskMoney = 0.0, lot = 0.0;
   string lotErr = "";
   if(!CalcLot(slDist, lot, riskMoney, lotErr))
     { Reject(id, line, lotErr); return; }

   // --- vao lenh MARKET, SL/TP dat ngay theo gia hien tai roi hieu chinh theo fill ---
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double refPrice = isBuy ? ask : bid;
   double sl  = NormalizeDouble(isBuy ? refPrice - slDist       : refPrice + slDist,       _Digits);
   double tp  = NormalizeDouble(isBuy ? refPrice + rr*slDist    : refPrice - rr*slDist,    _Digits);
   string cmt = "RB " + branch + " " + TimeToString(TimeCurrent(), TIME_MINUTES);

   bool ok = isBuy ? trade.Buy(lot, _Symbol, 0.0, sl, tp, cmt)
                   : trade.Sell(lot, _Symbol, 0.0, sl, tp, cmt);
   if(!ok)
     {
      Reject(id, line, StringFormat("OrderSend loi %u: %s", trade.ResultRetcode(), trade.ResultRetcodeDescription()));
      return;
     }

   double fill = trade.ResultPrice();
   if(fill <= 0.0) fill = refPrice;
   ulong  pos  = NewestMyPosition();

   // hieu chinh SL/TP theo GIA KHOP THAT (dam bao dung 1R / rr R)
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(pos > 0 && MathAbs(fill - refPrice) > tickSize/2.0)
     {
      double sl2 = NormalizeDouble(isBuy ? fill - slDist    : fill + slDist,    _Digits);
      double tp2 = NormalizeDouble(isBuy ? fill + rr*slDist : fill - rr*slDist, _Digits);
      if(trade.PositionModify(pos, sl2, tp2)) { sl = sl2; tp = tp2; }
     }

   g_traded++;
   MarkDone(id);
   Ack(id, branch, side, "OPEN", lot, refPrice, fill, spr, sl, tp, riskMoney, "ok", src, slDist, rr);
   g_lastMsg = StringFormat("%s %s %s lot %.2f fill %.2f SL %.2f TP %.2f (rui ro %.2f)",
                            ts, branch, side, lot, fill, sl, tp, riskMoney);
   Print("RunnerBridge: ", g_lastMsg);
  }

//+------------------------------------------------------------------+
//| Tien MAT neu chay SL, cho 1.00 lot, tinh theo don vi tien cua tai |
//| khoan. Uu tien OrderCalcProfit (chinh broker tinh) -> dung cho MOI |
//| loai tai khoan (cent / standard) khong can gia dinh contract size. |
//| Du phong: tick value, neu broker khong tra ve.                     |
//+------------------------------------------------------------------+
double RiskPerLot(const double slDist)
  {
   double px = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double prof = 0.0;
   if(px > slDist && OrderCalcProfit(ORDER_TYPE_BUY, _Symbol, 1.0, px, px - slDist, prof) && prof < 0.0)
      return(-prof);

   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickVal  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tickSize > 0.0 && tickVal > 0.0)
      return((slDist/tickSize)*tickVal);
   return(0.0);
  }

//+------------------------------------------------------------------+
//| Tinh lot tu khoang cach SL                                        |
//+------------------------------------------------------------------+
bool CalcLot(const double slDist, double &lot, double &riskMoney, string &err)
  {
   double minLot   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step     = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double equity   = AccountInfoDouble(ACCOUNT_EQUITY);

   if(minLot <= 0.0 || step <= 0.0)
     { err = "khong doc duoc dac ta symbol"; return(false); }

   double riskPerLot = RiskPerLot(slDist);            // tien mat neu SL, cho 1.00 lot
   if(riskPerLot <= 0.0) { err = "khong tinh duoc rui ro/lot"; return(false); }

   if(InpRiskMode == RISK_FIXED)         lot = InpFixedLot;
   else if(InpRiskMode == RISK_MIN_LOT)  lot = minLot;
   else if(InpRiskMode == RISK_MONEY)    lot = InpRiskMoney/riskPerLot;
   else                                  lot = (equity*InpRiskPercent/100.0)/riskPerLot;

   lot = MathFloor(lot/step + 1e-8)*step;              // lam tron XUONG theo step -> khong bao gio vuot rui ro dat ra
   if(lot < minLot) lot = minLot;                      // khong ha duoi lot min -> tran cung ben duoi se kiem
   if(lot > maxLot) lot = maxLot;
   int vd = (step >= 1.0) ? 0 : (step >= 0.1) ? 1 : (step >= 0.01) ? 2 : 3;
   lot = NormalizeDouble(lot, vd);

   riskMoney = lot*riskPerLot;

   // TRAN CUNG — chot an toan quan trong nhat voi tai khoan nho:
   // neu ngay ca lot NHO NHAT cung lam rui ro vuot tran thi BO lenh, khong giao dich.
   if(InpMaxRiskPct > 0.0 && equity > 0.0 && riskMoney > equity*InpMaxRiskPct/100.0)
     {
      err = StringFormat("rui ro %.2f (lot %.2f) = %.1f%% equity > tran %.1f%% -> BO lenh",
                         riskMoney, lot, 100.0*riskMoney/equity, InpMaxRiskPct);
      return(false);
     }
   double margin = 0.0;
   double price  = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(OrderCalcMargin(ORDER_TYPE_BUY, _Symbol, lot, price, margin))
      if(margin > AccountInfoDouble(ACCOUNT_MARGIN_FREE))
        { err = StringFormat("khong du margin (can %.2f, con %.2f)", margin, AccountInfoDouble(ACCOUNT_MARGIN_FREE)); return(false); }
   return(true);
  }

//+------------------------------------------------------------------+
//| Ghi ack + danh dau da xu ly khi BO lenh                           |
//+------------------------------------------------------------------+
void Reject(const string id, const string line, const string why)
  {
   string branch = JStr(line, "branch");
   string side   = JStr(line, "side");
   string src    = JStr(line, "src");
   double slDist = JNum(line, "sl_dist", 0.0);
   double rr     = JNum(line, "rr", 0.0);
   Ack(id, branch, side, "SKIP", 0.0, 0.0, 0.0, CurSpread(), 0.0, 0.0, 0.0, why, src, slDist, rr);
   MarkDone(id);   // tin hieu la lenh vao MARKET tai nen dong -> khong thu lai sau, se vao gia te hon
   g_skipped++;
   g_lastMsg = "BO: " + why;
   Print("RunnerBridge BO [", id, "]: ", why);
  }

//+------------------------------------------------------------------+
void Ack(const string id, const string branch, const string side, const string action,
         const double lot, const double reqPrice, const double fill, const double spread,
         const double sl, const double tp, const double riskMoney, const string reason,
         const string src, const double slDist, const double rr)
  {
   int flags = FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ;
   if(InpUseCommonFolder) flags |= FILE_COMMON;
   int h = FileOpen(InpAckFile, flags);
   if(h == INVALID_HANDLE) { Print("RunnerBridge: khong ghi duoc ", InpAckFile, " loi ", GetLastError()); return; }
   ulong sz = FileSize(h);
   FileSeek(h, 0, SEEK_END);
   if(sz == 0)
      FileWriteString(h, "thoi_diem,id,src,nhanh,huong,hanh_dong,lot,sl_dist,rr,gia_yeu_cau,gia_khop,truot,spread,SL,TP,rui_ro,equity,ly_do\n");
   FileWriteString(h, StringFormat("%s,%s,%s,%s,%s,%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%s\n",
                    TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS), id, src, branch, side, action,
                    lot, slDist, rr, reqPrice, fill, (fill > 0 && reqPrice > 0) ? MathAbs(fill-reqPrice) : 0.0,
                    spread, sl, tp, riskMoney, AccountInfoDouble(ACCOUNT_EQUITY), reason));
   FileClose(h);
  }

//+------------------------------------------------------------------+
//| Danh sach id da xu ly (ben vung qua restart)                      |
//+------------------------------------------------------------------+
void LoadDone()
  {
   int flags = FILE_READ|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE;
   if(InpUseCommonFolder) flags |= FILE_COMMON;
   int h = FileOpen(InpDoneFile, flags);
   if(h == INVALID_HANDLE) return;
   while(!FileIsEnding(h))
     {
      string s = FileReadString(h);
      StringTrimRight(s); StringTrimLeft(s);
      if(StringLen(s) > 0) PushDone(s);
     }
   FileClose(h);
   Print("RunnerBridge: nap ", ArraySize(g_done), " id da xu ly tu ", InpDoneFile);
  }

void MarkExistingDone()
  {
   int flags = FILE_READ|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE;
   if(InpUseCommonFolder) flags |= FILE_COMMON;
   int h = FileOpen(InpCmdFile, flags);
   if(h == INVALID_HANDLE) return;
   int n = 0;
   while(!FileIsEnding(h))
     {
      string line = FileReadString(h);
      string id = JStr(line, "id");
      if(id != "" && !IsDone(id)) { MarkDone(id); n++; }
     }
   g_lastSize = FileSize(h);
   FileClose(h);
   if(n > 0) Print("RunnerBridge: danh dau ", n, " dong CU la da-xu-ly (khong vao lenh)");
  }

void PushDone(const string id)
  {
   int n = ArraySize(g_done);
   ArrayResize(g_done, n+1);
   g_done[n] = id;
  }

bool IsDone(const string id)
  {
   for(int i = ArraySize(g_done)-1; i >= 0; i--)
      if(g_done[i] == id) return(true);
   return(false);
  }

void MarkDone(const string id)
  {
   if(IsDone(id)) return;
   PushDone(id);
   int flags = FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ;
   if(InpUseCommonFolder) flags |= FILE_COMMON;
   int h = FileOpen(InpDoneFile, flags);
   if(h == INVALID_HANDLE) return;
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, id + "\n");
   FileClose(h);
  }

//+------------------------------------------------------------------+
//| Tro giup: doc JSON tho (khong can thu vien)                       |
//+------------------------------------------------------------------+
string JStr(const string src, const string key)
  {
   string pat = "\"" + key + "\":\"";
   int p = StringFind(src, pat);
   if(p < 0) return("");
   p += StringLen(pat);
   int q = StringFind(src, "\"", p);
   if(q < 0) return("");
   return(StringSubstr(src, p, q-p));
  }

double JNum(const string src, const string key, const double def)
  {
   string pat = "\"" + key + "\":";
   int p = StringFind(src, pat);
   if(p < 0) return(def);
   p += StringLen(pat);
   int len = StringLen(src), q = p;
   while(q < len)
     {
      ushort c = StringGetCharacter(src, q);
      if((c >= '0' && c <= '9') || c == '.' || c == '-' || c == '+') q++;
      else break;
     }
   if(q == p) return(def);
   return(StringToDouble(StringSubstr(src, p, q-p)));
  }

bool JBool(const string src, const string key)
  {
   return(StringFind(src, "\"" + key + "\":true") >= 0);
  }

//+------------------------------------------------------------------+
//| Tro giup: tai khoan / vi the                                      |
//+------------------------------------------------------------------+
double CurSpread()
  {
   return(SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));
  }

int CountMyPositions()
  {
   int n = 0;
   for(int i = PositionsTotal()-1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) == InpMagic && PositionGetString(POSITION_SYMBOL) == _Symbol) n++;
     }
   return(n);
  }

ulong NewestMyPosition()
  {
   ulong  best = 0;
   long   bestT = 0;
   for(int i = PositionsTotal()-1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic || PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      long tm = PositionGetInteger(POSITION_TIME_MSC);
      if(tm >= bestT) { bestT = tm; best = t; }
     }
   return(best);
  }

double RealizedToday()
  {
   datetime now  = TimeCurrent();
   datetime from = now - (now % 86400);
   if(!HistorySelect(from, now+60)) return(0.0);
   double sum = 0.0;
   for(int i = HistoryDealsTotal()-1; i >= 0; i--)
     {
      ulong t = HistoryDealGetTicket(i);
      if(t == 0) continue;
      if(HistoryDealGetInteger(t, DEAL_MAGIC) != InpMagic) continue;
      if(HistoryDealGetString(t, DEAL_SYMBOL) != _Symbol) continue;
      sum += HistoryDealGetDouble(t, DEAL_PROFIT) + HistoryDealGetDouble(t, DEAL_SWAP)
           + HistoryDealGetDouble(t, DEAL_COMMISSION);
     }
   return(sum);
  }

//+------------------------------------------------------------------+
//| In dac ta symbol — KIEM TRA BAT BUOC truoc khi chay tien that     |
//+------------------------------------------------------------------+
void PrintSpec()
  {
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickVal  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double minLot   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double contract = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
   double equity   = AccountInfoDouble(ACCOUNT_EQUITY);
   double r3 = RiskPerLot(3.0)*minLot;                 // dung DUNG cong thuc ma CalcLot dung
   double r7 = RiskPerLot(7.0)*minLot;

   PrintFormat("RunnerBridge %s | contract %.2f | tick %.5f | tickValue %.5f | lot min %.2f | digits %d | stops %d",
               _Symbol, contract, tickSize, tickVal, minLot, _Digits, (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL));
   PrintFormat("RunnerBridge equity %.2f %s | don bay 1:%d | LOT MIN: SL 3.0 -> mat %.2f (%.1f%%), SL 7.0 -> mat %.2f (%.1f%%)",
               equity, AccountInfoString(ACCOUNT_CURRENCY), (int)AccountInfoInteger(ACCOUNT_LEVERAGE),
               r3, equity > 0 ? 100.0*r3/equity : 0.0, r7, equity > 0 ? 100.0*r7/equity : 0.0);
   // KIEM TRA TRUOC: voi che do sizing dang chon, lenh SL 3.0 va SL 7.0 se ra lot / rui ro bao nhieu
   double l3 = 0, m3 = 0, l7 = 0, m7 = 0; string e3 = "", e7 = "";
   bool ok3 = CalcLot(3.0, l3, m3, e3), ok7 = CalcLot(7.0, l7, m7, e7);
   PrintFormat("RunnerBridge SIZING (che do %d): SL 3.0 -> lot %.2f rui ro %.2f (%.1f%%) %s | SL 7.0 -> lot %.2f rui ro %.2f (%.1f%%) %s",
               (int)InpRiskMode,
               l3, m3, equity > 0 ? 100.0*m3/equity : 0.0, ok3 ? "OK" : ("=> BO LENH: " + e3),
               l7, m7, equity > 0 ? 100.0*m7/equity : 0.0, ok7 ? "OK" : ("=> BO LENH: " + e7));

   double spr = CurSpread();
   PrintFormat("RunnerBridge exec mode %d | spread hien tai %.3f -> voi tran %.0f%% thi SL toi thieu duoc nhan = %.2f USD"
               " | deviation %d points = %.3f USD",
               (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_EXEMODE), spr, InpMaxSpreadPctOfR,
               InpMaxSpreadPctOfR > 0.0 ? spr/(InpMaxSpreadPctOfR/100.0) : 0.0,
               InpDeviationPts, InpDeviationPts*SymbolInfoDouble(_Symbol, SYMBOL_POINT));
   if(equity > 0 && r7 > equity*InpMaxRiskPct/100.0)
     {
      g_specWarn = true;
      Print("RunnerBridge CANH BAO: lot NHO NHAT da vuot tran rui ro -> EA se BO cac lenh SL rong. ",
            "Can nap them tien, doi loai tai khoan (cent), hoac nang InpMaxRiskPct co y thuc.");
     }
   if(StringFind(_Symbol, "XAU") < 0)
      Print("RunnerBridge CANH BAO: symbol chart khong chua 'XAU' — EA giao dich DUNG symbol cua chart nay.");
  }

//+------------------------------------------------------------------+
void ShowPanel()
  {
   static int    cnt = 0;
   static double pnl = 0.0;
   if(cnt % 8 == 0) pnl = RealizedToday();      // HistorySelect ~2s/lan, khong phai 250ms/lan
   cnt++;
   string st = InpEnableTrading ? "LIVE" : "CHI LOG";
   Comment(StringFormat(
      "RunnerBridge  [%s]  %s\n"
      "vi the: %d/%d   da vao: %d   da bo: %d\n"
      "spread: %.2f   lo/lai ngay: %.2f   equity: %.2f %s\n"
      "%s%s",
      st, _Symbol, CountMyPositions(), InpMaxPositions, g_traded, g_skipped,
      CurSpread(), pnl, AccountInfoDouble(ACCOUNT_EQUITY), AccountInfoString(ACCOUNT_CURRENCY),
      g_lastMsg, g_specWarn ? "\nCANH BAO: lot min vuot tran rui ro — xem tab Experts" : ""));
  }
//+------------------------------------------------------------------+
