# Deployment — 3YZN Discord Bot

For a local or hosted process, install Python dependencies, provide environment variables securely, and run `python bot.py`. Use `SYNC_MODE=guild` for development and `SYNC_MODE=global` for production. Keep logs accessible to maintainers but free of tokens and credentials. Configure a restart policy with your host's process manager rather than running multiple bot copies against the same bot token.
