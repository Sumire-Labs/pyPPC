"""
Japanese messages for pyPPC CLI
"""

MESSAGES = {
    # General
    "app": {
        "description": "pyPPC - 人間が読みやすい設定ファイルフォーマット",
        "version": "pyPPC バージョン {version}",
    },

    # Commands
    "commands": {
        "validate": "設定ファイルを検証する",
        "format": "設定ファイルを整形する",
        "to_json": "JSON形式に変換する",
        "to_yaml": "YAML形式に変換する",
        "get": "指定したキーの値を取得する",
        "env": "必要な環境変数を一覧表示する",
        "init": "テンプレートから新しい設定ファイルを作成する",
    },

    # Arguments
    "args": {
        "file": "設定ファイルのパス",
        "output": "出力ファイル (省略時: 標準出力)",
        "write": "結果をファイルに上書き保存する",
        "indent": "JSONのインデント幅 (デフォルト: 2)",
        "key": "キーのパス (例: bot.token)",
        "check": "全ての環境変数が設定されているかチェックする",
        "template": "テンプレートの種類",
        "lang": "言語を指定する (ja/en)",
    },

    # Validate command
    "validate": {
        "success": "[OK] {path} は有効な設定ファイルです",
        "error": "[NG] {path} にエラーがあります",
    },

    # Format command
    "format": {
        "success": "[OK] {path} を整形しました",
    },

    # Convert commands
    "convert": {
        "success": "[OK] {path} に保存しました",
    },

    # Get command
    "get": {
        "not_found": "キーが見つかりません: {key}",
    },

    # Env command
    "env": {
        "header_env": "環境変数:",
        "header_secrets": "シークレット (SECRET_*):",
        "all_set": "[OK] 全ての環境変数が設定されています",
        "missing": "未設定の環境変数があります:",
    },

    # Init command
    "init": {
        "success": "[OK] {path} を作成しました",
        "exists": "[NG] {path} は既に存在します",
        "templates": {
            "minimal": "最小構成",
            "bot": "Discord Bot用",
            "web": "Webアプリケーション用",
        },
    },

    # Errors
    "errors": {
        "file_not_found": "ファイルが見つかりません: {path}",
        "parse_error": "構文エラー: {message}",
        "unknown_error": "エラーが発生しました: {message}",
    },
}
