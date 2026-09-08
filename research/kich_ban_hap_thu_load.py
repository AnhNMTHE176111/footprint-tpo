import csv
def days_from_civil(y,m,d):
    y -= m<=2
    era=(y if y>=0 else y-399)//400
    yoe=y-era*400
    doy=(153*(m+(-3 if m>2 else 9))+2)//5+d-1
    doe=yoe*365+yoe//4-yoe//100+doy
    return era*146097+doe-719468
def load(path):
    t,o,h,l,c,v,dl=[],[],[],[],[],[],[]
    with open(path,newline="") as f:
        r=csv.reader(f); hd=next(r); ix={k:i for i,k in enumerate(hd)}
        for row in r:
            s=row[ix["datetime"]]
            t.append(days_from_civil(int(s[0:4]),int(s[5:7]),int(s[8:10]))*1440+int(s[11:13])*60+int(s[14:16]))
            o.append(float(row[ix["open"]])); h.append(float(row[ix["high"]]))
            l.append(float(row[ix["low"]])); c.append(float(row[ix["close"]]))
            v.append(float(row[ix["volume"]])); dl.append(float(row[ix["delta"]]))
    return t,o,h,l,c,v,dl
