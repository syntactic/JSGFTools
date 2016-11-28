"""
This file deterministically generates strings from a JSGF Grammar, whether there are \
        weights defined in rules or not. It requires one argument: the path to the JSGF\
        Grammar file. You can run this on the included grammar IdeasNonRecursive.gram:\


        ``python DeterministicGenerator.py IdeasNonRecursive.gram``

This will generate all strings defined by the public rules of IdeasNonRecursive.gram.\
        It is important that the grammar used by the generator is not recursive (rules \
        should not directly or indirectly reference themselves), so that the generator\
        terminates. Otherwise, you may get a maximum recursion depth exceeded error or \
        a segmentation fault. 
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
# @summary: This file generates all strings described by a non-recursive JSGF grammar.
#   Run it by entering into the command line: python DeterministicGenerator.py <grammarFile>
#   where <grammarFile> is the path to the JSGF grammar.
# @since: 2014/06/02

import sys, itertools
import JSGFParser as parser
import JSGFGrammar as gram


def combineSets(listOfSets):
    """
    Combines sets of strings by taking the cross product of the sets and \
            concatenating the elements in the resulting tuples

    :param listOfSets: 2-D list of strings
    :returns: a list of strings
    """
    totalCrossProduct = ['']
    for i in range(len(listOfSets)):
        currentProduct = []
        for crossProduct in itertools.product(totalCrossProduct, listOfSets[i]):
            currentProduct.append((crossProduct[0].strip() + ' ' + crossProduct[1].strip()).strip())
        totalCrossProduct = currentProduct
    return totalCrossProduct

def processSequence(seq):
    """
    Combines adjacent elements in a sequence
    """
    componentSets = []
    for component in seq:
        componentSets.append(processRHS(component))
    return combineSets(componentSets)


def processNonTerminal(nt):
    """
    Finds the rule expansion for a nonterminal and returns its expansion.
    """
    return processRHS(grammar.getRHS(nt))

def processDisjunction(disj):
    """
    Returns the string representations of a set of alternatives

    :returns: list of strings, where each string is each alternative
    """
    disjunctExpansions = []
    if type(disj.disjuncts[0]) is tuple:
        disjuncts = map(lambda x : x[0], disj.disjuncts)
    else:
        disjuncts = disj.disjuncts
    for disjunct in disjuncts:
        disjunctExpansions.extend(processRHS(disjunct))
    return disjunctExpansions

def processOptional(opt):
    """
    Returns the string representations of an optional grouping

    :type opt: JSGFOptional
    :returns: list of strings, including an empty string
    """
    optional = ['']
    optional.extend(processRHS(opt.option))
    return optional

def processRHS(rhs):
    """
    Depending on the type of the argument, calls the corresponding
    function to deal with that type.

    :param rhs: portion of JSGF rule
    :type rhs: either a JSGF Expression, list, or string
    :returns: list of strings
    """
    if type(rhs) is list:
        return processSequence(rhs)
    elif isinstance(rhs, gram.Disjunction):
        return processDisjunction(rhs)
    elif isinstance(rhs, gram.Optional):
        return processOptional(rhs)
    elif isinstance(rhs, gram.NonTerminal):
        return processNonTerminal(rhs)
    elif type(rhs) is str:
        return [rhs]


if __name__ == '__main__':
    fileStream = open(sys.argv[1])
    grammar = parser.getGrammarObject(fileStream)
    for rule in grammar.publicRules:
        expansions = processRHS(rule.rhs)
        for expansion in expansions:
            print expansion



