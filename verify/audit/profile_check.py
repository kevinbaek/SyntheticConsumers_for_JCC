import re, csv, sys
A = sys.argv[1]; CSV = sys.argv[2]
def parse(path, ncols):
    rows = []
    for line in open(path, encoding='utf-8'):
        toks = re.findall(r'(?<![\d.])\d{1,3}(?:,\d{3})+(?![\d])|(?<![\d.,])\d+\.\d(?![\d])|(?<![\d.,])\d{3}(?![\d.,])', line)
        # first token row total (integer with or without comma), then ncols decimals
        if len(toks) == ncols + 1 and '.' not in toks[0]:
            rows.append((line.strip()[:12], int(toks[0].replace(',', '')), [float(t) for t in toks[1:]]))
    return rows
r16 = parse(f'{A}/txt/p16_table.txt', 16)
r17 = parse(f'{A}/txt/p17_table.txt', 14)
print(len(r16), len(r17))
rows = list(csv.DictReader(open(CSV, encoding='utf-8')))
countries = list(rows[0].keys())[4:]
print(countries, len(countries))
assert len(r16) == len(rows) == len(r17)
nchk = 0; mism = []
for i, row in enumerate(rows):
    lab16, tot16, v16 = r16[i]; lab17, tot17, v17 = r17[i]
    printed = v16 + v17
    if tot16 != tot17: mism.append(('total p16 vs p17', i, tot16, tot17))
    if int(row['row_total']) != tot16: mism.append(('row_total', row['dimension'], row['category'], row['row_total'], tot16))
    nchk += 1
    for c, pv in zip(countries, printed):
        nchk += 1
        if abs(float(row[c]) - pv) > 1e-9:
            mism.append(('cell', row['dimension'], row['category'], c, row[c], pv))
    print(f"{i:2d} {row['dimension']:16s} {row['category']:32s} | {lab16:12s} tot={tot16} ok")
print('checked', nchk, 'mismatches', len(mism))
for m in mism: print(m)
