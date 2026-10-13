# 3YZN Discord Bot

**A modular Discord moderation and automation bot built with Python and discord.py 2.x.**

Copyright (c) 2026 3YZN. See [LICENSE](LICENSE) for the project license.

Repository URL placeholder: `https://github.com/3yznz/3yzn-discord-bot`

## Features

- Native slash commands, configurable guild/global synchronization, and asynchronous SQLite persistence.
- General commands: `/say`, `/help`, `/avatar`, `/banner`, `/user`, `/server`, `/come`.
- Moderation: `/kick`, `/ban`, `/unban`, `/timeout`, `/untimeout`, `/mute`, `/unmute`, `/clear`, `/slowmode`, `/nickname`, `/unnickname`.
- Channel visibility: `/hide-channel`, `/unhide-channel`.
- Role operations: `/role-add`, `/role-remove`, `/role-add-bulk`, `/role-remove-bulk`.
- Custom embeds: `/embed`.
- Separator image automation: `/separator-set`, `/separator-remove`, `/separator-exempt-channel-add`, `/separator-exempt-channel-remove`, `/separator-settings`.
- Custom responses: `/autoresponse-add`, `/autoresponse-edit`, `/autoresponse-remove`, `/autoresponse-list`.
- Mute-role configuration: `/settings-mute-role`.

## Requirements

- Python 3.11 or newer.
- A Discord application and bot created in the Discord Developer Portal.
- Bot token stored privately in `.env`; never paste it into source code or commit it.

## Windows installation

Open PowerShell in the project directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
python bot.py
```

Set `DISCORD_TOKEN` in `.env`. For the default `SYNC_MODE=guild`, set `DEV_GUILD_ID` to your test server's numeric ID. Keep the `.env` file private.

## Discord Developer Portal setup

1. Create an application at the Discord Developer Portal and add a bot user.
2. Copy the bot token into your local `.env` file only. If it is ever exposed, reset it immediately.
3. Under **Bot → Privileged Gateway Intents**, enable **Server Members Intent** and **Message Content Intent**. Members intent supports member-oriented commands and role/member operations. Message Content intent is required for separator and auto-response message matching.
4. Invite the bot using OAuth2 URL Generator with scopes `bot` and `applications.commands`. Grant only needed permissions: View Channels, Send Messages, Embed Links, Read Message History, Manage Messages (clear and deleting separator triggers), Manage Channels (hide/unhide and slowmode), Manage Roles, Kick Members, Ban Members, Moderate Members, and Manage Nicknames as needed. Do not grant Administrator unless you have a separate, deliberate reason.
5. Ensure the bot's highest role is above roles it must assign and members it must moderate.

## Sync modes

- Development: `SYNC_MODE=guild` and `DEV_GUILD_ID=...`. Guild command changes are normally visible quickly.
- Production: set `SYNC_MODE=global`. Global command propagation can take time. Do not repeatedly sync on every event; this project syncs once during startup.

## Configuration reference

| Variable | Purpose |
|---|---|
| `DISCORD_TOKEN` | Required bot token |
| `BOT_OWNER_ID` | Optional numeric owner ID reserved for future documented maintenance use |
| `DEV_GUILD_ID` | Required when guild sync is selected |
| `SYNC_MODE` | `guild` or `global`; defaults to `guild` |
| `DATABASE_PATH` | SQLite path; defaults to `data/3yzn.sqlite3` |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |
| `BULK_ROLE_LIMIT` | Maximum members per bulk role operation, 1–100; defaults to 20 |

## Database and backups

The bot initializes its SQLite schema on startup. Settings and automation rules are separated by guild ID. Stop the bot before making a simple file backup of `data/3yzn.sqlite3`, or use SQLite's online backup facilities if the bot must remain online. Never commit the database; it may contain private server configuration.

## Notes and limitations

- `/mute` and `/unmute` use a configured role, not Discord voice mute or native timeout. Configure with `/settings-mute-role` and set the role's channel permissions intentionally. Use `/timeout` for Discord's native timeout feature.
- Discord has no reversible `/unkick` command. A kicked user may rejoin using a valid invite if permitted.
- `/clear` relies on Discord's bulk-delete rules; messages older than 14 days cannot be bulk-deleted by Discord’s bulk endpoint; discord.py may delete them individually.
- `/hide-channel` changes only the `@everyone` view permission. Other role overrides may still grant access; it does not guarantee secrecy from every role.
- Separator automation deletes a triggering message only if Manage Messages is available and the channel is not exempt. It sends the image URL as a message, so Discord will display it only if the URL is accessible and supported.
- This project has not been validated against a live Discord server unless you perform the live setup and verify it yourself.

## Troubleshooting

- **No slash commands:** verify the bot was invited with `applications.commands`, check `SYNC_MODE` and `DEV_GUILD_ID`, and review startup logs. Global commands can take time to appear.
- **Message automation does not run:** enable Message Content Intent in both the portal and the code configuration, and restart the bot.
- **Role/moderation failure:** check bot permissions and role hierarchy. The bot cannot manage roles at or above its highest role.
- **Invalid token:** reset the token in the Developer Portal and update `.env`. Never include the token in a support request.

## License

This original project is licensed under the MIT License. Third-party dependencies retain their own licenses. Copyright notices do not transfer ownership of third-party software.
