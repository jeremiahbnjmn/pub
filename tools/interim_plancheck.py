"""Show how the course list scanned on the site differs from plan.json in umalyfe-engine (counts and the first differences only)."""
import gzip, json, glob, os, subprocess
raw = lambda path: subprocess.run(['gh', 'api', f'repos/jeremiahbnjmn/umalyfe-engine/contents/{path}', '-H', 'Accept: application/vnd.github.raw'], capture_output=True, check=True).stdout
plan = json.loads(raw('scores/interim/plan.json'))['courses']
f = sorted(glob.glob('out/*.json.gz'))[0]; site = json.load(gzip.open(f, 'rt'))['plan']
key = lambda c: [c['i'], c['track'], c['cv'], c['label']]
print('plan.json courses', len(plan), '| site courses', len(site))
d = [(a, b) for a, b in zip(plan, site) if key(a) != key(b)]
print('differing positions', len(d), '| first index that differs', (d[0][0]['i'] if d else None))
for a, b in d[:4]: print(' plan:', key(a), '\n site:', key(b))
if len(site) != len(plan): print('extra on', 'site' if len(site) > len(plan) else 'plan', [key(c) for c in (site if len(site) > len(plan) else plan)[min(len(site), len(plan)):][:4]])
