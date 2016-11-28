"""
This file parses a JSGF grammar file and returns a JSGFGrammar object. \
        It uses the pyparsing module and defines a grammar for JSGF grammars. \
        Upon finding a string or JSGF expression, it builds a grammar object from \
        the bottom up, composing JSGF expressions with strings and lists. When the \
        entire right hand side of a rule has been parsed and a JSGF expression \
        object has been created of it, it gets added to the main JSGFGrammar \
        object as one of its rules.

To run the parser independently and print the resulting JSGFGrammar object, \
        run it as:

        ``python JSGFParser.py Ideas.gram``

Generally, this module should be imported and the getGrammarObject should be called \
        with a ``file`` object as its argument. This function returns a grammar \
        object that can be used by the Generator scripts ``DeterministicGenerator.py`` \
        and ``ProbabilisticGenerator.py``.

The features of JSGF that this parser can handle include:
    - rulenames
    - tokens
    - comments
    - rule definitions
    - rule expansions
    - sequences
    - alternatives
    - weights
    - grouping
    - optional grouping

Notable features of JSGF that are **not** handled by this parser are:
    - grammar names
    - import statements
    - unary operators
    - tags

"""

# @copyright: (c)Copyright 2014, THC All Rights Reserved.
# The source code contained or described here in and all documents related
# to the source code ("Material") are owned by THC or its
# suppliers or licensors. Title to the Material remains with THC
# or its suppliers and licensors. The Material contains trade secrets and
# proprietary and confidential information of THC or its suppliers and
# licensors.

# The Material is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without THC's prior express written permission.

# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by THC in writing.

# @organization: THC Science
# @summary: This file parses a JSGF Grammar and prints it out.
# @since: 2014/06/02

import sys
import JSGFGrammar as gram
from pyparsing import * 

sys.setrecursionlimit(100000)
usePackrat = True

def foundWeight(s, loc, toks):
    """
    PyParsing action to run when a weight is found.

    :returns: Weight as a floating point number
    """
    #print 'found weight', toks.dump()
    #print 'returning the weight', float(toks.weightAmount)
    return float(toks.weightAmount)

def foundToken(s, loc, toks):
    """
    PyParsing action to run when a token is found.

    :returns: Token as a string
    """
    #print 'found token', toks.dump()
    #print 'returning the token', toks.token
    return toks.token

def foundNonterminal(s, loc, toks):
    """
    PyParsing action to run when a nonterminal reference is found.

    :returns: NonTerminal object representing the NT reference found
    """
    return gram.NonTerminal(list(toks)[0])

def foundWeightedExpression(s, loc, toks):
    """
    PyParsing action to run when a weighted expression is found.

    :returns: Ordered pair of the expression and its weight
    """
    toks.weightedExpression = (toks.expr, toks.weight)
    #print 'found weighted expression', toks.dump()
    expr = list(toks.expr)
    if len(expr) == 1:
        expr = expr[0]
    pair = (expr, toks.weight)
    #print 'returning', pair
    return pair

def foundPair(s, loc, toks):
    """
    PyParsing action to run when a pair of alternatives are found.

    :returns: Disjunction object containing all disjuncts that have been accumulated so far
    """
    #print 'found pair', toks.dump()
    #print 'disj1 is', list(toks.disj1), 'disj2 is', list(toks.disj2)
    firstAlternative = list(toks.disj1)
    secondAlternative = list(toks.disj2)
    if len(firstAlternative) > 1:
        disj = [firstAlternative]
    else:
        disj = firstAlternative
    if len(secondAlternative) == 1:
        if isinstance(secondAlternative[0], gram.Disjunction):
            #print 'found disjuncts in second alt', secondAlternative[0].disjuncts
            disj.extend(secondAlternative[0].disjuncts)
        else:
            disj.append(secondAlternative[0])
    else:
        disj.append(secondAlternative)
    disj = gram.Disjunction(disj)
    #print 'returing the pair', disj
    return disj

def foundOptionalGroup(s, loc, toks):
    """
    PyParsing action to run when an optional group is found.

    :returns: Optional object containing all elements in the group
    """
    #print 'optional item is', toks.optionalItem
    if len(list(toks[0])) > 1:
        return gram.Optional(list(toks[0]))
    else:
        return gram.Optional(toks.optionalItem[0])

