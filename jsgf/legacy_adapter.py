"""
Adapter to use the existing JSGFParser with the new Grammar architecture.

This provides a bridge between the old parser and the new modern API.
"""

from typing import TextIO
import sys
import os

# Add the parent directory to the path to import the legacy modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import JSGFParser as legacy_parser
import JSGFGrammar as legacy_grammar

from .ast_nodes import (
    JSGFNode, Terminal, NonTerminal, Sequence, Alternative,
    Optional as OptionalNode, Group, Rule
)
from .exceptions import ParseError


class LegacyAdapter:
    """Adapter to convert legacy grammar objects to new AST format."""

    def parse_to_grammar(self, stream: TextIO, grammar: 'Grammar') -> None:
        """
        Parse using the legacy parser and convert to new Grammar format.

        Args:
            stream: Text stream containing JSGF grammar
            grammar: Grammar object to populate
        """
        try:
            # Use the legacy parser
            legacy_gram = legacy_parser.getGrammarObject(stream)

            # Create a set of public rule names for easy lookup
            public_rule_names = {rule.lhs.name for rule in legacy_gram.publicRules}

            # Convert all rules, marking public ones appropriately
            for rule in legacy_gram.rules:
                is_public = rule.lhs.name in public_rule_names
                converted_rule = self._convert_rule(rule, is_public=is_public)
                grammar.add_rule(converted_rule)

        except Exception as e:
            raise ParseError(f"Failed to parse grammar: {e}")

    def _convert_rule(self, legacy_rule, is_public: bool = False) -> Rule:
        """Convert a legacy rule to new Rule format."""
        rule_name = legacy_rule.lhs.name
        expansion = self._convert_expansion(legacy_rule.rhs)

        return Rule(
            name=rule_name,
            expansion=expansion,
            is_public=is_public
        )

    def _convert_expansion(self, rhs) -> JSGFNode:
        """Convert legacy RHS to new AST format."""
        if isinstance(rhs, str):
            return Terminal(rhs)
        elif isinstance(rhs, list):
            if len(rhs) == 1:
                return self._convert_expansion(rhs[0])
            else:
                # Convert list to sequence
                elements = [self._convert_expansion(item) for item in rhs]
                return Sequence(elements)
        elif isinstance(rhs, legacy_grammar.Disjunction):
            # Convert disjunction
            choices = []
            for disjunct in rhs.disjuncts:
                if isinstance(disjunct, tuple):
                    # Weighted choice
                    node, weight = disjunct
                    choices.append((self._convert_expansion(node), weight))
                else:
                    # Unweighted choice
                    choices.append((self._convert_expansion(disjunct), 1.0))
            return Alternative(choices)
        elif isinstance(rhs, legacy_grammar.Optional):
            return OptionalNode(self._convert_expansion(rhs.option))
        elif isinstance(rhs, legacy_grammar.NonTerminal):
            return NonTerminal(rhs.name)
        else:
            # Fallback for unknown types
            return Terminal(str(rhs))