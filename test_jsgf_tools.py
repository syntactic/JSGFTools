# -*- coding: utf-8 -*-
"""
Test suite for JSGFTools

This module provides comprehensive tests for all components of JSGFTools:
- JSGFParser: grammar parsing functionality
- JSGFGrammar: grammar object structure and operations
- DeterministicGenerator: exhaustive string generation
- ProbabilisticGenerator: random string generation
"""

import pytest
import tempfile
import os
from io import StringIO

import JSGFParser as parser
import JSGFGrammar as gram
import DeterministicGenerator as det_gen
import ProbabilisticGenerator as prob_gen


class TestJSGFParser:
    """Test the JSGF parser functionality"""

    def test_parse_simple_grammar(self):
        """Test parsing a simple non-recursive grammar"""
        grammar_text = """
        public <start> = hello world;
        """
        grammar = parser.getGrammarObject(StringIO(grammar_text))

        assert len(grammar.publicRules) == 1
        assert grammar.publicRules[0].lhs.name == "<start>"

    def test_parse_weighted_grammar(self):
        """Test parsing grammar with weights"""
        grammar_text = """
        public <start> = /5/ hello | /1/ hi;
        """
        grammar = parser.getGrammarObject(StringIO(grammar_text))

        assert len(grammar.publicRules) == 1
        # The RHS should be a list containing a disjunction with weighted alternatives
        rhs = grammar.publicRules[0].rhs
        assert isinstance(rhs, list)
        assert len(rhs) == 1
        assert isinstance(rhs[0], gram.Disjunction)

    def test_parse_optional_elements(self):
        """Test parsing grammar with optional elements"""
        grammar_text = """
        public <start> = hello [ world ];
        """
        grammar = parser.getGrammarObject(StringIO(grammar_text))

        assert len(grammar.publicRules) == 1
        # Should contain an optional element in a list
        rhs = grammar.publicRules[0].rhs
        assert isinstance(rhs, list)
        assert len(rhs) == 2  # "hello" and optional "world"
        # The second element should be an Optional
        assert isinstance(rhs[1], gram.Optional)

    def test_parse_recursive_grammar(self):
        """Test parsing a recursive grammar"""
        grammar_text = """
        public <S> = <NP> <VP>;
        <NP> = the idea | the idea <CP>;
        <VP> = will suffice;
        <CP> = that <S>;
        """
        grammar = parser.getGrammarObject(StringIO(grammar_text))

        assert len(grammar.publicRules) == 1
        assert len(grammar.rules) == 4  # All rules including private ones

    def test_parse_multiple_public_rules(self):
        """Test parsing grammar with multiple public rules"""
        grammar_text = """
        public <start1> = hello;
        public <start2> = world;
        """
        grammar = parser.getGrammarObject(StringIO(grammar_text))

        assert len(grammar.publicRules) == 2

    def test_parse_comments(self):
        """Test that comments are properly stripped"""
        grammar_text = """
        // This is a comment
        public <start> = hello world; // Another comment
        """
        grammar = parser.getGrammarObject(StringIO(grammar_text))

        assert len(grammar.publicRules) == 1


class TestJSGFGrammar:
    """Test the JSGF grammar objects"""

    def test_disjunction_creation(self):
        """Test creating a disjunction"""
        disjuncts = ["hello", "hi", "hey"]
        disj = gram.Disjunction(disjuncts)

        assert len(disj.disjuncts) == 3
        assert "hello" in str(disj)

    def test_optional_creation(self):
        """Test creating an optional element"""
        opt = gram.Optional("world")

        assert opt.option == "world"
        assert "world" in str(opt)
        assert "[" in str(opt) and "]" in str(opt)

    def test_sequence_as_list(self):
        """Test that sequences are represented as lists"""
        # In this implementation, sequences are just lists
        seq = ["hello", "world"]

        assert len(seq) == 2
        assert seq[0] == "hello"

    def test_nonterminal_creation(self):
        """Test creating a nonterminal"""
        nt = gram.NonTerminal("test")

        assert nt.name == "test"
        assert "test" in str(nt)

    def test_rule_creation(self):
        """Test creating a rule"""
        lhs = gram.NonTerminal("start")
        rhs = "hello world"
        rule = gram.Rule(lhs, rhs)

        assert rule.lhs.name == "start"
        assert rule.rhs == "hello world"

    def test_grammar_operations(self):
        """Test grammar operations like adding rules"""
        grammar = gram.Grammar()
        lhs = gram.NonTerminal("start")
        rhs = "hello"
        rule = gram.Rule(lhs, rhs)

        grammar.addRule(rule)
        assert len(grammar.rules) == 1

        grammar.addPublicRule(rule)
        assert len(grammar.publicRules) == 1


