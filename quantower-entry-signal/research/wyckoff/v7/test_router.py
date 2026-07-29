"""
TEST TONG HOP cho ROUTER 1-VI-THE  (AUDIT_V7 §13, dieu kien bat buoc #2 truoc khi port sang C#).

VI SAO PHAI CO FILE NAY:
  Tren du lieu that 5-7/2026, nhanh "bo tin hieu vi dang co vi the" bo **0 lenh** (AUDIT_V7 §11.2:
  trung vi giu lenh chi 9 phut, cac tin hieu khong bao gio chong nhau). Nghia la doan code do
  CHUA TUNG DUOC MOT DIEM DU LIEU NAO KIEM. Neu no sai, backtest van cho dung so, nhung live
  se hanh xu khac -> loai loi im lang nhat.

  => Test o day dung DU LIEU TONG HOP tu tao, ep nhanh do phai chay.

CHAY:  python3 test_router.py     (khong can du lieu that, khong can mang)
Ky vong: in "==> TAT CA <n> TEST PASS" va exit 0. Bat ky FAIL nao => exit 1.

Test nay dong bang HANH VI THAM CHIEU. Khi port sang C# (GD9), RunnerSignal.cs phai cho
ket qua GIONG HET tren cung cac ca duoi day — dung lam bang doi chieu parity.
"""
import sys, os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine

T0 = datetime(2026, 5, 4, 8, 0)          # moc thoi gian gia, khong lien quan du lieu that


def sig(branch, prio, t_in, t_out, r=1.0, side='LONG'):
    """Tao 1 tin hieu tong hop: vao o phut t_in, dong o phut t_out (phut tinh tu T0)."""
    return dict(branch=branch, prio=prio, dt=T0 + timedelta(minutes=t_in),
                exit_dt=T0 + timedelta(minutes=t_out), r=r, side=side,
                ym='2026-05', tag=f"{branch}@{t_in}")


CASES = []


def case(name, sigs, want_tags, want_dropped):
    CASES.append((name, sigs, want_tags, want_dropped))


# ---------------------------------------------------------------- 1. Ca co so
case("1. Khong chong nhau -> giu tat ca (day la TAT CA nhung gi du lieu that kiem duoc)",
     [sig('KB1', 1, 0, 10), sig('KB2', 2, 20, 30), sig('KB3', 3, 40, 50)],
     ['KB1@0', 'KB2@20', 'KB3@40'], {})

# ---------------------------------------------------------------- 2. NHANH CHUA TUNG DUOC KIEM
case("2. ⭐ Chong nhau hoan toan -> tin hieu thu 2 BI BO",
     [sig('KB1', 1, 0, 60), sig('KB2', 2, 10, 20)],
     ['KB1@0'], {'KB2': 1})

case("3. ⭐ Nhieu tin hieu bi bo trong 1 lenh dai",
     [sig('KB1', 1, 0, 100), sig('KB2', 2, 10, 20), sig('KB2', 2, 30, 40), sig('KB3', 3, 50, 60)],
     ['KB1@0'], {'KB2': 2, 'KB3': 1})

case("4. ⭐ Vao DUNG phut dong lenh cu -> BI BO (luat '<=', bao thu)",
     [sig('KB1', 1, 0, 30), sig('KB2', 2, 30, 40)],
     ['KB1@0'], {'KB2': 1})

case("5. ⭐ Vao 1 phut SAU khi dong -> DUOC VAO",
     [sig('KB1', 1, 0, 30), sig('KB2', 2, 31, 40)],
     ['KB1@0', 'KB2@31'], {})

# ---------------------------------------------------------------- 6. Uu tien khi trung phut
case("6. ⭐ Cung phut vao: prio nho hon thang, cai kia bi bo",
     [sig('KB3', 3, 5, 15), sig('KB1', 1, 5, 25)],
     ['KB1@5'], {'KB3': 1})

case("7. ⭐ Cung phut, 3 nhanh: chi KB1 vao",
     [sig('KB2', 2, 5, 9), sig('KB3', 3, 5, 9), sig('KB1', 1, 5, 9)],
     ['KB1@5'], {'KB2': 1, 'KB3': 1})

