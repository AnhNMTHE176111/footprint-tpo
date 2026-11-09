# Parity of_signals.py ↔ C# (StackedImbalance.cs + ExhaustionLogic.cs) — GĐ0

- Dữ liệu: `fp_GCZ26_XCEC_Time_20260723-20261021_90d` — **51319 nến** bar_idx 0…51318 (toàn bộ TRAIN, không đụng TEST).
- C#: `benzo-trader/tools/OfSignalsDump` biên dịch thẳng 2 file nguồn sản phẩm (không sửa dòng nào).
- So từng dòng: vùng stacked (Lo/Hi, số mức, tỷ lệ yếu nhất, volume 2 bên, vị trí, Weak, Follow chế độ Touch và
  CloseThrough 300 nến sau) ở 3 cấu hình (250 %/3/1 = plan, 250 %/4/5, 300 %/3/1); kiệt sức đỉnh/đáy (loại, mức,
  volume cực trị, TB/mức, chuỗi tooltip, nến đầu tiên bị râu quét qua ≤ 300 nến).

| Nhóm | Số dòng Python |
|---|---|
| E_day | 6203 |
| E_dinh | 6176 |
| Z_250_3_1 | 43169 |
| Z_250_4_5 | 1834 |
| Z_300_3_1 | 40224 |

- Tổng dòng: C# 97606 · Python 97606 · chỉ có ở C# **0** · chỉ có ở Python **0** · khác giá trị **0**.
- **Kết luận: KHỚP 100 %.**
