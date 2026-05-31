# AI Industry HOT

[![Feishu Push](https://github.com/paopao-zero/ai-industry-hot/actions/workflows/feishu-push.yml/badge.svg)](https://github.com/paopao-zero/ai-industry-hot/actions/workflows/feishu-push.yml)
[![CI](https://github.com/paopao-zero/ai-industry-hot/actions/workflows/ci.yml/badge.svg)](https://github.com/paopao-zero/ai-industry-hot/actions/workflows/ci.yml)

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

5. Open `Actions -> Feishu Push -> Run workflow` to test the workflow manually. Manual runs can choose the number of cards, the fallback threshold, and card/text output.

The scheduled workflow runs every 30 minutes at minute 7 and 37 of each UTC hour. GitHub Actions scheduled jobs can be delayed, so this project describes the automation as scheduled or near-real-time push, not strict real-time monitoring.

## Automation Reliability

- `.github/workflows/feishu-push.yml` runs the Feishu push on a 30-minute schedule and supports manual runs.
- The workflow validates Python syntax before sending messages.
- A concurrency guard prevents overlapping push jobs when GitHub Actions is delayed.
- `.github/workflows/ci.yml` runs syntax checks and unit tests on pushes, pull requests, and manual dispatches.
- If the `FEISHU_WEBHOOK_URL` secret is missing, manual and scheduled push jobs fail fast without exposing sensitive values.

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

Run the offline checks:

```bash
python -m py_compile scripts/feishu_push.py
python -m unittest discover -s tests -t . -v
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

Save the Feishu group QR code as `assets/feishu-group-qr.png`, then uncomment the line below to display it on GitHub:

<!-- ![Feishu demo push group](assets/feishu-group-qr.png) -->

## License

MIT