# ---------------------------------------------------------------- 8. Khong xep hang
case("8. ⭐ KHONG xep hang: bo la bo han, khong vao lai sau khi lenh cu dong",
     [sig('KB1', 1, 0, 50), sig('KB2', 2, 10, 90)],
     ['KB1@0'], {'KB2': 1})

case("9. ⭐ Chuoi lien tiep: moi lenh chan lenh ke tiep, so le duoc vao",
     [sig('KB1', 1, 0, 10), sig('KB2', 2, 5, 15), sig('KB1', 1, 11, 20),
      sig('KB2', 2, 18, 25), sig('KB1', 1, 21, 30)],
     ['KB1@0', 'KB1@11', 'KB1@21'], {'KB2': 2})

# ---------------------------------------------------------------- 10. Bien
case("10. Rong -> khong loi, khong lenh",
     [], [], {})

case("11. Mot tin hieu duy nhat",
     [sig('KB2', 2, 7, 9)], ['KB2@7'], {})

case("12. ⭐ Lenh dai 1 phut (vao=dong): tin hieu ngay sau BI BO, sau nua duoc vao",
     [sig('KB1', 1, 0, 0), sig('KB2', 2, 0, 5), sig('KB3', 3, 1, 5)],
     ['KB1@0', 'KB3@1'], {'KB2': 1})

case("13. ⭐ Vao TRUOC lenh dang mo nhung input KHONG sap xep san -> router phai tu sort",
     [sig('KB2', 2, 40, 50), sig('KB1', 1, 0, 45)],
     ['KB1@0'], {'KB2': 1})


# ================================================================= chay
def main():
    npass = nfail = 0
    for name, sigs, want_tags, want_dropped in CASES:
        kept, dropped = engine.route_one_position(sigs)
        got_tags = [s['tag'] for s in kept]
        got_dropped = dict(dropped)
        ok = (got_tags == want_tags) and (got_dropped == want_dropped)
        if ok:
            npass += 1
            print(f"PASS  {name}")
        else:
            nfail += 1
            print(f"FAIL  {name}")
            print(f"        kept    mong doi {want_tags}")
            print(f"        kept    thuc te  {got_tags}")
            print(f"        dropped mong doi {want_dropped}")
            print(f"        dropped thuc te  {got_dropped}")

    # ---- kiem tinh chat bat bien tren du lieu tong hop lon (khong chi ca le)
    print()
    print("--- Kiem 2 tinh chat bat bien tren 300 tin hieu tong hop chong nhau day dac ---")
    big = []
    for k in range(300):                              # vao moi 3 phut, giu 7 phut => chong nhau nhieu
        big.append(sig('KB1' if k % 2 == 0 else 'KB2', 1 if k % 2 == 0 else 2, k * 3, k * 3 + 7))
    kept, dropped = engine.route_one_position(big)

    # tinh chat 1: khong mot cap lenh nao chong thoi gian
    overlap = 0
    for a, b in zip(kept, kept[1:]):
        if b['dt'] <= a['exit_dt']:
            overlap += 1
    # tinh chat 2: khong mat lenh (giu + bo = tong)
    total_out = len(kept) + sum(dropped.values())

    for label, got, want in [("so cap lenh CHONG thoi gian", overlap, 0),
                             ("giu + bo = tong dau vao", total_out, len(big))]:
        if got == want:
            npass += 1; print(f"PASS  {label}: {got} (mong doi {want})")
        else:
            nfail += 1; print(f"FAIL  {label}: {got} (mong doi {want})")
    print(f"      (thong tin: giu {len(kept)}/{len(big)}, bo {dict(dropped)})")

    print()
    if nfail:
        print(f"==> {nfail} TEST FAIL / {npass+nfail} — ROUTER CHUA DUNG, KHONG DUOC PORT SANG C#")
        return 1
    print(f"==> TAT CA {npass} TEST PASS — router 1-vi-the dung nhu dac ta AUDIT_V7 §11.2")
    return 0


if __name__ == '__main__':
    sys.exit(main())
