"""
Init command
"""

import sys
from pathlib import Path

from ..i18n import t


TEMPLATES = {
    "minimal": '''# Configuration
>> app
  name = "myapp"
  debug :: bool = false
''',
    "bot": '''# Discord Bot Configuration
>> bot
  token :: str = $env.DISCORD_TOKEN
  prefix :: str = "!"
  description = "My Discord Bot"

>> database
  host = "localhost"
  port :: int = 5432
  password = $secret.DB_PASS

>> cogs
  enabled = ["music", "moderation", "fun"]

>> @when $env.ENV == "dev"
  >> bot
    debug = true
    prefix = "??"
''',
    "web": '''# Web Application Configuration
>> server
  host = "0.0.0.0"
  port :: int = $env.PORT ?? 8080
  debug :: bool = false

>> database
  url = $env.DATABASE_URL ?? "sqlite:///app.db"

>> session
  secret_key = $secret.SESSION_KEY
  expire :: int = 3600

>> @when $env.ENV == "dev"
  >> server
    debug = true
    host = "127.0.0.1"
''',
}


def cmd_init(args) -> int:
    """Create a new .ppc file from template."""
    output = Path(args.output)

    if output.exists():
        print(t("init.exists", path=output), file=sys.stderr)
        return 1

    template_content = TEMPLATES.get(args.template, TEMPLATES["minimal"])

    with open(output, "w", encoding="utf-8") as f:
        f.write(template_content)

    print(t("init.success", path=output))
    return 0
