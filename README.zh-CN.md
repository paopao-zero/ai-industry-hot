# AI Industry HOT 中文说明

AI Industry HOT 是一个面向中文用户的 AI 行业热点分析 Skill 与轻量自动推送示例。它会抓取 AIHOT 的公开 AI 行业资讯，筛选高价值事件，并从 AI 产业链上游、中游、下游视角整理影响路径、影响方向、推送理由和风险提示。

> 本项目只用于产业研究和信息整理，不构成投资建议、买卖建议、目标价预测或确定性市场判断。

## 项目能做什么

- 为 Codex 提供一个 `ai-industry-hot` Skill，用来生成中文 AI 行业热点简报。
- 默认关注模型发布、产品更新、算力硬件、云服务、Agent 应用、投融资并购、政策监管、开源生态和论文技术突破。
- 通过 GitHub Actions 每 30 分钟运行一次脚本，将简报推送到飞书 Demo 群。
- 使用飞书自定义机器人 Webhook，不需要自己维护服务器。

## 使用方式

将本仓库克隆到本地后，可以把整个目录放入 Codex 的 skills 目录；也可以只复制 `SKILL.md` 和 `agents/openai.yaml` 到你自己的 skill 目录中。

示例用法：

```text
Use $ai-industry-hot to summarize today's AI industry hotspots and explain their industry-chain impact in Chinese.
```

也可以直接这样问：

```text
今天 AI 行业有什么值得关注的热点？请按上中下游分析影响。
```

## 飞书推送演示

本项目提供一个最小可运行的飞书推送示例：

1. 在飞书群中添加自定义机器人。
2. 复制机器人的 Webhook 地址。
3. 打开 GitHub 仓库的 `Settings -> Secrets and variables -> Actions`。
4. 新增 repository secret：

```text
Name: FEISHU_WEBHOOK_URL
Value: 你的飞书机器人 Webhook 地址
```

5. 打开 `Actions -> Feishu Push -> Run workflow`，手动运行一次。

默认定时任务每 30 分钟运行一次。GitHub Actions 的定时任务可能存在延迟，所以本项目描述为“定时抓取 / 准实时推送”，不承诺秒级实时。

## 本地测试

本地预览简报内容：

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

## 输出示例

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

## 开源注意事项

• 切勿提交飞书webhook、应用程序API Key、密码、个人手机号、电子邮箱地址及其他机密信息。
• 请通过GitHub Actions仓库机密配置运行，不要将其写入源代码文件。
• 生成的简报仅作为研究总结，不构成任何投资建议。
• 首个版本暂未接入数据库、多群组分发功能、用户订阅管理功能以及完整的飞书应用。

## Demo 推送群

本项目的自动简报会推送到飞书 Demo 群，欢迎扫码查看运行效果。

> 说明：二维码可能过期；如果无法加入，可以在 GitHub Issue 中留言获取新的群入口。

将你的飞书群二维码图片保存为 `assets/feishu-group-qr.png` 后，取消下面这一行的注释即可在 GitHub README 中显示：

<!-- ![飞书 Demo 推送群](assets/feishu-group-qr.png) -->

## 许可证

MIT License
