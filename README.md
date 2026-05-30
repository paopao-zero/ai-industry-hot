# AI Industry HOT

AI Industry HOT 是一个面向中文用户的 AI 行业热点分析 Skill 与轻量自动推送示例。它会抓取 AIHOT 的公开 AI 行业资讯，筛选高价值事件，并从 AI 产业链上游、中游、下游视角整理影响路径、利好/利空/中性/待观察判断、推送理由和风险提示。

> 以下内容仅作产业研究和信息整理，不构成投资建议、买卖建议、目标价预测或确定性市场判断。

## What It Does

- 使用 `SKILL.md` 为 AI agent 提供 AI 行业热点分析工作流。
- 默认关注模型发布、产品更新、算力硬件、云服务、Agent 应用、投融资并购、政策监管、开源生态和论文技术突破。
- 通过 GitHub Actions 每 30 分钟运行一次推送脚本，将简报发送到飞书 Demo 群。
- 使用飞书自定义机器人 Webhook，不需要维护服务器。

## Install The Skill

将本仓库克隆到本地后，把整个目录放入 Codex 的 skills 目录，或复制 `SKILL.md` 和 `agents/openai.yaml` 到你自己的 skill 目录中。

示例用法：

```text
Use $ai-industry-hot to summarize today's AI industry hotspots and explain their industry-chain impact in Chinese.
```

你也可以直接询问：

```text
今天 AI 行业有什么值得关注的热点？请按上中下游分析影响。
```

## Feishu Push Demo

本项目提供一个最小可运行的飞书推送雏形：

1. 在飞书群中添加自定义机器人。
2. 复制机器人 Webhook 地址。
3. 在 GitHub 仓库中进入 `Settings -> Secrets and variables -> Actions`。
4. 新增 repository secret：

```text
Name: FEISHU_WEBHOOK_URL
Value: 你的飞书机器人 webhook 地址
```

5. 进入 `Actions -> Feishu Push -> Run workflow` 手动测试。

默认定时任务每 30 分钟运行一次。GitHub Actions 的定时任务可能存在延迟，因此本项目描述为“定时抓取 / 准实时推送”，不承诺秒级实时性。

## Local Test

本地预览推送内容：

```bash
python scripts/feishu_push.py --dry-run
```

本地真实推送：

```bash
FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/..." python scripts/feishu_push.py
```

Windows PowerShell:

```powershell
$env:FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/..."
python scripts/feishu_push.py
```

## Output Example

```markdown
以下为产业研究视角的信息整理，不构成投资建议。

## AI 行业热点简报

### 1. 示例新闻标题
- 来源与时间：AIHOT，今天 09:30
- 原文链接：https://example.com
- 事件类型：模型发布
- 一句话摘要：某公司发布新一代多模态模型。
- 影响链条：模型能力提升 -> API 与应用场景扩展 -> 中下游生态活跃度提升
- 产业链影响：
  - 上游：算力与云基础设施，偏利好，训练和推理需求可能增加
  - 中游：模型与 API 平台，偏利好，生态影响力可能增强
  - 下游：办公、教育、内容生成应用，待观察，仍需验证真实采用率
- 推送理由：该事件可能影响模型竞争格局和应用开发节奏。
- 风险提示：单一发布不等于商业化成功，需观察价格、性能、生态采用和用户留存。
```

## Repository Notes

- 不要提交飞书 Webhook、API key、token、邮箱、手机号等敏感信息。
- `项目背景（灵感对话记录）.txt` 是个人创作过程材料，默认不进入公开仓库。
- 第一版不做数据库、不做多群分发、不做用户订阅。
- 如果后续群成员变多，可以考虑 GitHub Issue 申请入群，或迁移到正式飞书应用。

## Demo 推送群

本项目的自动简报会推送到飞书 Demo 群，欢迎扫码查看运行效果。

> 说明：二维码可能过期；如果无法加入，可以在 GitHub Issue 中留言获取新的群入口。

将你的飞书群二维码图片保存为 `assets/feishu-group-qr.png` 后，取消下面这一行的注释即可在 GitHub README 中显示：

<!-- ![飞书 Demo 推送群](assets/feishu-group-qr.png) -->

## License

MIT
