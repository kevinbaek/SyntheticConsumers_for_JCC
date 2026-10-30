# Printed readings transcribed independently from the 250-dpi page images (not from the CSV).
import csv, sys
P = {}  # (country, wave, var, stat) -> (printed, printed_page, location, evidence)
def add(c, w, v, s, val, pg, loc, ev): P[(c, str(w), v, s)] = (val, pg, loc, ev)
for c, x in [('Philippines',87.0),('India',83.8),('Indonesia',82.7),('Thailand',79.4),('Mexico',78.9),('UAE',78.0),('Malaysia',77.4)]:
    add(c,15,'XQ5','t2b',x,40,'fig 2-1-1 top-7 bar','image+text layer')
add('ALL30',15,'XQ5','t2b',69.7,40,'fig 2-1-1 30-country bar; infographic p13; text p40','image+text')
for c, x in [('France',58.2),('Italy',56.4),('Poland',54.4),('Germany',54.4),('Japan',52.7),('Kazakhstan',50.8),('Russia',44.5)]:
    add(c,15,'XQ5','t2b',x,40,'fig 2-1-1 bottom-7 bar','image+text layer')
add('ALL30',15,'XQ5','b2b',5.0,13,'infographic 마음에 안듦(1+2)','image+text')
add('ALL30',15,'XQ5','mid',25.3,13,'infographic 보통(3)','image+text')
add('ALL30',14,'XQ5','t2b',70.3,41,'fig 2-1-2 콘텐츠 평균 2024; text p40 전년(70.3%)','image+text')
for c, x in [('United Kingdom',8.0),('Japan',6.4),('Spain',6.2),('United States',6.1),('Australia',6.0)]:
    add(c,14,'XQ5','t2b_delta',x,40,'fig 2-1-1 change box (▲) + text p40','image+text')
for c, x in [('Indonesia',-3.8),('Thailand',-3.3),('Philippines',-1.9)]:
    add(c,14,'XQ5','t2b_delta',x,40,'text p40 (▼)','image+text')
for c, x in [('Philippines',85.6),('India',83.3),('Mexico',79.8),('UAE',78.5),('South Africa',78.2),('Vietnam',76.1),('Brazil',75.6)]:
    add(c,15,'XQ6','t2b',x,62,'fig 2-1-11 top-7 bar','image+text layer')
for c, x in [('Japan',36.4),('Russia',48.6),('Germany',51.6),('Poland',53.4),('Italy',56.2),('France',56.8),('Kazakhstan',59.5)]:
    add(c,15,'XQ6','t2b',x,62,'fig 2-1-11 bottom-7 bar','image+text layer')
add('ALL30',15,'XQ6','t2b',67.7,62,'fig 2-1-10 2025 + text','image+text')
add('ALL30',15,'XQ6','mid',26.1,62,'fig 2-1-10 2025 보통 (chart only; =100-67.7-6.2)','image only')
add('ALL30',15,'XQ6','b2b',6.2,62,'fig 2-1-10 2025 + text','image+text')
add('ALL30',14,'XQ6','t2b',68.2,62,'fig 2-1-10 2024 + text 전년(68.2%)','image+text')
add('ALL30',14,'XQ6','mid',25.1,62,'fig 2-1-10 2024 보통 (chart only; =100-68.2-6.7)','image only')
add('ALL30',14,'XQ6','b2b',6.7,62,'fig 2-1-10 2024 (chart only; text: 6.2 = 0.5%p lower)','image only')
for c, x in [('Kazakhstan',9.0),('United Kingdom',7.4),('Australia',7.4),('South Africa',5.2),('Japan',4.6)]:
    add(c,14,'XQ6','t2b_delta',x,62,'fig 2-1-11 increase box (▲)','image+text')
for c, x in [('China',-5.3),('Russia',-5.2),('Turkiye',-4.8),('Vietnam',-4.7),('Thailand',-4.0)]:
    add(c,14,'XQ6','t2b_delta',x,62,'fig 2-1-11 decrease box (▼)','image+text')
for c, x in [('Philippines',60.0),('India',53.4),('Vietnam',53.1),('UAE',52.8),('Malaysia',52.2),('Saudi Arabia',51.0),('Thailand',50.2)]:
    add(c,15,'POPMEAN','t2b',x,58,'fig 2-1-8 top-7 bar','image+text layer')
for c, x in [('Poland',25.4),('Germany',31.3),('Russia',31.5),('Italy',31.7),('Japan',32.4),('Argentina',33.7),('Canada',34.5)]:
    add(c,15,'POPMEAN','t2b',x,58,'fig 2-1-8 bottom-7 bar','image+text layer')
dom = {'XQ1_1':('드라마',51.3),'XQ1_2':('예능',39.3),'XQ1_3':('영화',48.9),'XQ1_4':('음악',54.0),'XQ1_5':('애니메이션',37.5),
       'XQ1_6':('출판물',29.7),'XQ1_7':('웹툰',32.2),'XQ1_8':('게임',38.3),'XQ1_9':('패션',45.3),'XQ1_10':('뷰티',52.6),
       'XQ1_11':('음식',55.1),'XQ1_12':('캐릭터',38.9),'XQ1_13':('공연(K-pop 제외)',34.4)}
for v,(k,x) in dom.items():
    add('ALL30',15,v,'t2b',x,56,f'fig 2-1-6 2025 bar {k}', 'image only' if v in ('XQ1_5','XQ1_8') else 'image+text elsewhere')
for c, x in [('United Kingdom',71.1),('Australia',68.7),('China',61.3),('Turkiye',69.2),('Thailand',72.5)]:
    add(c,15,'XQ6','t2b',x,62,'fig 2-1-11 change box level','image+text')
LIST = {}
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
out = csv.writer(open(sys.argv[2], 'w', newline='', encoding='utf-8'))
out.writerow(['csv_line','country','wave','var','stat','csv_value','printed_value','csv_page','printed_page','pdf_page','location','evidence','list_csv','match'])
nm = 0
for i, r in enumerate(rows, start=2):
    k = (r['country'], r['wave'], r['var'], r['stat'])
    pv, pg, loc, ev = P.pop(k)
    ok = abs(float(r['value']) - pv) < 1e-9 and int(r['page']) == pg
    nm += ok
    out.writerow([i, *k, r['value'], pv, r['page'], pg, pg//2+1, loc, ev, r['list'], 'yes' if ok else 'NO'])
print('rows', len(rows), 'match', nm, 'unused printed keys', P)
