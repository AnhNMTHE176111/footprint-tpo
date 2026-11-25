#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vong20.py — 20 vòng: vẽ sẵn vùng cụm khối lượng → giá chạm thì đảo hay xuyên (M15). python vong20.py [vòng ...]"""
import sys
import vs

R = {}
def vong(k):
    def deco(f): R[k] = f; return f
    return deco

F = 'imp4>=3 and nt<=2'           # luật nền sau vòng 3 (cập nhật dần)

@vong(1)
def v1():
    d = vs.both(); vs.line(1, 'cụm 2 nặng nhất / phiên, 3 phiên, gộp chồng · MỌI lần chạm', d)
    sn = {s: vs.snapshot(s) for s in d}; vs.line('1·mốc', 'kiểm: 400 mốc ngẫu nhiên / mã, lần chạm đầu sau mốc', sn)

@vong(2)
def v2():
    d = vs.both()
    vs.line(2, 'chỉ vùng giá đã RỜI MẠNH (≥ 3 U15 trong 4 nến M15)', d, 'imp4>=3')
    vs.line('2·b', 'đối lại: rời chậm (< 3 U15 trong 4 nến)', d, 'imp4<3')

@vong(3)
def v3():
    d = vs.both()
    for k in (1, 2, 3):
        vs.line('3·%d' % k, 'rời mạnh · lần tới gần thứ %d' % k, d, 'imp4>=3 and nt==%d' % k)
    vs.line(3, 'rời mạnh · lần tới 1–2 (LUẬT NỀN)', d, F)

@vong(4)
def v4():
    d = vs.both()
    for col, lab in (('imp2', '2 nến'), ('imp4', '4 nến'), ('imp8', '8 nến')):
        for x in (2, 3, 4, 5):
            vs.line(4, 'rời ≥ %d U15 trong %s · lần 1–2' % (x, lab), d, '%s>=%d and nt<=2' % (col, x))

@vong(5)
def v5():
    d = vs.both()
    vs.line(5, 'luật nền · chỉ cụm nặng nhất của phiên (hạng 1)', d, F + ' and rank==1')
    vs.line(5, 'luật nền · cụm hạng 2', d, F + ' and rank==2')
    for r in (2.0, 2.5, 3.0):
        vs.line(5, 'luật nền · cụm ≥ %.1f × TB hàng' % r, d, F + ' and ratio>=%g' % r)

@vong(6)
def v6():
    d = vs.both()
    for g in (1, 2, 3):
        vs.line(6, 'luật nền · cụm từ phiên cách %d ngày' % g, d, F + ' and lag==%d' % g)
    d5 = vs.both(LBD=5); vs.line(6, 'luật nền · lấy 5 phiên', d5, F)

@vong(7)
def v7():
    d = vs.both()
    vs.line(7, 'luật nền · vùng 1 nguồn', d, F + ' and nm==1')
    vs.line(7, 'luật nền · vùng HỢP LƯU ≥ 2 cụm chồng nhau', d, F + ' and nm>=2')
    vs.line(7, 'mọi lần chạm · vùng hợp lưu ≥ 2', d, 'nm>=2')
    d5 = vs.both(LBD=5); vs.line(7, 'mọi lần chạm · hợp lưu ≥ 2 (5 phiên)', d5, 'nm>=2')
    vs.line(7, 'mọi lần chạm · hợp lưu ≥ 3 (5 phiên)', d5, 'nm>=3')

@vong(8)
def v8():
    d = vs.both(WEEK=True)
    vs.line(8, 'thêm cụm tuần trước (gộp) · luật nền', d, F)
    vs.line(8, '  · vùng có cụm tuần', d, F + ' and src.str.contains("tuan")', )
    vs.line(8, '  · vùng không có cụm tuần', d, F + ' and not src.str.contains("tuan")')
    vs.line(8, 'mọi lần chạm · vùng có cụm tuần', d, 'src.str.contains("tuan")')

@vong(9)
def v9():
    for fr in (0.55, 0.70, 0.85):
        vs.line(9, 'dải cụm tới %.0f %% đỉnh · luật nền' % (fr * 100), vs.both(FRAC=fr), F)

@vong(10)
def v10():
    for pad in (0.0, 0.1, 0.2):
        vs.line(10, 'nới theo râu mỗi mép %.1f U15 · luật nền' % pad, vs.both(PAD=pad), F)

