import csv, re, sys
A = sys.argv[1]; CSV = sys.argv[2]
KO = {'Philippines':'필리핀','India':'인도','Indonesia':'인도네시아','Thailand':'태국','Mexico':'멕시코','UAE':'UAE',
      'Malaysia':'말레이시아','France':'프랑스','Italy':'이탈리아','Poland':'폴란드','Germany':'독일','Japan':'일본',
      'Kazakhstan':'카자흐스탄','Russia':'러시아','United Kingdom':'영국','Spain':'스페인','United States':'미국',
      'Australia':'호주','South Africa':'남아프리카공화국','Vietnam':'베트남','Brazil':'브라질','China':'중국',
      'Turkiye':'튀르키예','Saudi Arabia':'사우디아라비아','Argentina':'아르헨티나','Canada':'캐나다'}
rows = list(csv.DictReader(open(CSV, encoding='utf-8')))
print('n rows', len(rows), 'cols', list(rows[0].keys()))
txt = {p: open(f'{A}/txt/p{p}.txt', encoding='utf-8').read() for p in range(1, 71)}
for i, r in enumerate(rows, start=2):
    pp = int(r['page']); pdfp = pp // 2 + 1
    v = float(r['value']); s = f'{abs(v):.1f}'
    t = txt[pdfp]
    found_page = s in t
    pair = ''
    if r['country'] != 'ALL30':
        ko = KO[r['country']]
        # name followed by value on same line (bar chart / change box / running text)
        pat = re.escape(ko) + r'[ \t]*\(?[ \t]*(?:[▲▼][ \t]*)?' + re.escape(s)
        m = re.search(pat, t)
        if not m and ko == '인도':
            pass
        pair = 'pair' if m else 'NOPAIR'
        # guard against '인도' matching inside '인도네시아'
        if ko == '인도' and m:
            m2 = re.search(r'(?<!\S)인도(?!네)[ \t]*\(?' + re.escape(s), t)
            pair = 'pair' if m2 else 'NOPAIR'
    print(f"{i:3d} {r['country']:15s} w{r['wave']} {r['var']:8s} {r['stat']:9s} {r['value']:>6s} p{pp}->pdf{pdfp} text:{'Y' if found_page else 'N'} {pair} {r['list']}")
