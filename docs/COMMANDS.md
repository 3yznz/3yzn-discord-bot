# Command reference — 3YZN Discord Bot

- General: `/say`, `/help`, `/avatar`, `/banner`, `/user`, `/server`, `/come`.
- Moderation: `/kick`, `/ban`, `/unban`, `/timeout`, `/untimeout`, `/mute`, `/unmute`, `/clear`, `/slowmode`, `/nickname`, `/unnickname`.
- Channels: `/hide-channel`, `/unhide-channel`.
- Roles: `/role-add`, `/role-remove`, `/role-add-bulk`, `/role-remove-bulk`. Bulk member input accepts IDs or mentions separated by spaces or commas and is capped by `BULK_ROLE_LIMIT`.
- Embeds: `/embed`.
- Separator automation: `/separator-set`, `/separator-remove`, `/separator-exempt-channel-add`, `/separator-exempt-channel-remove`, `/separator-settings`. Matching is case-insensitive substring by default, or exact matching.
- Auto responses: `/autoresponse-add`, `/autoresponse-edit`, `/autoresponse-remove`, `/autoresponse-list`.
- Settings: `/settings-mute-role`.

`/mute` means assigning a configured role. It is distinct from voice mute and native timeout. There is no `/unkick` operation in Discord.
