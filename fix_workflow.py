# -*- coding: utf-8 -*-
import json

file_path = r'd:\AI Agent\xhs-yunying\xiaohongshu-automation-workflow.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

lines = []
lines.append("=== Data Flow Verification ===")
lines.append("")

# Build adjacency
forward = {}
for src, conn in data['connections'].items():
    if 'main' in conn:
        for targets in conn['main']:
            for t in targets:
                forward.setdefault(src, []).append(t['node'])

reverse_adj = {}  # node -> [upstream nodes]
for src, conn in data['connections'].items():
    if 'main' in conn:
        for targets in conn['main']:
            for t in targets:
                reverse_adj.setdefault(t['node'], []).append(src)
    if 'ai_languageModel' in conn:
        for targets in conn['ai_languageModel']:
            for t in targets:
                reverse_adj.setdefault(t['node'], []).append(src)

id_to_name = {n['id']: n['name'] for n in data['nodes']}
name_to_id = {n['name']: n['id'] for n in data['nodes']}

def get_upstream_set(node_name, max_depth=5):
    """Find the nearest upstream Set node"""
    visited = set()
    queue = [(node_name, 0)]
    while queue:
        node, depth = queue.pop(0)
        if depth > max_depth:
            continue
        for up in reverse_adj.get(node, []):
            # Check if this upstream is a Set node (n8n-nodes-base.set)
            for n in data['nodes']:
                if n['name'] == up and 'set' in n.get('type', ''):
                    return up, depth + 1
            if up not in visited:
                visited.add(up)
                queue.append((up, depth + 1))
    return None, -1

# Print pipeline order
lines.append("Pipeline execution order:")
order = ['定时或手动触发', '【用户参数设定】', '❓ 检查是否指定主题']
# After IF: two paths converge at 📌 确立最终主题
order += ['📌 确立最终主题', '💪 健身教练 Agent', '💾 保存教练输出',
          '🎨 知识卡片架构师 Agent', '💾 保存卡片输出',
          '✍️ 文案撰写 Agent', '💾 保存全部数据',
          '✅ 质量审核 Agent', '💾 保存审核结果', '📦 输出最终内容']

for i, name in enumerate(order):
    n = [x for x in data['nodes'] if x['name'] == name]
    if n:
        ntype = n[0]['type'].split('.')[-1]
        lines.append(f"  [{i+1}] {name} ({ntype})")

lines.append("")
lines.append("=== Each Pack Node: where does it read data from? ===")
lines.append("")

pack_nodes = ['💾 保存教练输出', '💾 保存卡片输出', '💾 保存全部数据', '💾 保存审核结果']
for pname in pack_nodes:
    pn = [x for x in data['nodes'] if x['name'] == pname][0]
    assignments = pn['parameters'].get('assignments', {}).get('assignments', [])
    
    lines.append(f"📦 {pname}:")
    lines.append(f"   Upstream input comes from: {reverse_adj.get(pname, ['?'])}")
    
    for a in assignments:
        val = a.get('value', '')
        name_field = a.get('name', '')
        # Check if it uses $('xxx') cross-reference or $json direct
        if '$(\'' in val:
            import re
            refs = re.findall(r"\$\(['\"]([^'\"]+)['\"]\)", val)
            lines.append(f"   {name_field} = $(\'{refs[0]}\')  <-- cross-node ref")
        elif '$json.' in val:
            field = val.replace('={{ ', '').replace(' }}', '').replace('$json.', '')
            lines.append(f"   {name_field} = $json.{field}  <-- from direct upstream")
    lines.append("")

lines.append("=== AI Agent Nodes: what do they read? ===")
lines.append("")
for n in data['nodes']:
    if 'langchain' in n.get('type', '') and 'lmChat' not in n.get('type', ''):
        params_str = json.dumps(n.get('parameters', {}), ensure_ascii=False)
        import re
        refs = re.findall(r'\{\{ ([^}]+) \}\}', params_str)
        lines.append(f"🤖 {n['name']}:")
        for ref in refs:
            ref_clean = ref.strip()
            if '$json' in ref_clean or '{{' not in ref_clean:
                lines.append(f"   reads: {ref_clean}")
        lines.append("")

with open(r'd:\AI Agent\xhs-yunying\diag_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('Done! See diag_result.txt')
