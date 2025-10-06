"""
String generators for JSGF grammars.

This module provides generators that can produce strings from JSGF grammars
in both deterministic and probabilistic ways.
"""

from typing import List, Iterator, Optional, Set, Dict, Any
from abc import ABC, abstractmethod
import random
import itertools
from collections import defaultdict

from .grammar import Grammar
from .ast_nodes import (
    JSGFNode, Terminal, NonTerminal, Sequence, Alternative,
    Optional as OptionalNode, Group, Rule
)
from .exceptions import GenerationError, RecursionError


class GeneratorConfig:
    """Configuration for string generators."""

    def __init__(
        self,
        max_recursion_depth: int = 50,
        max_results: Optional[int] = None,
        random_seed: Optional[int] = None,
        optimize_memory: bool = True
    ):
        self.max_recursion_depth = max_recursion_depth
        self.max_results = max_results
        self.random_seed = random_seed
        self.optimize_memory = optimize_memory


class BaseGenerator(ABC):
    """
    Base class for all JSGF string generators.

    This class provides common functionality for working with grammars
    and generating strings from AST nodes.
    """

    def __init__(self, grammar: Grammar, config: Optional[GeneratorConfig] = None):
        self.grammar = grammar
        self.config = config or GeneratorConfig()
        self._recursion_tracker: Dict[str, int] = defaultdict(int)

        if self.config.random_seed is not None:
            random.seed(self.config.random_seed)

    @abstractmethod
    def generate(self, rule_name: Optional[str] = None) -> Iterator[str]:
        """
        Generate strings from the grammar.

        Args:
            rule_name: Name of the rule to start generation from.
                      If None, uses all public rules.

        Yields:
            Generated strings
        """
        pass

    def generate_list(self, rule_name: Optional[str] = None, limit: Optional[int] = None) -> List[str]:
        """
        Generate a list of strings from the grammar.

        Args:
            rule_name: Name of the rule to start generation from
            limit: Maximum number of strings to generate

        Returns:
            List of generated strings
        """
        results = []
        count = 0

        for string in self.generate(rule_name):
            results.append(string)
            count += 1

            if limit and count >= limit:
                break
            if self.config.max_results and count >= self.config.max_results:
                break

        return results

    def _process_node(self, node: JSGFNode, context: Optional[str] = None) -> Any:
        """
        Process a single AST node. Implementation depends on generator type.

        Args:
            node: The AST node to process
            context: Optional context for recursion tracking

        Returns:
            Processed result (type depends on implementation)
        """
        if isinstance(node, Terminal):
            return self._process_terminal(node)
        elif isinstance(node, NonTerminal):
            return self._process_nonterminal(node, context)
        elif isinstance(node, Sequence):
            return self._process_sequence(node, context)
        elif isinstance(node, Alternative):
            return self._process_alternative(node, context)
        elif isinstance(node, OptionalNode):
            return self._process_optional(node, context)
        elif isinstance(node, Group):
            return self._process_group(node, context)
        else:
            raise GenerationError(f"Unknown node type: {type(node)}")

    @abstractmethod
    def _process_terminal(self, node: Terminal) -> Any:
        """Process a terminal node."""
        pass

    @abstractmethod
    def _process_nonterminal(self, node: NonTerminal, context: Optional[str] = None) -> Any:
        """Process a non-terminal node."""
        pass

    @abstractmethod
    def _process_sequence(self, node: Sequence, context: Optional[str] = None) -> Any:
        """Process a sequence node."""
        pass

    @abstractmethod
    def _process_alternative(self, node: Alternative, context: Optional[str] = None) -> Any:
        """Process an alternative node."""
        pass

    @abstractmethod
    def _process_optional(self, node: OptionalNode, context: Optional[str] = None) -> Any:
        """Process an optional node."""
        pass

    def _process_group(self, node: Group, context: Optional[str] = None) -> Any:
        """Process a group node (default implementation)."""
        return self._process_node(node.element, context)

    def _check_recursion(self, rule_name: str) -> None:
        """Check for excessive recursion."""
        self._recursion_tracker[rule_name] += 1
        if self._recursion_tracker[rule_name] > self.config.max_recursion_depth:
            raise RecursionError(
                f"Maximum recursion depth ({self.config.max_recursion_depth}) "
                f"exceeded for rule '{rule_name}'"
            )

    def _enter_rule(self, rule_name: str) -> None:
        """Enter a rule (for recursion tracking)."""
        self._check_recursion(rule_name)

    def _exit_rule(self, rule_name: str) -> None:
        """Exit a rule (for recursion tracking)."""
        self._recursion_tracker[rule_name] -= 1


