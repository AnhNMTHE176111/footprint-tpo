# Vùng quan trọng → nới theo râu / điểm quay đầu: 10 vòng đo (Opus, 2026-11-25)

Chỉ đo PHẢN ỨNG CỦA GIÁ TẠI VÙNG, không có lệnh, không tính R.

Dữ liệu:
- **NQZ26** từ 13/09 đến 25/11 (53 phiên). Phần từ tháng 2 đến tháng 8 là hợp đồng phụ nên bỏ.
- **GCZ26** từ 28/07 đến 18/11, dùng làm thị trường kiểm độc lập.

## Cách đo (`vz.py`)

**Thời điểm vẽ.** Tại mỗi nến M30 vừa đóng, mỗi cách vẽ cho ra danh sách vùng, chỉ dùng dữ liệu tới nến đó.

**Lần quay lại.** Giá (nến M1) vào trong khoảng 0,6 U ngoài mép gần, sau khi đã cách mép ít nhất 1,25 U.

**Điểm đảo.** Là cực trị tại lúc giá bật ngược 1 U. Phép đo được chạy lại với ngưỡng 0,5 U để kiểm độ bền.

**Phân loại theo vị trí điểm đảo:**
- **Tại vùng:** trong vùng, sai lệch ±0,1 U.
- **Sớm:** quay đầu trước khi tới mép gần.
- **Phá:** vượt quá mép xa, hoặc không bật đủ.

**Đối chứng.** Cùng vùng đó, dời đi ±1,5–4 U (3 bản). Với cách vẽ có nới theo râu thì có hai cách dời: dời lõi rồi nới lại tại chỗ mới, hoặc dời nguyên vùng. Cả hai cách đều được thử.

**Chỉ số.** Δ = % đảo tại vùng (thật) − % đảo tại vùng (đối chứng), theo điểm %. Khoảng [5–95 %] tính bằng bootstrap theo phiên.

**Tập kiểm.** NQ chia TRAIN (60 % phiên đầu) và TEST (40 % phiên sau). GC là thị trường thứ hai.

**Kiểm dụng cụ.** Đặt vùng 0,2 U tại đúng các đỉnh/đáy sẽ xảy ra trong tương lai (nhìn trước) cho Δ = **+11,5** [+10,2, +12,9]. Đây là trần của phép đo, nên một hiệu ứng thật cỡ +3 đến +5 là đáng kể.

## Mười vòng

