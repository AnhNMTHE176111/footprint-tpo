# Đẩy file dữ liệu lớn lên GitHub (khi export dài nhiều năm)

## Vì sao push bị từ chối
GitHub có **giới hạn cứng 100 MB/file** (và cảnh báo từ 50 MB). Export per-level
2 năm của Optimus Flow nặng **556 MB** → bị chặn:

```
remote: error: File ...748d9h.csv is 556.33 MB; this exceeds GitHub's file size limit of 100.00 MB
! [remote rejected] main -> main (pre-receive hook declined)
```

Lưu ý: commit vẫn nằm ở máy, chỉ có **push** bị chặn. Phải gỡ commit đó ra rồi làm lại.

## Cách xử lý: nén gzip rồi mới commit
Đo thật trên file cùng định dạng: CSV per-level nén được **9,5 lần**, file `_bars` nén **5,9 lần**.

| File | Thô | Sau nén |
|---|---|---|
| `..._748d9h.csv` (per-level) | 556 MB | ~58 MB ✅ |
| `..._748d9h_bars.csv` | 87 MB | ~15 MB ✅ |

Cả hai đều lọt dưới ngưỡng 100 MB.

## Các bước làm trên máy Windows (mở **Git Bash**, không dùng CMD)

```bash
cd /d/duong-dan/toi/footprint-tpo     # sửa lại đúng đường dẫn repo

# 1. Xem đang thừa mấy commit chưa push
git log origin/main..HEAD --oneline

# 2. Gỡ các commit đó ra, GIỮ NGUYÊN file trên đĩa
git reset --mixed origin/main

# 3. Lấy .gitignore mới (đã chặn sẵn 2 file thô)
git pull origin main

# 4. Nén (giữ lại bản gốc nhờ cờ -k). File 556 MB nén mất vài phút, cứ chờ.
gzip -9 -k data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h.csv
gzip -9 -k data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv

# 5. Kiểm tra kích thước sau nén (phải < 100 MB)
ls -lh data-export/data-footprint/*.gz

# 6. Commit + push bản nén
git add -A
git commit -m "Thêm export GC:XCEC 2024-08-01..2026-08-19 (bản nén .csv.gz)"
git push origin main
```

**Nếu bản nén vẫn > 100 MB** thì chia nhỏ trước khi commit:
```bash
split -b 45m fp_..._748d9h.csv.gz fp_..._748d9h.csv.gz.part-
rm fp_..._748d9h.csv.gz
```
Ghép lại ở máy Linux: `cat *.gz.part-* > file.csv.gz`

## Giải nén ở máy Linux (để chạy nghiên cứu)
```bash
cd data-export/data-footprint
gunzip -k fp_GC_XCEC_Time_20240801-20260819_748d9h.csv.gz
gunzip -k fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv.gz
```
Bản `.csv` giải nén ra đã được `.gitignore` chặn nên không lo commit nhầm.

## ⚠️ Đừng dùng Git LFS
Tài khoản GitHub miễn phí chỉ có 1 GB lưu trữ + 1 GB băng thông/tháng cho LFS.
Riêng file này đã ăn hơn nửa hạn mức, mỗi lần clone lại trừ tiếp băng thông.
