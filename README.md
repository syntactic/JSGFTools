# JSGF Grammar Tools

This set of tools can be used primarily to generate strings from a JSGF
grammar, but it also provides an easy to use JSGFParser module which creates
abstract syntax trees for JSGF grammars. Developers can use these ASTs to 
help create more tools for their purposes. For more detailed documentation,
refer to the Sphinx documentation located in docs/_build/html/index.html

## Dependencies

- Python 2.7
- PyParsing module (http://pyparsing.wikispaces.com/Download+and+Installation)

## Instructions

The two main Python scripts are DeterministicGenerator.py and
ProbabilisticGenerator.py. Both files require a grammar file as a command
line argument, and the latter also requires a number, which refers to the number
of sentences to generate. Importantly, DeterministicGenerator.py should not take
grammars with recursive rules as an argument. A recursive rule is of the form:

```<nonTerminal> = this (comes | goes) back to <nonTerminal>;```

There are two example grammars included with the scripts: Ideas.gram and 
IdeasNonRecursive.gram. Ideas.gram is an example of a grammar with recursive
rules, though the recursion is not as direct as the above example. It's a good
idea to run these grammars with the generator scripts to see how the scripts 
work:

```> python DeterministicGenerator.py IdeasNonRecursive.gram

> python ProbabilisticGenerator.py Ideas.gram 20```

### Notes

- Larger grammars take a longer time to parse, so if nothing seems to be generating,
wait a few seconds and the grammar should be parsed. 

- Most of JSGF as described in [http://www.w3.org/TR/2000/NOTE-jsgf-20000605/] is
supported, but there are a few things that have not been implemented by these
tools yet:
    - Kleene operators
    - Imports and Grammar Names
    - Tags