def foundSeq(s, loc, toks):
    """
    PyParsing action to run when a sequence of concatenated elements is found.

    :returns: List of JSGFGrammar objects, strings, or more lists
    """
    #print 'seq is', toks.dump()
    #print 'length of seq is', len(list(toks[0])), list(toks[0])
    if len(list(toks[0])) > 1:
        #print 'seq retringin', list(toks[0]), type(list(toks[0]))
        return list(toks[0])
    else:
        #print 'seq returning', list(toks[0])[0], type(list(toks[0])[0])
        return list(toks[0])[0]

# PyParsing rule for a weight
weight = (Literal('/').suppress() + (Word(nums + '.')).setResultsName('weightAmount') + Literal('/').suppress()).setParseAction(foundWeight).setResultsName("weight")

# PyParsing rule for a token
token = Word(alphanums+"'_-").setResultsName('token').setParseAction(foundToken)

# PyParsing rule for a nonterminal reference
nonterminal = Combine(Literal('<') + Word(alphanums+'$_:;,=|/\\()[]@#%!^&~') + Literal('>')).setParseAction(foundNonterminal).setResultsName('NonTerminal')

Sequence = Forward()

weightedExpression = (weight + Group(Sequence).setResultsName("expr")).setResultsName('weightedExpression').setParseAction(foundWeightedExpression)

weightAlternatives = Forward()
weightedPrime = Literal('|').suppress() + weightAlternatives
weightAlternatives << MatchFirst([(Group(weightedExpression).setResultsName("disj1") + Group(weightedPrime).setResultsName("disj2")).setParseAction(foundPair).setResultsName("pair"), Group(weightedExpression).setParseAction(foundSeq)])

disj = Forward()
disjPrime = Literal('|').suppress() + disj
disj << MatchFirst([(Group(Sequence).setResultsName("disj1") + Group(disjPrime).setResultsName("disj2")).setParseAction(foundPair).setResultsName("pair"), Group(Sequence).setParseAction(foundSeq)])

topLevel = MatchFirst([disj, weightAlternatives])
StartSymbol = Optional(Literal('public')).setResultsName('public') + nonterminal.setResultsName('identifier') + Literal('=').suppress() + Group(topLevel).setResultsName('ruleDef') + Literal(';').suppress() + stringEnd


Expression = MatchFirst([nonterminal, token])

Grouping = Literal('(').suppress() + topLevel + Literal(')').suppress()
OptionalGrouping = (Literal('[').suppress() + Group(topLevel).setResultsName("optionalItem") + Literal(']').suppress()).setParseAction(foundOptionalGroup)

Sequence << Group(OneOrMore(MatchFirst([Grouping, OptionalGrouping, Expression]))).setResultsName("seq").setParseAction(foundSeq)

def nocomment(oldline):
    """
    Removes a comment from a line

    :param oldline: String representing the original line
    :returns: String with the same semantic content, with the comments stripped
    """
    if '//' in oldline:
        return oldline.replace(oldline, oldline[0:oldline.index('//')])
    elif '*' in oldline:
        return oldline.replace(oldline, '')
    else:
        return oldline

def getGrammarObject(fileStream):
    """
    Produces a JSGFGrammar object from a stream of text, the grammar object has a set of public rules and regular rules

    :param fileStream: file object containing the contents of the grammar file
    :type fileStream: file object
    :returns: JSGFGrammar object
    """
    linegenerator = fileStream
    lines = linegenerator.readlines()
    for i in range(len(lines)):
        lines[i] = nocomment(lines[i])
    # buffer will accumulate lines until a fully parseable piece is found
    buffer = ""

    grammar = gram.Grammar()
    for line in lines:
        buffer += line

        match = next(StartSymbol.scanString(buffer), None)
        while match:
            tokens, start, end = match
            #print 'rule dict is', tokens.asDict()
            if 'public' in tokens.keys():
                grammar.addPublicRule(gram.Rule(tokens.identifier, list(tokens.ruleDef)))
            grammar.addRule(gram.Rule(tokens.identifier, list(tokens.ruleDef)))

            buffer = buffer[end:]
            match = next(StartSymbol.scanString(buffer), None)
    return grammar

if __name__ == '__main__':
    fileStream = open(sys.argv[1])
    grammar = getGrammarObject(fileStream)
    print grammar
