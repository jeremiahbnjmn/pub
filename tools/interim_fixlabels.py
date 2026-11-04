"""The site may add a tag to a course label (e.g. 'CUP') that plan.json does not have. Copy plan.json's label into the piece when i, track and course id match,
so the store script accepts it. Anything else that differs is left alone (the store script then stops). Usage: interim_fixlabels.py <piece.json.gz>"""
import gzip, json, sys, subprocess
raw = lambda path: subprocess.run(['gh', 'api', f'repos/jeremiahbnjmn/umalyfe-engine/contents/{path}', '-H', 'Accept: application/vnd.github.raw'], capture_output=True, check=True).stdout
plan = json.loads(raw('scores/interim/plan.json'))['courses']
f = sys.argv[1]; p = json.load(gzip.open(f, 'rt', encoding='utf-8')); n = 0
if len(p['plan']) == len(plan):
    for c, q in zip(p['plan'], plan):
        if (c['i'], c['track'], c['cv']) == (q['i'], q['track'], q['cv']) and c['label'] != q['label']:
            c['label'] = q['label']; n += 1
    for k, c in p['courses'].items():
        q = plan[int(k)]
        if (c['idx'], c['track'], c['cv']) == (q['i'], q['track'], q['cv']): c['label'] = q['label']
if n: gzip.open(f, 'wt', encoding='utf-8').write(json.dumps(p))
print('labels fixed:', n)
