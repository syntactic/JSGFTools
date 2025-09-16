"""
JSGF Grammar parser implementation.

This module provides the JSGFParser class that converts JSGF grammar text
into Grammar objects with proper AST representation.
"""

from typing import TextIO, List, Optional, Union, Any
import re
from pyparsing import (
    Word, Literal, Group, Optional as PyparsingOptional, Forward, MatchFirst,
    Combine, alphas, alphanums, nums, stringEnd, ParseException, ParserElement
)

from .ast_nodes import (
    JSGFNode, Terminal, NonTerminal, Sequence, Alternative,
    Optional as OptionalNode, Group as GroupNode, Rule
)
from .exceptions import ParseError


# Enable packrat parsing for performance
ParserElement.enablePackrat()


class JSGFParser:
    """
    Parser for JSGF grammar files.

    This parser converts JSGF grammar text into a Grammar object containing
    properly structured AST nodes.
    """

    def __init__(self):
        self._grammar_def = None
        self._setup_parser()

    def _setup_parser(self):
        """Set up the pyparsing grammar definition."""

        # Basic tokens
        weight = (
            Literal('/').suppress() +
            Word(nums + '.').setResultsName('weight_value') +
            Literal('/').suppress()
        ).setParseAction(self._parse_weight)

        token = (
            Word(alphanums + "'_-,.?@!#$%^&*()+={}[]|\\:;\"~`")
        ).setParseAction(self._parse_token)

        nonterminal = (
            Combine(
                Literal('<') +
                Word(alphanums + '$_:;,=|/\\()[]@#%!^&~') +
                Literal('>')
            )
        ).setParseAction(self._parse_nonterminal)

        # Forward declarations for recursive grammar
        sequence = Forward()
        alternative = Forward()

        # Weighted expressions
        weighted_expr = (
            weight + Group(sequence).setResultsName("expr")
        ).setParseAction(self._parse_weighted_expression)

        # Grouping and optional elements
        grouping = (
            Literal('(').suppress() +
            alternative +
            Literal(')').suppress()
        ).setParseAction(self._parse_group)

        optional_grouping = (
            Literal('[').suppress() +
            Group(alternative).setResultsName("optional_content") +
            Literal(']').suppress()
        ).setParseAction(self._parse_optional)

        # Basic expression elements
        expression = MatchFirst([
            nonterminal,
            token,
            grouping,
            optional_grouping
        ])

        # Sequence definition
        sequence <<= Group(
            expression +
            (expression)[...]
        ).setParseAction(self._parse_sequence)

        # Alternative definitions
        weighted_alternatives = Forward()
        weighted_prime = Literal('|').suppress() + weighted_alternatives
        weighted_alternatives <<= MatchFirst([
            (
                Group(weighted_expr).setResultsName("choice1") +
                Group(weighted_prime).setResultsName("choice2")
            ).setParseAction(self._parse_weighted_alternatives),
            Group(weighted_expr).setParseAction(self._parse_single_weighted)
        ])

        regular_alternatives = Forward()
        regular_prime = Literal('|').suppress() + regular_alternatives
        regular_alternatives <<= MatchFirst([
            (
                Group(sequence).setResultsName("choice1") +
                Group(regular_prime).setResultsName("choice2")
            ).setParseAction(self._parse_regular_alternatives),
            Group(sequence).setParseAction(self._parse_single_regular)
        ])

        # Top-level alternative
        alternative <<= MatchFirst([regular_alternatives, weighted_alternatives])

        # Complete rule definition
        rule_def = (
            PyparsingOptional(Literal('public')).setResultsName('is_public') +
            nonterminal.setResultsName('rule_name') +
            Literal('=').suppress() +
            Group(alternative).setResultsName('expansion') +
            Literal(';').suppress()
        ).setParseAction(self._parse_rule)

        self._grammar_def = rule_def

    def parse(self, stream: TextIO, grammar: 'Grammar') -> None:
        """
        Parse a JSGF grammar from a text stream into a Grammar object.

        Args:
            stream: Text stream containing JSGF grammar
            grammar: Grammar object to populate with parsed rules

        Raises:
            ParseError: If parsing fails
        """
        content = stream.read()

        # Remove comments
        content = self._remove_comments(content)

        # Split into individual rules and parse each one
        for line_num, line in enumerate(content.split('\n'), 1):
            line = line.strip()
            if not line:
                continue

            try:
                result = self._grammar_def.parseString(line, parseAll=True)
                rule = self._extract_rule(result)
                grammar.add_rule(rule)
            except ParseException as e:
                raise ParseError(
                    f"Failed to parse rule: {str(e)}",
                    line=line_num,
                    column=e.column if hasattr(e, 'column') else None
                )
            except Exception as e:
                raise ParseError(f"Unexpected error parsing rule: {str(e)}", line=line_num)

    def _remove_comments(self, text: str) -> str:
        """Remove comments from JSGF text."""
        # Remove // style comments
        text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
        # Remove /* */ style comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        return text

    def _parse_weight(self, s: str, loc: int, tokens: Any) -> float:
        """Parse a weight value."""
        return float(tokens.weight_value)

    def _parse_token(self, s: str, loc: int, tokens: Any) -> Terminal:
        """Parse a terminal token."""
        return Terminal(tokens[0])

    def _parse_nonterminal(self, s: str, loc: int, tokens: Any) -> NonTerminal:
        """Parse a non-terminal."""
        return NonTerminal(tokens[0])

    def _parse_sequence(self, s: str, loc: int, tokens: Any) -> Union[JSGFNode, Sequence]:
        """Parse a sequence of elements."""
        elements = list(tokens[0])
        if len(elements) == 1:
            return elements[0]
        return Sequence(elements)

    def _parse_group(self, s: str, loc: int, tokens: Any) -> GroupNode:
        """Parse a grouped expression."""
        return GroupNode(tokens[0])

    def _parse_optional(self, s: str, loc: int, tokens: Any) -> OptionalNode:
        """Parse an optional expression."""
        return OptionalNode(tokens.optional_content[0])

    def _parse_weighted_expression(self, s: str, loc: int, tokens: Any) -> tuple:
        """Parse a weighted expression."""
        weight = tokens[0]  # The weight value
        expr = tokens.expr[0]  # The expression
        return (expr, weight)

    def _parse_weighted_alternatives(self, s: str, loc: int, tokens: Any) -> Alternative:
        """Parse weighted alternatives."""
        choices = []

        # Add first choice
        first_choice = tokens.choice1[0]
        if isinstance(first_choice, tuple):
            choices.append(first_choice)
        else:
            choices.append((first_choice, 1.0))

        # Add remaining choices
        remaining = tokens.choice2[0]
        if isinstance(remaining, Alternative):
            choices.extend(remaining.choices)
        else:
            if isinstance(remaining, tuple):
                choices.append(remaining)
            else:
                choices.append((remaining, 1.0))

        return Alternative(choices)

    def _parse_single_weighted(self, s: str, loc: int, tokens: Any) -> Alternative:
        """Parse a single weighted choice."""
        choice = tokens[0]
        if isinstance(choice, tuple):
            return Alternative([choice])
        else:
            return Alternative([(choice, 1.0)])

    def _parse_regular_alternatives(self, s: str, loc: int, tokens: Any) -> Alternative:
        """Parse regular (unweighted) alternatives."""
        choices = []

        # Add first choice
        choices.append((tokens.choice1[0], 1.0))

        # Add remaining choices
        remaining = tokens.choice2[0]
        if isinstance(remaining, Alternative):
            choices.extend(remaining.choices)
        else:
            choices.append((remaining, 1.0))

        return Alternative(choices)

    def _parse_single_regular(self, s: str, loc: int, tokens: Any) -> Union[JSGFNode, Alternative]:
        """Parse a single regular choice."""
        choice = tokens[0]
        # Don't wrap single elements in Alternative unnecessarily
        return choice

    def _parse_rule(self, s: str, loc: int, tokens: Any) -> dict:
        """Parse a complete rule definition."""
        return {
            'is_public': bool(tokens.is_public),
            'name': tokens.rule_name.name,
            'expansion': tokens.expansion[0]
        }

    def _extract_rule(self, parse_result: Any) -> Rule:
        """Extract a Rule object from parse results."""
        return Rule(
            name=parse_result['name'],
            expansion=parse_result['expansion'],
            is_public=parse_result['is_public']
        )