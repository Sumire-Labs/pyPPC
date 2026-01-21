# pyPPC チートシート

## 基本構文

```ppc
# コメント
>> セクション名
  キー = "値"
```

## セクション

```ppc
>> bot                     # 基本セクション
>> database.connection     # ネストしたセクション (database.connection.*)
```

## 値の種類

```ppc
>> types
  string = "hello"         # 文字列
  number = 42              # 整数
  decimal = 3.14           # 小数
  flag = true              # 真偽値 (true/false/yes/no/on/off)
  empty = null             # 空値 (null/none/nil)
  list = [1, 2, 3]         # 配列
  mixed = ["a", 1, true]   # 混合配列
```

## 型ヒント

```ppc
>> config
  port :: int = 8080       # 整数型
  name :: str = "app"      # 文字列型
  rate :: float = 1.5      # 小数型
  debug :: bool = false    # 真偽値型
  items :: list = []       # 配列型
```

## 環境変数

```ppc
>> bot
  token = $env.DISCORD_TOKEN           # 必須
  port = $env.PORT ?? 8080             # デフォルト値付き
  host = $env.HOST ?? "localhost"      # 文字列のデフォルト
```

## シークレット

```ppc
>> database
  password = $secret.DB_PASS           # SECRET_DB_PASS 環境変数から取得
  api_key = $secret.API_KEY ?? ""      # デフォルト値付き
```

## 条件分岐

```ppc
>> @when $env.ENV == "dev"
  >> bot
    debug = true
    prefix = "??"

>> @when $env.ENV == "prod"
  >> bot
    debug = false
    prefix = "!"

>> @when $env.DEBUG                    # 真偽チェック
  >> logging
    level = "DEBUG"
```

## ファイル読み込み

```ppc
@include "secrets.ppc"
@include "config/base.ppc"
```

## Pythonでの使い方

```python
from ppc import load, loads, dump, dumps

# ファイルから読み込み
config = load("config.ppc")

# 文字列から読み込み
config = loads("""
>> bot
  prefix = "!"
""")

# 値へのアクセス
config.bot.prefix          # ドット記法
config["bot"]["prefix"]    # 辞書記法
config.bot.get("key", default)  # デフォルト値付き

# 設定の書き出し
dump(config, "output.ppc")
text = dumps(config)

# シークレット付きで読み込み
config = load("config.ppc", secrets={"DB_PASS": "password"})
config = load("config.ppc", secrets_file="secrets.json")
```

## Configオブジェクトのメソッド

```python
config.to_dict()           # 辞書に変換
config.get("key", default) # デフォルト値付きで取得
config.keys()              # キー一覧
config.values()            # 値一覧
config.items()             # キーと値のペア
"key" in config            # キーの存在確認
```

## クイックリファレンス

| 構文 | 説明 |
|------|------|
| `>> name` | セクション |
| `>> a.b` | ネストしたセクション |
| `key = value` | 代入 |
| `key :: type = value` | 型付き代入 |
| `# comment` | コメント |
| `$env.NAME` | 環境変数 |
| `$secret.NAME` | シークレット |
| `?? default` | デフォルト値 |
| `>> @when cond` | 条件分岐 |
| `@include "file"` | ファイル読み込み |
| `[a, b, c]` | 配列 |

## サポートされる型

| 型 | 値の例 |
|----|--------|
| `str` | `"text"`, `'text'` |
| `int` | `42`, `-1` |
| `float` | `3.14`, `-0.5` |
| `bool` | `true`, `false`, `yes`, `no`, `on`, `off` |
| `list` | `[1, 2, 3]` |
| `null` | `null`, `none`, `nil` |

## 例: Discord Bot設定

```ppc
# bot.ppc
>> bot
  token :: str = $env.DISCORD_TOKEN
  prefix :: str = "!"
  description = "私のBot"

>> database
  host = "localhost"
  port :: int = 5432
  password = $secret.DB_PASS

>> cogs
  enabled = ["music", "mod", "fun"]

>> permissions.admin
  users = [123456789]
  roles = ["Admin"]

>> @when $env.ENV == "dev"
  >> bot
    prefix = "??"
```
