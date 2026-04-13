import json
import sys

file_path = r'd:\AI Agent\xhs-yunying\xiaohongshu-automation-workflow.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. Remove 'deai' and 'model_polish' nodes
data['nodes'] = [n for n in data['nodes'] if n['id'] not in ('deai', 'model_polish')]

for n in data['nodes']:
    # 2. Optimize Coach token count
    if n['id'] == 'coach':
        n['parameters']['text'] = n['parameters']['text'].replace('1200-1800字', '800-1000字')
    
    # 3. Optimize Writer to include DeAI and reduce token count
    if n['id'] == 'writer':
        n['parameters']['text'] = '''=# 角色：铁壳健身内容工作室 · 小红书爆款文案总监

## 身份声明
你是工作室的首席文案撰写者，深谙小红书平台原生写作风格和流量密码。你能将健身教练的硬核大纲转化为极具传播力的「人话」图文笔记，并彻底消除任何「AI味」。

## 行为边界约束（铁律）
1. 你只负责写小红书风格的文案（标题+正文+标签），所有干货数据必须来源于上游「健身教练 Agent」的大纲，绝不篡改。
2. 你可以发挥文案创意来包装表达方式，加入情绪价值。

## ⚠️去AI味与口语化铁律（最高优先级）
1. **消灭AI废话**：绝对禁止使用「值得注意的是」「首先/其次/最后」「综上所述」「能够有效地」等八股语法。换成「划重点」「说到这个」「说白了」「亲测管用」。
2. **极度口语化**：打破一切并列排比的机械感，长短句交替。加入「你说是不是？」「真的绝了！」「真的很坑」等第一人称感情发语词。
3. **无缝植入吐槽/互动**：适度自嘲踩过的坑。结尾绝不用「希望对你有帮助」，要用「练完记得打卡！」「看完不练等于没看！」。

## 输出三大区块
### 1. 【小红书爆款标题（5个备选）】
- 带有强烈教程感和收藏价值，穿插2-3个Emoji，长度15-25字。

### 2. 【小红书极简干货正文】
- 开门见山痛点（「这篇教程帮你解决什么问题」）
- 采用步骤拆解排版（动作名称 + 组数×次数 + 核心发力点，必须用简单大白话讲清楚！）
- 穿插「⚠️避坑提醒」（用❌和✅对比，语气要真实如吐槽）
- 字数严格控制在 **600-800字** 左右！（精简！小红书用户没有耐心看几千字的长篇大论，直接给核心结论）

### 3. 【干货标签区】
- 6-8个精准标签（#健身 #新手跟练 等）

今日核心标题方向：『{{ $('📌 确立最终主题').first().json.output }}』

以下是由教练给出的权威干货模型：
『{{ $json.output }}』

请直接输出标题、高度去AI化正文和标签，无需无关废话！'''
        
    # 4. Bind QA to writer directly
    if n['id'] == 'qa':
        n['parameters']['text'] = n['parameters']['text'].replace(
            "### 去AI味润色后的小红书文案：\n{{ $('🔧 去AI味润色 Agent').first().json.output }}",
            "### 小红书配套正文：\n{{ $('✍️ 文案撰写 Agent').first().json.output }}"
        )
    
    # 5. Bind Output to writer directly
    if n['id'] == 'output':
        n['parameters']['assignments']['assignments'][0]['value'] = n['parameters']['assignments']['assignments'][0]['value'].replace(
            "# ✍🏻 小红书配套正文（已去AI味润色）\n{{ $('🔧 去AI味润色 Agent').first().json.output }}",
            "# ✍🏻 小红书配套正文\n{{ $('✍️ 文案撰写 Agent').first().json.output }}"
        )

# 6. Update Map Connections
# Remove deai mappings and route writer -> merge directly
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
    "✍️ 文案撰写 Agent": { "main": [ [ { "node": "内容汇总打包", "type": "main", "index": 1 } ] ] },
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
    }
}

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON successfully merged and optimized.")
