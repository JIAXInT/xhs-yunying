import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'd:\AI Agent\xhs-yunying\xiaohongshu-automation-workflow.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

output = []
output.append('=' * 60)
output.append('NODES:')
output.append('=' * 60)
for n in data['nodes']:
    output.append(f'  id={n["id"]:15s} name={n["name"]}')

output.append('')
output.append('=' * 60)
output.append('CONNECTIONS:')
output.append('=' * 60)
for src, conn in data['connections'].items():
    if 'main' in conn:
        for i, targets in enumerate(conn['main']):
            for t in targets:
                output.append(f'  {src} --> {t["node"]}')

output.append('')
output.append('=' * 60)
output.append('EXPRESSION REF CHECK:')
output.append('=' * 60)

all_names = set(n['name'] for n in data['nodes'])
issues = []

for n in data['nodes']:
    params_str = json.dumps(n.get('parameters', {}), ensure_ascii=False)
    refs = set(re.findall(r"\$\(['\"]([^'\"]+)['\"]\)", params_str))
    if refs:
        for ref in refs:
            if ref not in all_names:
                issues.append(f"  [BAD] Node '{n['name']}' references MISSING: {ref}")
            else:
                output.append(f"  [OK]  '{n['name']}' -> '{ref}'")

if issues:
    output.append('')
    output.append('!!! ISSUES FOUND !!!')
    for i in issues:
        output.append(i)
else:
    output.append('')
    output.append('All referenced nodes exist. No missing refs.')

output.append('')
output.append('=' * 60)
output.append('IF BRANCH CHECK:')
output.append('=' * 60)
check_conn = data['connections'].get('\u2753 \u68c0\u67e5\u662f\u5426\u6307\u5b9a\u4e3b\u9898', {})
if 'main' in check_conn:
    branches = check_conn['main']
    output.append(f'  Branch count: {len(branches)}')
    for i, branch in enumerate(branches):
        label = 'True (has theme)' if i == 0 else 'False (no theme)'
        for t in branch:
            output.append(f'  {label} --> {t["node"]}')
else:
    output.append('  BAD: IF node has no main output!')

# Write to file
with open(r'd:\AI Agent\xhs-yunying\check_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print('Done, result written to check_result.txt')
