# 小红书健身账号自动化运营

> 利用 n8n + AI 实现小红书健身教程内容的全自动化生产

## 📁 目录结构

```
xhs-yunying/
├── xiaohongshu-automation-workflow.json  ← 🔥 主工作流（导入 n8n 使用）
├── 需求.md                              ← 项目需求文档
├── README.md                            ← 本说明文档
└── 参考素材/
    └── 4.8卡片样例/                     ← 知识卡片参考图片 (1-7.png)
```

## 🚀 使用说明

1. 将 `xiaohongshu-automation-workflow.json` 导入 n8n
2. 配置「硅基流动大脑」节点的 API Key（SiliconFlow）
3. 可在「人工设定主题参数」节点指定主题，或留空自动生成
4. 执行工作流，输出包含 8 张教程知识卡片提示词 + 去AI味正文
