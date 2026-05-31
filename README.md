# AI Industry HOT

AI Industry HOT is a Codex Skill and lightweight automation example for AI industry news briefings. It fetches public AIHOT items, filters high-signal events, and turns them into concise Chinese briefings with industry-chain impact analysis across upstream, midstream, and downstream segments.

> This project is for industry research and information organization only. It does not provide investment advice, trading recommendations, target prices, or deterministic market forecasts.

## What It Does

- Provides an AI industry news analysis workflow through `SKILL.md`.
- Focuses on model releases, product launches, compute infrastructure, cloud services, agent applications, financing and M&A, regulation, open source ecosystems, and research breakthroughs.
- Runs a GitHub Actions workflow every 30 minutes to generate mobile-friendly Feishu card messages and send them to a demo group.
- Uses a Feishu custom bot webhook, so no always-on server is required.

## Install The Skill

Clone this repository and place the whole folder in your Codex skills directory, or copy `SKILL.md` and `agents/openai.yaml` into your own skill folder.

Example prompt:

```text
Use $ai-industry-hot to summarize today's AI industry hotspots and explain their industry-chain impact in Chinese.
```

Another example:

```text
What AI industry news is worth watching today? Analyze the upstream, midstream, and downstream impact in Chinese.
```

## Feishu Push Demo

This repository includes a minimal Feishu push workflow:

1. Add a custom bot to your Feishu group.
2. Copy the bot webhook URL.
3. Open your GitHub repository settings and go to `Settings -> Secrets and variables -> Actions`.
4. Add a repository secret:

```text
Name: FEISHU_WEBHOOK_URL
Value: your Feishu custom bot webhook URL
```

5. Open `Actions -> Feishu Push -> Run workflow` to test the workflow manually.

The scheduled workflow runs every 30 minutes. GitHub Actions scheduled jobs can be delayed, so this project describes the automation as scheduled or near-real-time push, not strict real-time monitoring.

## Local Test

Preview the generated briefing locally:

```bash
python scripts/feishu_push.py --dry-run
```

Preview the legacy plain-text format:

```bash
python scripts/feishu_push.py --dry-run --message-format text
```

Send a real Feishu message locally:

```bash
FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/..." python scripts/feishu_push.py
```

Windows PowerShell:

```powershell
$env:FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/..."
python scripts/feishu_push.py
```

## Output Style

The default Feishu push uses investor-focused interactive card messages instead of one long plain-text bubble. Each selected item is sent as a compact card with:

- a red industry-chain impact header
- a clickable news title and short summary
- upstream, midstream, and downstream impact notes near the top
- A-share-style impact markers: red for bullish, green for bearish
- source, time, event type, ranking, and time-window metadata

Use `--message-format text` only if your Feishu bot or workspace does not support interactive card messages.

## Notes For Users And Contributors

- Never commit Feishu webhooks, API keys, tokens, passwords, personal phone numbers, email addresses, or other secrets.
- Configure runtime secrets through GitHub Actions repository secrets instead of source files.
- Treat generated briefings as research summaries, not financial advice.
- The first version intentionally avoids databases, multi-group distribution, user subscription management, and a full Feishu app.
- If the demo group becomes hard to manage, maintainers may switch to GitHub Issues-based access requests or a formal Feishu application.

## Demo Push Group

The automated briefing can be sent to a Feishu demo group so users can observe the workflow output.

> Note: QR codes may expire. If the QR code no longer works, please open a GitHub Issue to request an updated group entry.

<img width="1029" height="1164" alt="69de22456940f86842a5d06d127fd114" src="https://github.com/user-attachments/assets/91c80b58-1acb-4a26-bd1a-d9e8852baf33" />


## License

MIT
