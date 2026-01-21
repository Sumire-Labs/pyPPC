"""
pyPPC - Evaluator
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Callable

from .parser import AST, ValueNode, SectionNode, ConditionalNode, parse
from .config import Config
from .types import PPCType, validate_type
from .exceptions import EvaluationError, IncludeError


class Evaluator:
    """
    Evaluates the AST and produces a Config object.
    Handles environment variables, secrets, conditionals, and includes.
    """

    def __init__(
        self,
        base_path: Optional[Path] = None,
        secret_provider: Optional[Callable[[str], Optional[str]]] = None,
    ):
        self.base_path = base_path or Path.cwd()
        self.secret_provider = secret_provider
        self._included_files: set = set()

    def evaluate(self, ast: AST) -> Config:
        """Evaluate AST into Config."""
        data: Dict[str, Any] = {}

        # Process includes first
        for include in ast.includes:
            included_data = self._process_include(include.path, include.line)
            self._deep_merge(data, included_data)

        # Process sections
        for section in ast.sections:
            self._process_section(section, data)

        # Process conditionals
        for conditional in ast.conditionals:
            if self._evaluate_condition(conditional.condition):
                for section in conditional.sections:
                    self._process_section(section, data)

        return Config(data)

    def _process_section(self, section: SectionNode, data: Dict[str, Any]) -> None:
        """Process a section and add to data dict."""
        # Handle nested sections (e.g., "permissions.admin")
        parts = section.name.split(".") if section.name else []

        # Navigate/create nested structure
        current = data
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Process assignments
        for assignment in section.assignments:
            value = self._evaluate_value(assignment.value)
            current[assignment.key] = value

    def _evaluate_value(self, node: ValueNode) -> Any:
        """Evaluate a value node."""
        value = None

        # Environment variable
        if node.env_var:
            value = os.environ.get(node.env_var)
            if value is None and node.default:
                value = self._evaluate_value(node.default)
            elif value is None:
                value = None  # Will remain None if no default

        # Secret
        elif node.secret:
            if self.secret_provider:
                value = self.secret_provider(node.secret)
            else:
                # Try environment variable as fallback
                value = os.environ.get(f"SECRET_{node.secret}")

            if value is None and node.default:
                value = self._evaluate_value(node.default)

        # Array with potential env vars
        elif isinstance(node.value, list):
            value = self._evaluate_array(node.value)

        # Regular value
        else:
            value = node.value

        # Apply type validation
        if node.type_hint and value is not None:
            try:
                ppc_type = PPCType.from_string(node.type_hint)
                value = validate_type(value, ppc_type, node.line)
            except Exception as e:
                raise EvaluationError(str(e), line=node.line)

        return value

    def _evaluate_array(self, arr: list) -> list:
        """Evaluate array items, resolving any env vars or secrets."""
        result = []
        for item in arr:
            if isinstance(item, dict):
                if "$env" in item:
                    val = os.environ.get(item["$env"])
                    result.append(val)
                elif "$secret" in item:
                    if self.secret_provider:
                        val = self.secret_provider(item["$secret"])
                    else:
                        val = os.environ.get(f"SECRET_{item['$secret']}")
                    result.append(val)
                else:
                    result.append(item)
            else:
                result.append(item)
        return result

    def _evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a condition string.
        Supports: $env.VAR == "value", $env.VAR != "value"
        """
        condition = condition.strip()

        # Pattern: $env.VAR == "value" or $env.VAR != "value"
        match = re.match(
            r'\$env\.(\w+)\s*(==|!=)\s*["\']?([^"\']*)["\']?',
            condition
        )

        if match:
            var_name = match.group(1)
            operator = match.group(2)
            expected = match.group(3)

            actual = os.environ.get(var_name, "")

            if operator == "==":
                return actual == expected
            elif operator == "!=":
                return actual != expected

        # Pattern: $env.VAR (truthy check)
        match = re.match(r'\$env\.(\w+)$', condition)
        if match:
            var_name = match.group(1)
            return bool(os.environ.get(var_name))

        # Unknown condition - default to False
        return False

    def _process_include(self, path: str, line: int) -> Dict[str, Any]:
        """Process an @include directive."""
        # Resolve path
        if not os.path.isabs(path):
            full_path = self.base_path / path
        else:
            full_path = Path(path)

        # Check for circular includes
        resolved = full_path.resolve()
        if resolved in self._included_files:
            raise IncludeError(f"Circular include detected: {path}", line=line)

        self._included_files.add(resolved)

        # Read and parse included file
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            raise IncludeError(f"Include file not found: {path}", line=line)
        except Exception as e:
            raise IncludeError(f"Error reading include file: {e}", line=line)

        # Parse and evaluate included file
        included_ast = parse(text)
        included_evaluator = Evaluator(
            base_path=full_path.parent,
            secret_provider=self.secret_provider,
        )
        included_evaluator._included_files = self._included_files

        included_config = included_evaluator.evaluate(included_ast)
        return included_config.to_dict()

    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Deep merge two dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value


def evaluate(ast: AST, base_path: Optional[Path] = None) -> Config:
    """Convenience function to evaluate AST."""
    evaluator = Evaluator(base_path=base_path)
    return evaluator.evaluate(ast)
