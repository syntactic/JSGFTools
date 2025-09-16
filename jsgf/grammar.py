"""
JSGF Grammar representation and parsing functionality.
"""

from typing import Dict, List, Optional, Union, TextIO, Iterator
from pathlib import Path
import re
from io import StringIO

from .ast_nodes import (
    JSGFNode, Terminal, NonTerminal, Sequence, Alternative,
    Optional as OptionalNode, Group, Rule
)
from .exceptions import ParseError, ValidationError
from .legacy_adapter import LegacyAdapter


class Grammar:
    """
    Represents a complete JSGF grammar with rules and provides parsing functionality.

    This class encapsulates all grammar rules and provides methods for parsing,
    validation, and rule lookup.
    """

    def __init__(self):
        self._rules: Dict[str, Rule] = {}
        self._public_rules: List[Rule] = []

    @classmethod
    def from_string(cls, grammar_text: str) -> 'Grammar':
        """
        Parse a grammar from a string.

        Args:
            grammar_text: The JSGF grammar text to parse

        Returns:
            A Grammar instance

        Raises:
            ParseError: If the grammar cannot be parsed
        """
        grammar = cls()
        adapter = LegacyAdapter()

        try:
            with StringIO(grammar_text) as f:
                adapter.parse_to_grammar(f, grammar)
        except Exception as e:
            raise ParseError(f"Failed to parse grammar: {e}")

        grammar.validate()
        return grammar

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'Grammar':
        """
        Parse a grammar from a file.

        Args:
            file_path: Path to the JSGF grammar file

        Returns:
            A Grammar instance

        Raises:
            ParseError: If the grammar cannot be parsed
            FileNotFoundError: If the file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Grammar file not found: {file_path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return cls.from_stream(f)
        except Exception as e:
            raise ParseError(f"Failed to parse grammar file {file_path}: {e}")

    @classmethod
    def from_stream(cls, stream: TextIO) -> 'Grammar':
        """
        Parse a grammar from a text stream.

        Args:
            stream: Text stream containing JSGF grammar

        Returns:
            A Grammar instance

        Raises:
            ParseError: If the grammar cannot be parsed
        """
        grammar = cls()
        adapter = LegacyAdapter()

        try:
            adapter.parse_to_grammar(stream, grammar)
        except Exception as e:
            raise ParseError(f"Failed to parse grammar: {e}")

        grammar.validate()
        return grammar

    def add_rule(self, rule: Rule) -> None:
        """
        Add a rule to the grammar.

        Args:
            rule: The rule to add

        Raises:
            ValueError: If a rule with the same name already exists
        """
        if rule.name in self._rules:
            raise ValueError(f"Rule '{rule.name}' already exists")

        self._rules[rule.name] = rule
        if rule.is_public:
            self._public_rules.append(rule)

    def get_rule(self, name: str) -> Optional[Rule]:
        """
        Get a rule by name.

        Args:
            name: The rule name (with or without angle brackets)

        Returns:
            The rule if found, None otherwise
        """
        # Handle both <name> and name formats
        clean_name = name.strip('<>')
        return self._rules.get(f"<{clean_name}>")

    def has_rule(self, name: str) -> bool:
        """
        Check if a rule exists.

        Args:
            name: The rule name (with or without angle brackets)

        Returns:
            True if the rule exists, False otherwise
        """
        return self.get_rule(name) is not None

    @property
    def rules(self) -> Dict[str, Rule]:
        """Get all rules in the grammar."""
        return self._rules.copy()

    @property
    def public_rules(self) -> List[Rule]:
        """Get all public rules in the grammar."""
        return self._public_rules.copy()

    @property
    def rule_names(self) -> List[str]:
        """Get all rule names."""
        return list(self._rules.keys())

    @property
    def public_rule_names(self) -> List[str]:
        """Get all public rule names."""
        return [rule.name for rule in self._public_rules]

    def validate(self) -> None:
        """
        Validate the grammar for consistency and completeness.

        Raises:
            ValidationError: If the grammar is invalid
        """
        errors = []

        # Check that all referenced non-terminals have rules
        for rule in self._rules.values():
            undefined_refs = self._find_undefined_references(rule.expansion)
            if undefined_refs:
                errors.append(
                    f"Rule '{rule.name}' references undefined non-terminals: "
                    f"{', '.join(undefined_refs)}"
                )

        # Check for at least one public rule
        if not self._public_rules:
            errors.append("Grammar must have at least one public rule")

        if errors:
            raise ValidationError("Grammar validation failed:\n" + "\n".join(errors))

    def _find_undefined_references(self, node: JSGFNode) -> List[str]:
        """Find all undefined non-terminal references in a node."""
        undefined = []

        def visit(n: JSGFNode):
            if isinstance(n, NonTerminal):
                if not self.has_rule(n.name):
                    undefined.append(n.name)
            elif isinstance(n, Sequence):
                for element in n.elements:
                    visit(element)
            elif isinstance(n, Alternative):
                for choice_node, _ in n.choices:
                    visit(choice_node)
            elif isinstance(n, (OptionalNode, Group)):
                visit(n.element)

        visit(node)
        return undefined

    def detect_cycles(self) -> List[List[str]]:
        """
        Detect cycles in the grammar rules.

        Returns:
            List of cycles, where each cycle is a list of rule names
        """
        # Build dependency graph
        graph = {}
        for rule_name, rule in self._rules.items():
            graph[rule_name] = self._get_direct_dependencies(rule.expansion)

        # Find strongly connected components (cycles)
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor, path.copy())

            rec_stack.remove(node)

        for rule_name in self._rules:
            if rule_name not in visited:
                dfs(rule_name, [])

        return cycles

    def _get_direct_dependencies(self, node: JSGFNode) -> List[str]:
        """Get direct non-terminal dependencies of a node."""
        dependencies = []

        def visit(n: JSGFNode):
            if isinstance(n, NonTerminal):
                dependencies.append(n.name)
            elif isinstance(n, Sequence):
                for element in n.elements:
                    visit(element)
            elif isinstance(n, Alternative):
                for choice_node, _ in n.choices:
                    visit(choice_node)
            elif isinstance(n, (OptionalNode, Group)):
                visit(n.element)

        visit(node)
        return dependencies

    def is_recursive(self, rule_name: Optional[str] = None) -> bool:
        """
        Check if the grammar (or a specific rule) contains recursion.

        Args:
            rule_name: If provided, check if this specific rule is recursive.
                      If None, check if any rule in the grammar is recursive.

        Returns:
            True if recursion is detected, False otherwise
        """
        cycles = self.detect_cycles()

        if rule_name is None:
            return len(cycles) > 0

        # Check if the specific rule is involved in any cycle
        clean_name = rule_name.strip('<>')
        full_name = f"<{clean_name}>"

        for cycle in cycles:
            if full_name in cycle:
                return True

        return False

    def __str__(self) -> str:
        """Return a string representation of the grammar."""
        lines = []
        for rule in self._rules.values():
            lines.append(str(rule))
        return "\n".join(lines)

    def __len__(self) -> int:
        """Return the number of rules in the grammar."""
        return len(self._rules)

    def __contains__(self, rule_name: str) -> bool:
        """Check if a rule name exists in the grammar."""
        return self.has_rule(rule_name)

    def __iter__(self) -> Iterator[Rule]:
        """Iterate over all rules in the grammar."""
        return iter(self._rules.values())