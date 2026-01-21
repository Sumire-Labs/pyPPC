# PPC Language Support for VSCode

VSCode extension for pyPPC (.ppc) configuration files.

## Features

- Syntax highlighting
- Code snippets
- Auto-closing brackets and quotes
- Comment toggling (Ctrl+/)
- Code folding

## Syntax Highlighting

![Syntax Highlighting](images/syntax-example.png)

Highlights:
- Sections (`>> section`)
- Type hints (`:: str`, `:: int`)
- Environment variables (`$env.VAR`)
- Secrets (`$secret.NAME`)
- Conditionals (`>> @when`)
- Strings, numbers, booleans
- Comments

## Snippets

| Prefix | Description |
|--------|-------------|
| `section` | New section |
| `section-nested` | Nested section |
| `kv` | Key value pair |
| `kvt` | Key value with type hint |
| `str` | String with type |
| `int` | Integer with type |
| `bool` | Boolean with type |
| `array` | Array value |
| `env` | Environment variable |
| `envd` | Env var with default |
| `secret` | Secret reference |
| `when` | Conditional section |
| `include` | Include file |
| `bot-template` | Discord bot template |
| `web-template` | Web app template |
| `comment` | Comment |
| `comment-block` | Comment block |

## Installation

### From VSIX file

1. Download the `.vsix` file
2. Open VSCode
3. Press `Ctrl+Shift+P`
4. Type "Install from VSIX"
5. Select the downloaded file

### Manual Installation

1. Copy the `vsc-ppc-plugin` folder to:
   - Windows: `%USERPROFILE%\.vscode\extensions\ppc-plugin`
   - macOS: `~/.vscode/extensions/ppc-plugin`
   - Linux: `~/.vscode/extensions/ppc-plugin`
2. Restart VSCode

### Build VSIX (for developers)

```bash
npm install -g @vscode/vsce
cd vsc-ppc-plugin
vsce package
# ppc-plugin-0.1.0.vsix が生成される
```

## Example

```ppc
# Bot Configuration

>> bot
  token :: str = $env.DISCORD_TOKEN
  prefix :: str = "!"
  debug :: bool = false

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
```

## License

WTFPL
