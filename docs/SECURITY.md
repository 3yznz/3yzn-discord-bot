# Security — 3YZN Discord Bot

- Store secrets in `.env`; do not commit it. Reset any exposed bot token immediately.
- Use least-privilege bot permissions and place the bot role only as high as required.
- Restrict configuration commands to administrators.
- All database values are parameterized; never add arbitrary code execution or shell execution to commands.
- Bulk role actions are bounded and report partial failures.
- Automation requires Message Content Intent; enable it only if you intend to use these features.
- Back up SQLite data securely and keep it out of public repositories.
