# pyPPC

A human-readable configuration format for Python. Perfect for Discord bots and other applications.

## Features

- Human-readable syntax
- Type hints with validation
- Environment variable expansion (`$env.VAR`)
- Secret management (`$secret.NAME`)
- Conditional sections (`>> @when condition`)
- File includes (`@include "file.ppc"`)
- Default values (`$env.VAR ?? default`)
- Dot notation access (`config.section.key`)

## Installation

```bash
pip install pyPPC
```

Or install from source:

```bash
git clone https://github.com/yourusername/pyPPC
cd pyPPC
pip install -e .
```

## Quick Start

### Create a config file (`config.ppc`)

```ppc
# Bot configuration
>> bot
  token :: str = $env.DISCORD_TOKEN
  prefix :: str = "!"
  debug :: bool = false

>> database
  host = "localhost"
  port :: int = 5432
  password = $secret.DB_PASS ?? "default"

>> cogs
  enabled = ["music", "moderation", "fun"]

# Development overrides
>> @when $env.ENV == "dev"
  >> bot
    debug = true
    prefix = "??"
```

### Load in Python

```python
from ppc import load

config = load("config.ppc")

# Dot notation access
print(config.bot.token)
print(config.bot.prefix)      # "!"
print(config.database.port)   # 5432
print(config.cogs.enabled)    # ["music", "moderation", "fun"]

# Dict-style access also works
print(config["bot"]["token"])
```

## Syntax Reference

### Sections

```ppc
>> section_name
  key = value
```

### Nested Sections

```ppc
>> parent.child
  key = value
```

### Type Hints

```ppc
>> config
  name :: str = "myapp"
  port :: int = 8080
  debug :: bool = false
  rate :: float = 1.5
  items :: list = ["a", "b", "c"]
```

Supported types: `str`, `int`, `float`, `bool`, `list`

### Environment Variables

```ppc
>> bot
  token = $env.DISCORD_TOKEN
  port = $env.PORT ?? 8080      # with default value
```

### Secrets

```ppc
>> database
  password = $secret.DB_PASSWORD
```

Secrets are resolved in order:
1. Custom secret provider (if provided)
2. Environment variable `SECRET_<NAME>`
3. Default value (if specified)

### Arrays

```ppc
>> cogs
  enabled = ["music", "moderation", "fun"]
  ids = [123, 456, 789]
```

### Comments

```ppc
# This is a comment
>> bot
  token = "abc"  # inline comments work too
```

### Conditional Sections

```ppc
>> @when $env.ENV == "dev"
  >> bot
    debug = true

>> @when $env.ENV == "prod"
  >> bot
    debug = false
```

### Include Files

```ppc
@include "secrets.ppc"
@include "common/base.ppc"
```

## API Reference

### `load(path, **kwargs)`

Load a config file.

```python
from ppc import load

config = load("config.ppc")

# With custom secrets
config = load("config.ppc", secrets={"DB_PASS": "mypassword"})

# With secrets file
config = load("config.ppc", secrets_file="secrets.json")
```

### `loads(text, **kwargs)`

Load config from a string.

```python
from ppc import loads

config = loads("""
>> bot
  prefix = "!"
""")
```

### `dump(config, path)`

Write config to a file.

```python
from ppc import dump

dump(config, "output.ppc")
```

### `dumps(config)`

Convert config to string.

```python
from ppc import dumps

text = dumps(config)
```

## Using with Discord.py

```python
import discord
from discord.ext import commands
from ppc import load

config = load("bot.ppc")

bot = commands.Bot(
    command_prefix=config.bot.prefix,
    description=config.bot.description,
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Load cogs
for cog in config.cogs.enabled:
    bot.load_extension(f"cogs.{cog}")

bot.run(config.bot.token)
```

## Project Structure

```
pyPPC/
├── examples/          # Example .ppc files
├── lib/
│   └── ppc/          # Main package
├── packaging/        # Packaging utilities
├── tests/            # Test suite
├── pyproject.toml
└── README.md
```

## License

WTFPL - Do What The Fuck You Want To Public License