@vong(11)
def v11():
    d = vs.both(NGAY=False, ROT=True)
    vs.line(11, 'chỉ vùng ĐI NGANG → BỨT kiểu Dale (tự dò M15) · mọi lần chạm', d)
    vs.line(11, '  · lần tới 1–2', d, 'nt<=2')
    for rr, rn in ((2.0, 6), (3.0, 6), (2.5, 8), (2.5, 4)):
        d2 = vs.both(NGAY=False, ROT=True, RR=rr, RN=rn)
        vs.line(11, '  · hộp ≤ %.1f U15, ≥ %d nến · lần 1–2' % (rr, rn), d2, 'nt<=2')

@vong(12)
def v12():
    d = vs.both(ROT=True)
    vs.line(12, 'cụm phiên + vùng đi ngang Dale (gộp) · luật nền', d, F)
    vs.line(12, '  · vùng có đi ngang Dale', d, F + ' and src.str.contains("rot")')
    vs.line(12, '  · vùng có cả cụm phiên lẫn đi ngang Dale', d, F + ' and src.str.contains("rot") and src.str.contains("ngay")')

@vong(13)
def v13():
    d = vs.both()
    vs.line(13, 'luật nền · vùng chứa cao/thấp phiên trước', d, F + ' and brk==1')
    vs.line(13, 'luật nền · không chứa', d, F + ' and brk==0')

@vong(14)
def v14():
    d = vs.both()
    vs.line(14, 'luật nền · chạm THUẬN xu hướng (giá vẫn ở phía vùng so với TB 1 ngày)', d, F + ' and tr>0')
    vs.line(14, 'luật nền · chạm NGƯỢC xu hướng', d, F + ' and tr<=0')

@vong(15)
def v15():
    d = vs.both()
    vs.line(15, 'luật nền · giá lao tới nhanh (60 phút trước còn cách ≥ 3 U15)', d, F + ' and spd>=3')
    vs.line(15, 'luật nền · lao tới vừa (1,5–3 U15)', d, F + ' and spd>=1.5 and spd<3')
    vs.line(15, 'luật nền · bò tới chậm (< 1,5 U15)', d, F + ' and spd<1.5')

@vong(16)
def v16():
    d = vs.both()
    for a, b in ((0, 4), (4, 12), (12, 99)):
        vs.line(16, 'luật nền · chạm %d–%d giờ sau khi rời dải' % (a, b), d, F + ' and since>=%d and since<%d' % (a, b))

@vong(17)
def v17():
    d = vs.both()
    vs.line(17, 'luật nền · giờ Mỹ (13–20 UTC)', d, F + ' and hour>=13 and hour<20')
    vs.line(17, 'luật nền · ngoài giờ Mỹ', d, F + ' and (hour<13 or hour>=20)')

@vong(18)
def v18():
    for b in (0.5, 1.0, 1.5, 2.0):
        vs.line(18, 'luật nền · ngưỡng đảo = bật %.1f U15' % b, vs.both(B=b), F)


F2 = 'imp8>=3 and nt<=2 and rank==1'
F3 = F2 + ' and tr>0'

@vong(19)
def v19():
    d = vs.both()
    vs.line(19, 'GHÉP: rời ≥ 3 U15 trong 8 nến · lần 1–2 · cụm nặng nhất phiên', d, F2)
    vs.line(19, 'GHÉP + chạm thuận xu hướng', d, F3)
    vs.line(19, 'đối lại: GHÉP nhưng chạm ngược xu hướng', d, F2 + ' and tr<=0')
    d2 = vs.both(ROT=True)
    vs.line(19, 'GHÉP + thêm vùng đi ngang Dale (gộp)', d2, F2)
    vs.line(19, 'GHÉP + đi ngang Dale + thuận xu hướng', d2, F3)

@vong(20)
def v20():
    sn = {s: vs.snapshot(s, n_moc=600) for s in ('nqy', 'gc')}
    vs.line('20·mốc', 'KIỂM CUỐI nghĩa đen: 600 mốc ngẫu nhiên / mã · luật GHÉP', sn, F2)
    vs.line('20·mốc', 'KIỂM CUỐI nghĩa đen · luật GHÉP + thuận xu hướng', sn, F3)
    for b in (0.5, 1.5, 2.0):
        vs.line(20, 'luật GHÉP + thuận xu hướng · bật %.1f U15' % b, vs.both(B=b), F3)
    vs.line(20, 'luật GHÉP + thuận xu hướng · lấy 5 phiên', vs.both(LBD=5), F3)

if __name__ == '__main__':
    print(vs.HDR)
    ks = [int(a) for a in sys.argv[1:]] or sorted(R)
    for k in ks: R[k]()
