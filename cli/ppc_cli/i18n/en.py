"""
English messages for pyPPC CLI
"""

MESSAGES = {
    # General
    "app": {
        "description": "pyPPC - A human-readable configuration format",
        "version": "pyPPC version {version}",
    },

    # Commands
    "commands": {
        "validate": "Validate a configuration file",
        "format": "Format a configuration file",
        "to_json": "Convert to JSON format",
        "to_yaml": "Convert to YAML format",
        "get": "Get a value by key path",
        "env": "List required environment variables",
        "init": "Create a new configuration file from template",
    },

    # Arguments
    "args": {
        "file": "Path to configuration file",
        "output": "Output file (default: stdout)",
        "write": "Write result back to file",
        "indent": "JSON indent (default: 2)",
        "key": "Key path (e.g., bot.token)",
        "check": "Check if all env vars are set",
        "template": "Template type",
        "lang": "Set language (ja/en)",
    },

    # Validate command
    "validate": {
        "success": "[OK] {path} is valid",
        "error": "[NG] {path} has errors",
    },

    # Format command
    "format": {
        "success": "[OK] Formatted {path}",
    },

    # Convert commands
    "convert": {
        "success": "[OK] Saved to {path}",
    },

    # Get command
    "get": {
        "not_found": "Key not found: {key}",
    },

    # Env command
    "env": {
        "header_env": "Environment variables:",
        "header_secrets": "Secrets (SECRET_*):",
        "all_set": "[OK] All environment variables are set",
        "missing": "Missing environment variables:",
    },

    # Init command
    "init": {
        "success": "[OK] Created {path}",
        "exists": "[NG] {path} already exists",
        "templates": {
            "minimal": "Minimal",
            "bot": "Discord Bot",
            "web": "Web Application",
        },
    },

    # Errors
    "errors": {
        "file_not_found": "File not found: {path}",
        "parse_error": "Parse error: {message}",
        "unknown_error": "Error: {message}",
    },
}
