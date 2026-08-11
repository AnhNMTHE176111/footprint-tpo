import csv, statistics as st
rows=[]
with open('/home/asl86/Documents/footprint-tpo/data-export/TPO-chart-daily.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f): rows.append(r)
def fl(r,k):
    try: return float(r[k])
    except: return None
# gom thành từng profile (run các dòng có cùng VAH/VAL/POC/IBHigh/IBLow)
profs=[]; cur=None; sig=None
for r in rows:
    s=(r['VAH'],r['VAL'],r['POC'],r['IB High'],r['IB Low'])
    if s!=sig:
        if cur: profs.append(cur)
        sig=s; cur={'start':r['DateTime'],'sig':s,'rows':[r]}
    else: cur['rows'].append(r)
if cur: profs.append(cur)
print(f"Số profile ngày gom được: {len(profs)}\n")
print("Mốc bắt đầu mỗi profile (5 cái đầu):")
for p in profs[:5]: print("  ", p['start'])
out=[]
for p in profs:
    rs=p['rows']; last=rs[-1]
    vah,val=fl(last,'VAH'),fl(last,'VAL'); ibh,ibl=fl(last,'IB High'),fl(last,'IB Low')
    rng=fl(last,'Range'); ibr=fl(last,'IB range'); close=fl(last,'Close'); op=fl(rs[0],'Open')
    if None in (vah,val,ibh,ibl,rng,ibr,close,op) or rng==0: continue
    out.append(dict(start=p['start'],n=len(rs),vah=vah,val=val,ibh=ibh,ibl=ibl,
        rng=rng,ibr=ibr,close=close,op=op,
        va_in_ib=(val>=ibl and vah<=ibh), ibr_pct=ibr/close*100,
        close_in_va=(val<=close<=vah)))
print(f"\nProfile dùng được: {len(out)}")
med=st.median([o['rng'] for o in out])
print(f"Range trung vị (1 phiên): {med:.1f} giá\n")
print("="*76)
print("LUẬT 1 — 'VA nằm TRONG IB ⇒ phiên SAU có trend'  (trend = Range > trung vị)")
a=b=c=d=0
for i in range(len(out)-1):
    nxt_trend = out[i+1]['rng'] > med
    if out[i]['va_in_ib']:
        a+=nxt_trend; b+=1
    else:
        c+=nxt_trend; d+=1
print(f"  VA TRONG IB   : {a}/{b} phiên sau có trend" + (f"  = {a/b*100:.0f}%" if b else ""))
print(f"  VA NGOÀI IB   : {c}/{d} phiên sau có trend" + (f"  = {c/d*100:.0f}%" if d else ""))
print("="*76)
print("LUẬT 2 — 'IB range ≤1% ⇒ phiên sau BREAKOUT'")
for thr in (0.5,0.75,1.0,1.5):
    a=b=c=d=0
    for i in range(len(out)-1):
        nxt = out[i+1]['rng'] > med
        if out[i]['ibr_pct']<=thr: a+=nxt; b+=1
        else: c+=nxt; d+=1
    print(f"  IB ≤{thr}%: {a}/{b}" + (f" = {a/b*100:.0f}%" if b else " = —") +
          f"   | IB >{thr}%: {c}/{d}" + (f" = {c/d*100:.0f}%" if d else ""))
print(f"\n  Phân bố IB range (% giá): min={min(o['ibr_pct'] for o in out):.2f}  "
      f"trung vị={st.median([o['ibr_pct'] for o in out]):.2f}  max={max(o['ibr_pct'] for o in out):.2f}")
print("="*76)
print("LUẬT 3 — 'Giá ĐÓNG ngoài VA ⇒ VA không phải vùng giá trị đúng'")
n_out=sum(1 for o in out if not o['close_in_va'])
print(f"  Số phiên đóng NGOÀI VA: {n_out}/{len(out)} = {n_out/len(out)*100:.0f}%")
