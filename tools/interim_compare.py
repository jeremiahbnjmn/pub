"""Compare a piece scanned on GitHub (./out) with the same course already stored from the browser (umalyfe-engine, round 1). Prints numbers only."""
import gzip, json, csv, io, glob, os, subprocess, statistics as st, math
START = int(os.environ.get('START', '6'))
def raw(path):
    return subprocess.run(['gh', 'api', f'repos/jeremiahbnjmn/umalyfe-engine/contents/{path}', '-H', 'Accept: application/vnd.github.raw'], capture_output=True, check=True).stdout
plan = json.loads(raw('scores/interim/plan.json')); d = plan['courses'][START]['dir']
names = subprocess.run(['gh', 'api', f'repos/jeremiahbnjmn/umalyfe-engine/contents/scores/interim/{d}', '--jq', '.[].name'], capture_output=True, text=True, check=True).stdout.split()
rf = sorted(n for n in names if n.startswith('r1_'))[0]
br = {(r['scan'], r['skill']): r for r in csv.DictReader(io.StringIO(gzip.decompress(raw(f'scores/interim/{d}/{rf}')).decode()))}
gh = json.load(gzip.open(glob.glob('out/*.json.gz')[0], 'rt'))['courses'][str(START)]
print('course', START, gh['label'], '| browser file', rf, '| github scans', len(gh['scans']), 'bad', gh['bad'])
rows = {(sc, r[0]): r for sc, rs in gh['scans'].items() for r in rs}
print('rows: browser', len(br), 'github', len(rows), '| only in browser', len(set(br) - set(rows)), 'only in github', len(set(rows) - set(br)))
pairs = []
for k, r in rows.items():
    if k in br:
        try: pairs.append((float(r[4]), float(br[k]['mean'])))
        except ValueError: pass
dif = [abs(a - b) for a, b in pairs]; x = [a for a, b in pairs]; y = [b for a, b in pairs]
mx, my = st.mean(x), st.mean(y)
print('compared', len(pairs), '| mean abs diff', round(st.mean(dif), 3), 'median', round(st.median(dif), 3), 'max', round(max(dif), 3), '| avg size of a browser value', round(st.mean(map(abs, y)), 3))
print('correlation', round(sum((a - mx) * (b - my) for a, b in pairs) / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)), 4))
ov = []
for sc in gh['scans']:
    g = sorted(((float(r[4]), r[0]) for r in gh['scans'][sc] if (sc, r[0]) in br and r[4] not in ('—', '')), reverse=True)[:10]
    b = sorted(((float(v['mean']), k[1]) for k, v in br.items() if k[0] == sc and v['mean'] not in ('—', '')), reverse=True)[:10]
    ov.append(len({n for _, n in g} & {n for _, n in b}))
print('top-10 skills in common per scan (of 10): average', round(st.mean(ov), 1), 'min', min(ov), 'max', max(ov))
