# SLAObot
SLAO Technologies introduce ability to automatically blame you guildmates 
as soon as WCL log is posted into logspam channel by WCL bot. 
SLAO bot will get report link from that message and will provide rankings information 
either for full clear or for up to 4 fights. 


## Dev setup
1. Clone the repo
2. Setup venv. This is optional but more convenient then system wide installation of our dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
3. Install dependencies (inside the activated venv)
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
```
4. Fill in config/base.cfg and config/guild.cfg. There are template files for these configs.
5. Run the bot
```powershell
cd slao_bot
python -m slaobot
```

## Commands

All commands use the configured prefix from `config/base.cfg` (by default `slaobot-local!`).

- **Sync slash commands**
  - Text: `slaobot-local!sync`
  - Description: Syncs slash commands for the current guild.

- **Raid statistics (slash commands)**
  - `/report <report_id>` – подробный отчёт по логу WCL.
  - `/potions <report_id>` – статистика по зельям/камням и пре-потам.
  - `/gear <report_id>` – проверка камней, энчантов и оффспек‑лутa.
  - `/engineers <report_id>` – использование гранат и инженерных расходников.

- **EPGP (slash commands)**
  - `/epgp [target]` – EPGP персонажа (по нику персонажа или вашему нику в Дискорде, если не указано имя персонажа).
  - `/raidloot` – последний рейд‑лут.
  - `/points` – последние начисления EP/GP.
  - `/standing [standing_filter]` – таблица EPGP гильдии (`all`, `non-zero`, `cap`).

- **Signup / newcomers (slash command)**
  - `/signup` – анкета для новых игроков, отправляется офицерам.