class DeterministicGenerator(BaseGenerator):
    """
    Generator that produces all possible strings from a grammar.

    This generator exhaustively enumerates all possible strings that can be
    generated from the grammar rules. It should only be used with non-recursive
    grammars to avoid infinite generation.
    """

    def generate(self, rule_name: Optional[str] = None) -> Iterator[str]:
        """
        Generate all possible strings from the grammar.

        Args:
            rule_name: Name of the rule to start generation from.
                      If None, generates from all public rules.

        Yields:
            All possible generated strings

        Raises:
            GenerationError: If generation fails
            RecursionError: If infinite recursion is detected
        """
        if rule_name:
            rule = self.grammar.get_rule(rule_name)
            if not rule:
                raise GenerationError(f"Rule '{rule_name}' not found")

            strings = self._process_node(rule.expansion, rule_name)
            for string in strings:
                yield string.strip()
        else:
            # Generate from all public rules
            for rule in self.grammar.public_rules:
                self._recursion_tracker.clear()
                strings = self._process_node(rule.expansion, rule.name)
                for string in strings:
                    yield string.strip()

    def _process_terminal(self, node: Terminal) -> List[str]:
        """Process a terminal node."""
        return [node.value]

    def _process_nonterminal(self, node: NonTerminal, context: Optional[str] = None) -> List[str]:
        """Process a non-terminal node."""
        rule = self.grammar.get_rule(node.name)
        if not rule:
            raise GenerationError(f"Undefined rule: {node.name}")

        self._enter_rule(node.name)
        try:
            result = self._process_node(rule.expansion, node.name)
        finally:
            self._exit_rule(node.name)

        return result

    def _process_sequence(self, node: Sequence, context: Optional[str] = None) -> List[str]:
        """Process a sequence node."""
        if not node.elements:
            return [""]

        # Get all possible strings for each element
        element_strings = []
        for element in node.elements:
            strings = self._process_node(element, context)
            element_strings.append(strings)

        # Compute cross product
        return self._combine_sequences(element_strings)

    def _process_alternative(self, node: Alternative, context: Optional[str] = None) -> List[str]:
        """Process an alternative node."""
        all_strings = []
        for choice_node, weight in node.choices:
            strings = self._process_node(choice_node, context)
            all_strings.extend(strings)
        return all_strings

    def _process_optional(self, node: OptionalNode, context: Optional[str] = None) -> List[str]:
        """Process an optional node."""
        strings = self._process_node(node.element, context)
        return [""] + strings  # Empty string plus all possible strings

    def _combine_sequences(self, element_strings: List[List[str]]) -> List[str]:
        """Combine lists of strings using cross product."""
        if not element_strings:
            return [""]

        result = []
        for combination in itertools.product(*element_strings):
            combined = " ".join(s for s in combination if s)
            result.append(combined)

        return result


class ProbabilisticGenerator(BaseGenerator):
    """
    Generator that produces random strings from a grammar.

    This generator randomly selects from alternatives based on weights and
    can handle recursive grammars safely through probabilistic termination.
    """

    def generate(self, rule_name: Optional[str] = None) -> Iterator[str]:
        """
        Generate random strings from the grammar.

        Args:
            rule_name: Name of the rule to start generation from.
                      If None, randomly selects from public rules.

        Yields:
            Random generated strings (infinite iterator)

        Raises:
            GenerationError: If generation fails
        """
        while True:
            self._recursion_tracker.clear()

            if rule_name:
                rule = self.grammar.get_rule(rule_name)
                if not rule:
                    raise GenerationError(f"Rule '{rule_name}' not found")

                yield self._process_node(rule.expansion, rule_name).strip()
            else:
                # Randomly select from public rules
                if not self.grammar.public_rules:
                    raise GenerationError("No public rules available")

                if len(self.grammar.public_rules) > 1:
                    # Multiple public rules - create virtual alternative
                    choices = [(rule.expansion, 1.0) for rule in self.grammar.public_rules]
                    virtual_alt = Alternative([choice for choice, _ in choices])
                    yield self._process_node(virtual_alt).strip()
                else:
                    # Single public rule
                    rule = self.grammar.public_rules[0]
                    yield self._process_node(rule.expansion, rule.name).strip()

    def generate_one(self, rule_name: Optional[str] = None) -> str:
        """
        Generate a single random string.

        Args:
            rule_name: Name of the rule to start generation from

        Returns:
            A single generated string
        """
        return next(self.generate(rule_name))

    def _process_terminal(self, node: Terminal) -> str:
        """Process a terminal node."""
        return node.value

    def _process_nonterminal(self, node: NonTerminal, context: Optional[str] = None) -> str:
        """Process a non-terminal node."""
        rule = self.grammar.get_rule(node.name)
        if not rule:
            raise GenerationError(f"Undefined rule: {node.name}")

        self._enter_rule(node.name)
        try:
            result = self._process_node(rule.expansion, node.name)
        finally:
            self._exit_rule(node.name)

        return result

    def _process_sequence(self, node: Sequence, context: Optional[str] = None) -> str:
        """Process a sequence node."""
        if not node.elements:
            return ""

        parts = []
        for element in node.elements:
            result = self._process_node(element, context)
            if result:  # Only add non-empty results
                parts.append(result)

        return " ".join(parts)

    def _process_alternative(self, node: Alternative, context: Optional[str] = None) -> str:
        """Process an alternative node."""
        if not node.choices:
            return ""

        # Use weighted random selection
        choices, weights = zip(*node.choices)
        selected_choice = random.choices(choices, weights=weights, k=1)[0]
        return self._process_node(selected_choice, context)

    def _process_optional(self, node: OptionalNode, context: Optional[str] = None) -> str:
        """Process an optional node."""
        # 50% chance of including the optional element
        if random.random() < 0.5:
            return self._process_node(node.element, context)
        else:
            return ""