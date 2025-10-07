# Dark Own

## Quick configuration check

1. Create a `.env` file alongside this repository with your bot credentials. For example:
   ```env
   API_ID=2032193
   API_HASH=8e06818e6ca64ab674031280c063b2e1
   BOT_TOKEN=5208722762:AAGQmIy-WhZrFJNOj068GwPXf_kYKSNanxk
   ADMINS=1291364201
   CHANNELS=-1001769102299 -1001329116889
   AUTH_CHANNEL=-1001802060546
   CACHE_TIME=100
   CUSTOM_FILE_CAPTION="<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <code>{file_name}</code>\n\n=========== • ✠ • ===========\n▫️ ɢʀᴏᴜᴘ : </b><b>@CinimaAdholokaam</b> \n<b>▫️ ᴄʜᴀɴɴᴇʟ : </b><b>@Calinkzz</b>\n<b>=========== • ✠ • ===========</b>"
   P_TTI_SHOW_OFF=False
   SINGLE_BUTTON=True
   SPELL_CHECK_REPLY=True
   RP_CHANNEL=-1001527001672
   ```

2. Run the configuration health check script to make sure the bot can start with your environment:
   ```bash
   python scripts/config_healthcheck.py --env-file .env
   ```
   The script re-imports `info.py`, prints the resolved IDs/booleans, and reports missing variables.

3. (Optional) Run the automated tests for additional safety:
   ```bash
   python scripts/config_healthcheck.py --env-file .env --run-tests
   ```

If you prefer to export variables manually instead of using a `.env` file, run:
```bash
export $(grep -v '^#' .env | xargs)
python scripts/config_healthcheck.py --run-tests
```