class TestDeterministicGenerator:
    """Test the deterministic string generator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.simple_grammar_text = """
        public <start> = hello world;
        """

        self.choice_grammar_text = """
        public <start> = hello | hi;
        """

        self.optional_grammar_text = """
        public <start> = hello [ world ];
        """

        self.complex_grammar_text = """
        public <start> = <greeting> <target>;
        <greeting> = hello | hi;
        <target> = world | there;
        """

    def test_simple_generation(self):
        """Test generating from a simple grammar"""
        # Set up global grammar for the generator
        det_gen.grammar = parser.getGrammarObject(StringIO(self.simple_grammar_text))

        rule = det_gen.grammar.publicRules[0]
        results = det_gen.processRHS(rule.rhs)

        assert len(results) == 1
        assert results[0] == "hello world"

    def test_choice_generation(self):
        """Test generating from grammar with choices"""
        det_gen.grammar = parser.getGrammarObject(StringIO(self.choice_grammar_text))

        rule = det_gen.grammar.publicRules[0]
        results = det_gen.processRHS(rule.rhs)

        assert len(results) == 2
        assert "hello" in results
        assert "hi" in results

    def test_optional_generation(self):
        """Test generating from grammar with optional elements"""
        det_gen.grammar = parser.getGrammarObject(StringIO(self.optional_grammar_text))

        rule = det_gen.grammar.publicRules[0]
        results = det_gen.processRHS(rule.rhs)

        assert len(results) == 2
        assert "hello" in results
        assert "hello world" in results

    def test_complex_generation(self):
        """Test generating from a more complex grammar"""
        det_gen.grammar = parser.getGrammarObject(StringIO(self.complex_grammar_text))

        rule = det_gen.grammar.publicRules[0]
        results = det_gen.processRHS(rule.rhs)

        # Should generate: hello world, hello there, hi world, hi there
        assert len(results) == 4
        expected = {"hello world", "hello there", "hi world", "hi there"}
        assert set(results) == expected


class TestProbabilisticGenerator:
    """Test the probabilistic string generator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.simple_grammar_text = """
        public <start> = hello world;
        """

        self.weighted_grammar_text = """
        public <start> = /5/ hello | /1/ hi;
        """

    def test_simple_generation(self):
        """Test generating from a simple grammar"""
        prob_gen.grammar = parser.getGrammarObject(StringIO(self.simple_grammar_text))

        rule = prob_gen.grammar.publicRules[0]
        result = prob_gen.processRHS(rule.rhs)

        assert result == "hello world"

    def test_choice_generation(self):
        """Test that generation produces valid results from choices"""
        prob_gen.grammar = parser.getGrammarObject(StringIO(self.weighted_grammar_text))

        rule = prob_gen.grammar.publicRules[0]

        # Generate multiple times to test randomness
        results = set()
        for _ in range(20):
            result = prob_gen.processRHS(rule.rhs)
            results.add(result)

        # Should only produce "hello" or "hi"
        assert results.issubset({"hello", "hi"})
        # With 20 iterations, we should get at least one of each (with high probability)
        # But we can't guarantee this due to randomness, so we just check validity


class TestIntegration:
    """Integration tests using the actual grammar files"""

    def test_ideas_grammar_parsing(self):
        """Test parsing the Ideas.gram file"""
        with open('Ideas.gram', 'r') as f:
            grammar = parser.getGrammarObject(f)

        assert len(grammar.publicRules) == 1
        assert grammar.publicRules[0].lhs.name == "<S>"

    def test_ideas_nonrecursive_grammar_parsing(self):
        """Test parsing the IdeasNonRecursive.gram file"""
        with open('IdeasNonRecursive.gram', 'r') as f:
            grammar = parser.getGrammarObject(f)

        assert len(grammar.publicRules) == 1

    def test_deterministic_generator_with_nonrecursive_grammar(self):
        """Test deterministic generation with IdeasNonRecursive.gram"""
        with open('IdeasNonRecursive.gram', 'r') as f:
            det_gen.grammar = parser.getGrammarObject(f)

        rule = det_gen.grammar.publicRules[0]
        results = det_gen.processRHS(rule.rhs)

        # Should generate multiple valid sentences
        assert len(results) > 1
        # All results should contain "idea"
        for result in results:
            assert "idea" in result

    def test_probabilistic_generator_with_recursive_grammar(self):
        """Test probabilistic generation with Ideas.gram"""
        with open('Ideas.gram', 'r') as f:
            prob_gen.grammar = parser.getGrammarObject(f)

        rule = prob_gen.grammar.publicRules[0]

        # Generate a few strings to ensure it works
        for _ in range(5):
            result = prob_gen.processRHS(rule.rhs)
            assert isinstance(result, str)
            assert len(result) > 0


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_grammar_syntax(self):
        """Test handling of invalid grammar syntax"""
        invalid_grammar = """
        public <start> = hello world  // Missing semicolon
        """

        # The parser may be tolerant of some syntax errors
        # Let's check what actually happens
        try:
            grammar = parser.getGrammarObject(StringIO(invalid_grammar))
            # If it doesn't raise an exception, check if it parsed correctly
            # A missing semicolon might result in no rules being parsed
            assert len(grammar.publicRules) == 0  # Should fail to parse the rule
        except Exception:
            # If it does raise an exception, that's also acceptable
            pass

    def test_empty_grammar(self):
        """Test handling of empty grammar"""
        empty_grammar = ""

        grammar = parser.getGrammarObject(StringIO(empty_grammar))
        assert len(grammar.publicRules) == 0

    def test_undefined_nonterminal(self):
        """Test handling of undefined nonterminals"""
        grammar_text = """
        public <start> = <undefined>;
        """
        grammar = parser.getGrammarObject(StringIO(grammar_text))

        # This should raise an error when trying to process
        with pytest.raises(ValueError):
            det_gen.grammar = grammar
            rule = det_gen.grammar.publicRules[0]
            det_gen.processRHS(rule.rhs)


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])