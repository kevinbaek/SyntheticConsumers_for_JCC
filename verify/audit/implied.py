import csv, sys
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
lvl = {(r['country'], r['var']): float(r['value']) for r in rows if r['wave']=='15' and r['stat']=='t2b'}
for r in rows:
    if r['stat'] == 't2b_delta':
        k = (r['country'], r['var']); d = float(r['value'])
        print(f"{r['country']:15s} {r['var']}: delta {d:+.1f} -> implied w14 = " + (f"{lvl[k]:.1f} - ({d:+.1f}) = {lvl[k]-d:.1f}" if k in lvl else "no w15 level in CSV"))
# distribution sums
for var in ('XQ5','XQ6'):
    for w in ('15','14'):
        d = {r['stat']: float(r['value']) for r in rows if r['country']=='ALL30' and r['var']==var and r['wave']==w and r['stat'] in ('t2b','mid','b2b')}
        if d: print(var, w, d, 'sum=', round(sum(d.values()),1))
pops = [float(r['value']) for r in rows if r['var'].startswith('XQ1_')]
p11 = [float(r['value']) for r in rows if r['var'].startswith('XQ1_') and r['var'] not in ('XQ1_12','XQ1_13')]
print('ALL30 13-domain mean', round(sum(pops)/len(pops),2), len(pops), '| 11-domain mean', round(sum(p11)/len(p11),2), len(p11))
y2020 = [45.1,42.2,43.1,31.1,34.2,39.6,29.2,33.3,30.0,25.3,26.3]; y2015=[46.2,39.0,35.8,29.9,29.0,35.8,29.9,27.1,22.8,15.1]
print('fig 2-1-7 check: 2025-2020 11-mean diff', round(sum(p11)/11 - sum(y2020)/11, 2), '| 2020-2015 (10 dom, excl webtoon)', round((sum(y2020)-25.3)/10 - sum(y2015)/10, 2))
