import csv, sys, statistics as st
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
N = {'China':2100,'Japan':1000,'Taiwan':750,'Thailand':850,'Malaysia':730,'Indonesia':1200,'India':1850,'Vietnam':900,
     'Kazakhstan':700,'Australia':710,'Philippines':700,'Singapore':700,'United States':1300,'Canada':800,'Mexico':960,
     'Brazil':1100,'Argentina':800,'Chile':500,'United Kingdom':850,'France':850,'Italy':840,'Spain':800,'Germany':900,
     'Russia':1000,'Turkiye':880,'Poland':500,'UAE':700,'Saudi Arabia':730,'South Africa':800,'Egypt':900}
assert sum(N.values()) == 27400
countries = list(rows[0].keys())[4:]
dims = []
for r in rows:
    if r['dimension'] not in dims: dims.append(r['dimension'])
# dimension totals of row_total
for d in dims:
    print(f"{d:16s} sum(row_total)={sum(int(r['row_total']) for r in rows if r['dimension']==d)}")
# column sums of shares per dimension? (shares are % of row, not of column) -> sum over countries of share per row
for r in rows:
    s = sum(float(r[c]) for c in countries)
    if abs(s-100) > 0.6: print('row share sum off', r['dimension'], r['category'], round(s,1))
print('row share sums range', min(sum(float(r[c]) for c in countries) for r in rows), max(sum(float(r[c]) for c in countries) for r in rows))
devs = []
print(f"{'country':15s} {'n':>5s} " + ' '.join(f'{d[:9]:>10s}' for d in dims))
for c in countries:
    out = []
    for d in dims:
        est = sum(int(r['row_total'])*float(r[c])/100 for r in rows if r['dimension']==d)
        dev = (est - N[c]) / N[c] * 100
        devs.append((abs(dev), c, d, est, dev)); out.append(f'{est:7.1f}({dev:+.1f}%)'.rjust(10))
    print(f'{c:15s} {N[c]:5d} ' + ' '.join(f'{x:>10s}' for x in [f"{dv[3]:.0f}/{dv[4]:+.1f}" for dv in devs[-len(dims):]]))
devs.sort(reverse=True)
print('max abs dev:', devs[:5])
print('median abs dev %:', round(st.median(d[0] for d in devs), 2))
# excluding the total row dim
d2 = [d for d in devs if d[2] != 'total']
print('max abs dev excl total:', d2[0]); print('median excl total', round(st.median(d[0] for d in d2),2))
# also count-level deviation
mx = max(devs, key=lambda d: abs(d[3]-N[d[1]]))
print('max abs count dev:', mx[1], mx[2], round(mx[3],1), N[mx[1]], round(mx[3]-N[mx[1]],1))
print('--- rounding-bound test: |est-n| <= sum(row_total*0.05/100) ---')
bad = 0
for c in countries:
    for d in dims:
        rs = [r for r in rows if r['dimension']==d]
        est = sum(int(r['row_total'])*float(r[c])/100 for r in rs)
        # bound: shares can't be negative; lower bound of true share = max(0, s-0.05)
        lo = sum(int(r['row_total'])*max(0, float(r[c])-0.05)/100 for r in rs)
        hi = sum(int(r['row_total'])*min(100, float(r[c])+0.05)/100 for r in rs)
        if not (lo - 1e-9 <= N[c] <= hi + 1e-9):
            bad += 1; print('OUTSIDE', c, d, round(lo,1), N[c], round(hi,1))
print('outside-bound cases:', bad)
