import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'd:\AI Agent\xhs-yunying\xiaohongshu-automation-workflow.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. 移除前台调度 Agent
data['nodes'] = [n for n in data['nodes'] if n['id'] != 'dispatch']

# 2. 新增 IF 节点和最终主题统一节点
data['nodes'].extend([
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.userTheme }}",
              "operation": "isNotEmpty"
            }
          ]
        }
      },
      "id": "check_theme",
      "name": "❓ 检查是否指定主题",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [440, 0],
      "notesInFlow": True,
      "notes": "有指定主题则直达，空则触发趋势Agent发散"
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "set_topic1",
              "name": "output",
              "value": "={{ $json.output ? $json.output : $('【用户参数设定】').first().json.userTheme }}",
              "type": "string"
            }
          ]
        },
        "options": {}
      },
      "id": "final_theme",
      "name": "📌 确立最终主题",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [940, -100],
      "notesInFlow": True,
      "notes": "统一输出变量给全链路"
    }
])

# 3. 遍历更新节点参数
for n in data['nodes']:
    # 隐藏并切断飞书
    if n['id'] == 'feishu':
        n['position'] = [440, -200]
        
    # 修改热点趋势 Agent 提示词，移除对 dispatch 简报的依赖
    if n['id'] == 'trend':
        n['position'] = [680, 100]
        n['parameters']['text'] = "=# 角色：小红书健身领域 · 高级趋势猎手\n\n## 身份声明\n你是「铁壳健身内容工作室」的趋势捕捉专家，拥有对小红书平台健身领域的极致洞察力。你的职责是自主思考并敲定今日的核心发布主题。\n\n## 行为边界约束（铁律）\n1. 你的唯一使命是输出一个精炼、具体、可执行的主题短语\n2. 输出不超过15个汉字\n3. 绝对禁止输出任何解释、分析过程、客套话或多余标点\n4. 你的主题必须严格聚焦在「健身/减脂/增肌/体态矫正/运动营养/居家训练」范畴内\n5. 你的输出将作为整条流水线的上下文核心参数，任何废话都会导致全链路崩溃！\n\n## 执行逻辑\n基于你的专业嗅觉，启动自主趋势捕获引擎：\n- 考虑当前月份的时令热点（1-3月新年打卡/4-6月夏日塑形/7-9月黄金增肌季/10-12月冬季体态调整）\n- 结合小红书健身赛道的长青流量密码（翘臀、马甲线、天鹅颈、直角肩、蜜桃臀、宽肩窄腰）\n- 优先选择兼具「保姆级教程价值」和「收藏冲动」的方向\n- 避开已被过度消费的烂梗主题\n\n## 输出\n直接输出主题短语。示例格式：\n新手友好的居家翘臀训练\n7天打造天鹅颈完整教程\n男生宽肩训练黄金6式"
    
    # 修改最终输出页面，彻底去除任务简报
    if n['id'] == 'output':
        n['parameters']['assignments']['assignments'][0]['value'] = "=\n# 🔥 今日主题\n{{ $('📌 确立最终主题').first().json.output }}\n\n---\n\n# 🎨 知识卡片绘图 Prompt（至少10张教程卡片）\n{{ $('🎨 知识卡片架构师 Agent').first().json.output }}\n\n---\n\n# ✍🏻 小红书配套正文（已去AI味润色）\n{{ $('🔧 去AI味润色 Agent').first().json.output }}\n\n---\n\n# ✅ 质量审核报告\n{{ $('✅ 质量审核 Agent').first().json.output }}"
        
    # 全局替换原引用
    if 'parameters' in n and 'text' in n['parameters']:
        n['parameters']['text'] = n['parameters']['text'].replace(
            "$('🔥 热点趋势 Agent').first().json.output", 
            "$('📌 确立最终主题').first().json.output"
        )

# 4. 彻底重构拓扑连接
data['connections'] = {
    "定时或手动触发": { "main": [ [ { "node": "【用户参数设定】", "type": "main", "index": 0 } ] ] },
    "【用户参数设定】": { "main": [ [ { "node": "❓ 检查是否指定主题", "type": "main", "index": 0 } ] ] },
    "❓ 检查是否指定主题": {
        "main": [
            [ { "node": "📌 确立最终主题", "type": "main", "index": 0 } ],
            [ { "node": "🔥 热点趋势 Agent", "type": "main", "index": 0 } ]
        ]
    },
    "🔥 热点趋势 Agent": { "main": [ [ { "node": "📌 确立最终主题", "type": "main", "index": 0 } ] ] },
    "📌 确立最终主题": { "main": [ [ { "node": "💪 健身教练 Agent", "type": "main", "index": 0 } ] ] },
    "💪 健身教练 Agent": {
        "main": [
            [ { "node": "🎨 知识卡片架构师 Agent", "type": "main", "index": 0 },
              { "node": "✍️ 文案撰写 Agent", "type": "main", "index": 0 } ]
        ]
    },
    "🎨 知识卡片架构师 Agent": { "main": [ [ { "node": "内容汇总打包", "type": "main", "index": 0 } ] ] },
    "✍️ 文案撰写 Agent": { "main": [ [ { "node": "🔧 去AI味润色 Agent", "type": "main", "index": 0 } ] ] },
    "🔧 去AI味润色 Agent": { "main": [ [ { "node": "内容汇总打包", "type": "main", "index": 1 } ] ] },
    "内容汇总打包": { "main": [ [ { "node": "✅ 质量审核 Agent", "type": "main", "index": 0 } ] ] },
    "✅ 质量审核 Agent": { "main": [ [ { "node": "📦 输出最终内容", "type": "main", "index": 0 } ] ] },
    "精准判断引擎 (T=0.1)": {
        "ai_languageModel": [ [ { "node": "✅ 质量审核 Agent", "type": "ai_languageModel", "index": 0 } ] ]
    },
    "专业知识引擎 (T=0.2)": {
        "ai_languageModel": [
            [ { "node": "💪 健身教练 Agent", "type": "ai_languageModel", "index": 0 },
              { "node": "🎨 知识卡片架构师 Agent", "type": "ai_languageModel", "index": 0 } ]
        ]
    },
    "创意文案引擎 (T=0.7)": {
        "ai_languageModel": [
            [ { "node": "🔥 热点趋势 Agent", "type": "ai_languageModel", "index": 0 },
              { "node": "✍️ 文案撰写 Agent", "type": "ai_languageModel", "index": 0 } ]
        ]
    },
    "润色平衡引擎 (T=0.5)": {
        "ai_languageModel": [
            [ { "node": "🔧 去AI味润色 Agent", "type": "ai_languageModel", "index": 0 } ]
        ]
    }
}

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON patch applied successfully.")
