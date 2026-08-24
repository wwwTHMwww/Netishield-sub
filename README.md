# NetiShield GitHub Telegram V2Ray Bot

Everything runs through **GitHub Actions**; no VPS is required.

### Flow
Telegram → GitHub Actions bot → `data/configs.txt` → daily random selection → `subscriptions/netishield.txt`

The bot workflow checks Telegram every 5 minutes. GitHub Actions scheduled jobs can be delayed by GitHub, so the exact run time is approximate.

### GitHub Secrets
Add these repository secrets:
- `BOT_TOKEN`: Telegram BotFather token
- `GH_TOKEN`: GitHub token with repository Contents read/write permission
- `ALLOWED_USER_IDS`: optional comma-separated Telegram user IDs

The workflow automatically gets owner/repository from GitHub.

### Subscription URL
After the first successful publish:

`https://raw.githubusercontent.com/OWNER/REPO/main/subscriptions/netishield.txt`

### Important
Do not put Telegram or GitHub tokens directly into source files.
