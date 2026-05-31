# AI Industry HOT

AI Industry HOT is a Codex Skill and lightweight automation example for AI industry news briefings. It fetches public AIHOT items, filters high-signal events, and turns them into concise Chinese briefings with industry-chain impact analysis across upstream, midstream, and downstream segments.

> This project is for industry research and information organization only. It does not provide investment advice, trading recommendations, target prices, or deterministic market forecasts.

## What It Does

- Provides an AI industry news analysis workflow through `SKILL.md`.
- Focuses on model releases, product launches, compute infrastructure, cloud services, agent applications, financing and M&A, regulation, open source ecosystems, and research breakthroughs.
- Runs a GitHub Actions workflow every 30 minutes to generate a briefing and send it to a Feishu demo group.
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

Send a real Feishu message locally:

```bash
FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/..." python scripts/feishu_push.py
```

Windows PowerShell:

```powershell
$env:FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/..."
python scripts/feishu_push.py
```

## Output Example

The skill can generate Chinese briefings by default, but the structure looks like this in English:

```markdown
The following is an industry research summary and does not constitute investment advice.

## AI Industry Briefing

### 1. Example News Title
- Source and time: AIHOT, today 09:30
- Original link: https://example.com
- Event type: Model release
- One-sentence summary: A company released a new multimodal model.
- Impact path: Better model capability -> broader API and application scenarios -> stronger midstream and downstream ecosystem activity
- Industry-chain impact:
  - Upstream: Compute and cloud infrastructure, bullish bias, training and inference demand may increase
  - Midstream: Foundation models and API platforms, bullish bias, ecosystem influence may strengthen
  - Downstream: Office, education, and content generation applications, watchlist, real adoption still needs validation
- Push rationale: This event may affect the model competition landscape and the application development cycle.
- Risk note: A single launch does not equal commercial success. Pricing, performance, ecosystem adoption, and user retention still need to be tracked.
```

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