| Vòng | Giả thuyết | Kết quả (Δ gộp NQ + GC, bật 1 U) | Kết luận |
|---|---|---|---|
| 1 | Indicator hiện tại (vùng mạnh + hộp HVN) | vùng mạnh −0,8 · hộp HVN +0,4 · cả hai −0,5 [−2,1, +1,0] | không hơn đường ngẫu nhiên |
| 2 | Từng loại mức làm lõi (mỏng ±0,1 U) | cạnh (VAL ngày +2,3, VWAP tuần +1σ +6,2, POC tuần +4,7) dương nhẹ; tâm (VWAP ngày −2,4, VWAP tuần −3,1) âm; HVN ngày −0,5, HVN tuần +2,2; **cao/thấp hôm qua & tuần trước âm rõ** (−5 đến −11) | mức "tâm" và HVN là chỗ giá đi xuyên; đỉnh/đáy cũ bị quét qua |
| 3 | Mọi lõi nới theo đỉnh/đáy M30 trong ±0,3–0,8 U | −0,6 đến −1,7 | nới theo râu cho MỌI loại lõi: vô ích, vì chỗ nào cũng có râu |
| 4 | Vùng = một điểm quay đầu M30 cũ (râu tới thân), theo độ bật 1–4 U | −0,4 đến +0,5 | điểm quay đầu cũ đứng một mình không có tác dụng |
| 5 | (a) hợp lưu các mức cạnh; (b) vùng **quét qua** đỉnh/đáy cũ | (a) 1 mức +2,7 [+0,3, +5,0], 2 mức +0,2, 3+ mức +5,9 (mẫu nhỏ); (b) 0,3–0,8 U ngoài đỉnh/đáy hôm qua và tuần trước: **+5,2 [+1,8, +8,6]**, đúng ngay mức thì −3,2 | giá quét qua đỉnh/đáy cũ khoảng 0,3–0,8 U rồi mới đảo |
| 6 | Biến thể vùng quét; quét qua đỉnh/đáy M30 bất kỳ; mức cạnh nới theo râu | quét 0,4–1,0 U +3,9; 0,5–1,2 U +4,4 (bật 0,5 U chỉ còn +2,4); quét đỉnh/đáy M30 bất kỳ ≈ 0; **cạnh nới râu +2,6 [+0,2, +5,0]** | hiệu ứng quét chỉ có ở đỉnh/đáy phiên và tuần; cạnh + râu có tác dụng |
| 7 | Chỉnh luật nới cho mức cạnh | **R 0,3 U, cần ≥ 1 điểm quay đầu: +3,0 [+0,6, +5,2]; bật 0,5 U: +3,2 [+1,1, +5,2]**, dương ở cả NQ TRAIN, NQ TEST và GC; R 0,8 U +1,4; cho cả tâm/HVN vào: +0,4 | đúng ý "vùng quan trọng trước, rồi nới theo râu", nhưng chỉ đúng với mức CẠNH |
| 8 | Giữ cả mức cạnh chưa có râu; ghép thêm vùng quét | cạnh có râu xác nhận mạnh hơn hẳn cạnh chưa có râu; ghép thêm vùng quét +3,1 [+1,6, +4,7] | cần râu xác nhận |
| 9 | Độ nhạy: nhìn lại 3/5/10 phiên, R 0,2/0,3 U, nới thêm 0/0,05/0,10 U | +3,0 đến +3,6 (bật 1 U), +2,3 đến +3,5 (bật 0,5 U); nới thêm 0,10 U thì tụt còn +1,1 | ổn định với lookback và R; vùng KHÔNG được nới quá |
| 10 | Bản đồ như indicator sẽ vẽ: gộp vùng chồng nhau + bán kính 4 U + tối đa 3 vùng mỗi phía | **+1,1 [−1,3, +3,5]**; bật 0,5 U +0,3; không gộp +1,7; tính riêng từng mức cạnh, bỏ trùng điểm đảo: +3,8 [+1,4, +6,1] | hiệu ứng **mong manh**: còn hay mất tuỳ cách gộp các vùng chồng nhau |

## Kết luận

1. Các mức trong spec cũ phần lớn KHÔNG phải chỗ giá đảo chiều. HVN, VWAP (tâm) và POC là chỗ giá đi xuyên hoặc bị hút vào. Đỉnh/đáy hôm qua và tuần trước bị quét qua. Điều này khớp với kết quả đo cũ: "HVN = đi tiếp / mục tiêu, không fade".
2. "Vùng quan trọng → nới theo râu" chỉ có lợi thế khi lõi là mức **CẠNH**: VAH/VAL và VWAP ±1σ, của ngày và tuần trước.
   - Luật: mức cạnh phải có ít nhất 1 điểm quay đầu M30 (bật ≥ 1 U, trong 5 phiên) nằm trong ±0,3 U.
   - Vùng được nới đến bao trọn các điểm quay đầu đó, cộng thêm 0,05 U.
   - Kết quả: đảo tại vùng hơn ngẫu nhiên khoảng **+3 đến +4 điểm %** (nền khoảng 30 %).
   - Khi gộp các vùng chồng nhau thành bản đồ vẽ thật, hiệu ứng chỉ còn **+1 đến +2**, không chắc chắn.
3. Có thể vẽ thêm **vùng quét** cách 0,3–0,8 U ngoài đỉnh/đáy hôm qua và tuần trước: +4 đến +5 với ngưỡng bật 1 U, yếu hơn với 0,5 U.
4. Tất cả vẫn **chưa kiểm định**: mẫu chỉ khoảng 2,5 tháng NQ và 3,5 tháng GC. Cần thêm NQU26, NQM26, NQH26 để kiểm lại.

## Lệnh chạy lại

```bash
python vong.py <1..10|10b|10c|kiem>
VZ_B=0.5 VZ_SFX=_B05 python vong.py <vòng>
python bang.py <bộ> | python bang.py tung_tag <bộ>
```

Bộ đệm `vm1_nqy.pkl` dựng bằng `prep_nqy.py`; bộ đệm `vm1_gc.pkl` dựng bằng `../vung_manh_2026-11-25/prep1.py gc`.
