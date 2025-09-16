"""
Abstract Syntax Tree nodes for JSGF grammars.

This module provides the core AST node classes that represent different
parts of a JSGF grammar structure.
"""

from typing import List, Union, Any, Optional
from abc import ABC, abstractmethod


class JSGFNode(ABC):
    """Base class for all JSGF AST nodes."""

    @abstractmethod
    def __str__(self) -> str:
        """Return a string representation of this node."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)})"


class Terminal(JSGFNode):
    """Represents a terminal symbol (token) in the grammar."""

    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Terminal) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class NonTerminal(JSGFNode):
    """Represents a non-terminal symbol in the grammar."""

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, NonTerminal) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


class Sequence(JSGFNode):
    """Represents a sequence of elements."""

    def __init__(self, elements: List[JSGFNode]):
        self.elements = elements

    def __str__(self) -> str:
        return " ".join(str(element) for element in self.elements)

    def __iter__(self):
        return iter(self.elements)

    def __len__(self) -> int:
        return len(self.elements)

    def __getitem__(self, index: int) -> JSGFNode:
        return self.elements[index]


class Alternative(JSGFNode):
    """Represents alternatives (choices) in the grammar."""

    def __init__(self, choices: List[Union[JSGFNode, tuple]]):
        """
        Initialize alternatives.

        Args:
            choices: List of choices. Each choice can be:
                    - A JSGFNode (unweighted)
                    - A tuple of (JSGFNode, weight) (weighted)
        """
        self.choices = []
        for choice in choices:
            if isinstance(choice, tuple):
                node, weight = choice
                self.choices.append((node, float(weight)))
            else:
                self.choices.append((choice, 1.0))  # Default weight

    def __str__(self) -> str:
        choice_strs = []
        for node, weight in self.choices:
            if weight != 1.0:
                choice_strs.append(f"/{weight}/ {node}")
            else:
                choice_strs.append(str(node))
        return "( " + " | ".join(choice_strs) + " )"

    def __iter__(self):
        return iter(self.choices)

    def __len__(self) -> int:
        return len(self.choices)

    def get_weights(self) -> List[float]:
        """Return the weights of all choices."""
        return [weight for _, weight in self.choices]

    def get_nodes(self) -> List[JSGFNode]:
        """Return the nodes of all choices."""
        return [node for node, _ in self.choices]


class Optional(JSGFNode):
    """Represents an optional element in the grammar."""

    def __init__(self, element: JSGFNode):
        self.element = element

    def __str__(self) -> str:
        return f"[ {self.element} ]"


class Group(JSGFNode):
    """Represents a grouped element."""

    def __init__(self, element: JSGFNode):
        self.element = element

    def __str__(self) -> str:
        return f"( {self.element} )"


class Rule:
    """Represents a complete grammar rule."""

    def __init__(self, name: str, expansion: JSGFNode, is_public: bool = False):
        self.name = name
        self.expansion = expansion
        self.is_public = is_public

    def __str__(self) -> str:
        prefix = "public " if self.is_public else ""
        return f"{prefix}<{self.name}> = {self.expansion};"

    def __repr__(self) -> str:
        return f"Rule(name='{self.name}', is_public={self.is_public})"