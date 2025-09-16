"""
Command-line interface for JSGF Tools.

This module provides clean CLI commands that use the modern JSGF API.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .grammar import Grammar
from .generators import DeterministicGenerator, ProbabilisticGenerator, GeneratorConfig
from .exceptions import JSGFError


def deterministic_command():
    """Command-line interface for deterministic generation."""
    parser = argparse.ArgumentParser(
        description='Generate all possible strings from a non-recursive JSGF grammar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s grammar.jsgf
  %(prog)s grammar.jsgf --rule greeting
  %(prog)s grammar.jsgf --max-results 100
        '''
    )

    parser.add_argument(
        'grammar_file',
        help='Path to the JSGF grammar file'
    )

    parser.add_argument(
        '--rule', '-r',
        help='Specific rule to generate from (default: all public rules)'
    )

    parser.add_argument(
        '--max-results', '-m',
        type=int,
        help='Maximum number of strings to generate'
    )

    parser.add_argument(
        '--max-recursion', '-d',
        type=int,
        default=50,
        help='Maximum recursion depth (default: 50)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )

    args = parser.parse_args()

    try:
        # Load grammar
        grammar = Grammar.from_file(args.grammar_file)

        # Check for recursion if no specific rule is given
        if not args.rule and grammar.is_recursive():
            print(
                "Warning: Grammar contains recursive rules. "
                "Consider using probabilistic generation instead.",
                file=sys.stderr
            )

        # Create generator
        config = GeneratorConfig(
            max_recursion_depth=args.max_recursion,
            max_results=args.max_results
        )
        generator = DeterministicGenerator(grammar, config)

        # Open output file if specified
        output_file = open(args.output, 'w') if args.output else sys.stdout

        try:
            # Generate strings
            for string in generator.generate(args.rule):
                print(string, file=output_file)
        finally:
            if args.output:
                output_file.close()

    except JSGFError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\\nGeneration interrupted", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def probabilistic_command():
    """Command-line interface for probabilistic generation."""
    parser = argparse.ArgumentParser(
        description='Generate random strings from a JSGF grammar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s grammar.jsgf 10
  %(prog)s grammar.jsgf 20 --rule greeting
  %(prog)s grammar.jsgf 5 --seed 42
        '''
    )

    parser.add_argument(
        'grammar_file',
        help='Path to the JSGF grammar file'
    )

    parser.add_argument(
        'count',
        type=int,
        help='Number of strings to generate'
    )

    parser.add_argument(
        '--rule', '-r',
        help='Specific rule to generate from (default: all public rules)'
    )

    parser.add_argument(
        '--seed', '-s',
        type=int,
        help='Random seed for reproducible results'
    )

    parser.add_argument(
        '--max-recursion', '-d',
        type=int,
        default=50,
        help='Maximum recursion depth (default: 50)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )

    args = parser.parse_args()

    try:
        # Load grammar
        grammar = Grammar.from_file(args.grammar_file)

        # Create generator
        config = GeneratorConfig(
            max_recursion_depth=args.max_recursion,
            random_seed=args.seed
        )
        generator = ProbabilisticGenerator(grammar, config)

        # Open output file if specified
        output_file = open(args.output, 'w') if args.output else sys.stdout

        try:
            # Generate specified number of strings
            strings = generator.generate_list(args.rule, args.count)
            for string in strings:
                print(string, file=output_file)
        finally:
            if args.output:
                output_file.close()

    except JSGFError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\\nGeneration interrupted", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def grammar_info_command():
    """Command-line interface for grammar information."""
    parser = argparse.ArgumentParser(
        description='Display information about a JSGF grammar',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'grammar_file',
        help='Path to the JSGF grammar file'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information'
    )

    args = parser.parse_args()

    try:
        # Load grammar
        grammar = Grammar.from_file(args.grammar_file)

        # Basic information
        print(f"Grammar: {args.grammar_file}")
        print(f"Total rules: {len(grammar)}")
        print(f"Public rules: {len(grammar.public_rules)}")

        if args.verbose:
            print("\\nPublic rules:")
            for rule in grammar.public_rules:
                print(f"  - {rule.name}")

            print("\\nAll rules:")
            for rule_name in sorted(grammar.rule_names):
                rule = grammar.get_rule(rule_name)
                visibility = "public" if rule.is_public else "private"
                print(f"  - {rule_name} ({visibility})")

        # Check for recursion
        if grammar.is_recursive():
            cycles = grammar.detect_cycles()
            print(f"\\nRecursive: Yes ({len(cycles)} cycle(s))")
            if args.verbose:
                for i, cycle in enumerate(cycles, 1):
                    print(f"  Cycle {i}: {' -> '.join(cycle)}")
        else:
            print("\\nRecursive: No")

        # Validation
        try:
            grammar.validate()
            print("Validation: Passed")
        except Exception as e:
            print(f"Validation: Failed - {e}")

    except JSGFError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)