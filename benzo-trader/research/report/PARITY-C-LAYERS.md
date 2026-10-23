# PARITY C# <-> Python — setup C va cac lop moi (file 90d GCZ26, tu phien 2026-07-29)

Python: setup_c_v7.run_all_v7 (C0/C4/C6), mo phong 1 lenh mo bang kernel.simulate. Cot "Python (tat ca)" = so lenh dong khong loc gi (so da bao trong RESULTS).
"Python (luat mo ao)" = bo cac entry trong 19:20-20:30 TRUOC khi mo phong (engine C# khong phat tin hieu o do, nen cung khong chiem cho lenh mo). Khop = cung (gio mo nen vao, chieu) VA entry/SL/TP giong nhau (1e-6).

| cau hinh | Python (tat ca) | Python (luat mo ao) | C# | khop hoan toan | khop gio+chieu nhung khac gia | chi Python | chi C# | khop ket qua |
|---|---|---|---|---|---|---|---|---|
| C0 TP chinh (`C:e`) | 103 (da bao 103) | 90 | 90 | 90 | 0 | 0 | 0 | 90 / 90 |
| C4 TP chinh (`C:gthe`) | 191 (da bao 191) | 175 | 175 | 175 | 0 | 0 | 0 | 175 / 175 |
| C6 TP chinh (`C:gthse`) | 555 (da bao 555) | 531 | 531 | 531 | 0 | 0 | 0 | 531 / 531 |
| C0 fixed2 (`C`) | 121 | 99 | 99 | 99 | 0 | 0 | 0 | 99 / 99 |
| C4 fixed2 (`C:gth`) | 220 | 193 | 193 | 193 | 0 | 0 | 0 | 193 / 193 |
| C6 fixed2 (`C:gths`) | 700 | 652 | 652 | 652 | 0 | 0 | 0 | 652 / 652 |

## Chi tiet lech

(khong lech)
