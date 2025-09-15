# JSGF Grammar Tools

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for parsing and generating strings from JSGF (Java Speech Grammar Format) grammars. This modernized version supports Python 3.7+ and includes comprehensive testing.

## Features

- **Parser**: Convert JSGF grammar files into abstract syntax trees
- **Deterministic Generator**: Generate all possible strings from non-recursive grammars
- **Probabilistic Generator**: Generate random strings using weights and probabilities
- **Modern Python**: Full Python 3.7+ support with type hints and proper packaging
- **Comprehensive Testing**: Full test suite with pytest

## Installation

### From Source
```bash
git clone https://github.com/syntactic/JSGFTools.git
cd JSGFTools
pip install -e .
```

### Development Setup
```bash
git clone https://github.com/syntactic/JSGFTools.git
cd JSGFTools
pip install -r requirements-dev.txt
```

## Quick Start

### Command Line Usage

Generate all possible strings from a non-recursive grammar:
```bash
python DeterministicGenerator.py IdeasNonRecursive.gram
```

Generate 20 random strings from a grammar (supports recursive rules):
```bash
python ProbabilisticGenerator.py Ideas.gram 20
```

### Python API Usage

```python
import JSGFParser as parser
import DeterministicGenerator as det_gen
import ProbabilisticGenerator as prob_gen
from io import StringIO

# Parse a grammar
grammar_text = """
public <greeting> = hello | hi;
public <target> = world | there;
public <start> = <greeting> <target>;
"""

with StringIO(grammar_text) as f:
    grammar = parser.getGrammarObject(f)

# Generate all possibilities (deterministic)
det_gen.grammar = grammar
rule = grammar.publicRules[2]  # <start> rule
all_strings = det_gen.processRHS(rule.rhs)
print("All possible strings:", all_strings)

# Generate random string (probabilistic)
prob_gen.grammar = grammar
random_string = prob_gen.processRHS(rule.rhs)
print("Random string:", random_string)
```

## Grammar Format

JSGFTools supports most of the JSGF specification:

```jsgf
// Comments are supported
public <start> = <greeting> <target>;

// Alternatives with optional weights
<greeting> = /5/ hello | /1/ hi | hey;

// Optional elements
<polite> = [ please ];

// Nonterminal references
<target> = world | there;

// Recursive rules (use with ProbabilisticGenerator only)
<recursive> = base | <recursive> more;
```

### Supported Features
- Rule definitions and nonterminal references
- Alternatives (|) with optional weights (/weight/)
- Optional elements ([...])
- Grouping with parentheses
- Comments (// and /* */)
- Public and private rules

### Not Yet Supported
- Kleene operators (* and +)
- Import statements
- Tags

## Important Notes

### Recursive vs Non-Recursive Grammars

- **DeterministicGenerator**: Only use with non-recursive grammars to avoid infinite loops
- **ProbabilisticGenerator**: Can safely handle recursive grammars through probabilistic termination

**Example of recursive rule:**
```jsgf
<sentence> = <noun> <verb> | <sentence> and <sentence>;
```

## Testing

Run the test suite:
```bash
pytest test_jsgf_tools.py -v
```

Run specific test categories:
```bash
pytest test_jsgf_tools.py::TestJSGFParser -v      # Parser tests
pytest test_jsgf_tools.py::TestIntegration -v     # Integration tests
```

## Documentation

For detailed API documentation, build the Sphinx docs:
```bash
cd docs
make html
```

Then open `docs/_build/html/index.html` in your browser.

## Example Files

- `Ideas.gram`: Recursive grammar example (use with ProbabilisticGenerator)
- `IdeasNonRecursive.gram`: Non-recursive grammar example (use with DeterministicGenerator)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `pytest`
6. Submit a pull request

## License

MIT License. See [LICENSE](LICENSE) file for details.

## Version History

- **2.0.0**: Complete Python 3 modernization, added test suite, improved packaging
- **1.x**: Original Python 2.7 version
