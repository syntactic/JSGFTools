# -*- coding: utf-8 -*-
#/usr/bin/python

# @copyright: MIT License
#   Copyright (c) 2018 syntactic (Pastèque Ho)
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.
# @summary: This file generates sentences from a PCFG in JSGF. Run it by entering 
#   in the command line: python ProbabilisticGenerator.py <grammarFile> <numStrings>
#   where <grammarFile> is the path of the JSGF file, and <numString> is the number
#   of strings you want to generate
# @since: 2014/06/02

"""
This file probabilistically generates strings from a JSGF grammar. It takes advantage \
        of weights assigned to alternatives (separated by pipes) by choosing to \
        expand higher weighted alternatives with greater probability. For sets of \
        alternatives without weights, each alternative is equally likely to be \
        expanded. For optional groups, the elements in the group have a 50% chance \
        of being expanded. 

It requires two arguments: the path to the JSGF\
        Grammar file, and the number of strings to generate. You can run this on the \
        included grammar Ideas.gram:\


        ``python ProbabilisticGenerator.py Ideas.gram 20``

This will generate 20 sentences based on the public rule(s) in Ideas.gram, using the \
weights if they are provided.
"""

import sys, itertools, random, bisect, argparse
import JSGFParser as parser
import JSGFGrammar as gram


def weightedChoice(listOfTuples):
    """
    Chooses an element of a list based on its weight

    :param listOfTuples: a list of (element, weight) tuples, where the element can be a JSGF expression object, string, or list,\
            and the weight is a float
    :returns: the first element of a chosen tuple
    """
    def accum(listOfWeights): # support function for creating ranges for weights
        for i in range(len(listOfWeights)):
            if i > 0:
                listOfWeights[i] += listOfWeights[i-1]
        return listOfWeights
    choices, weights = zip(*listOfTuples)
    cumdist = accum(list(weights))
    x = random.random() * cumdist[-1]
    return choices[bisect.bisect(cumdist, x)]

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
            #print crossProduct[0], crossProduct[1]
            currentProduct.append((crossProduct[0].strip() + ' ' + crossProduct[1].strip()).strip())
        totalCrossProduct = currentProduct
    return totalCrossProduct

def processSequence(seq):
    """
    Combines adjacent elements in a sequence.
    """
    componentSets = []
    for component in seq:
        expandedComponent = processRHS(component).strip()
        if len(expandedComponent) > 0:
            componentSets.append(expandedComponent)
    return ' '.join(componentSets)


def processNonTerminal(nt):
    """
    Finds the rule expansion for a nonterminal and returns its expansion.
    """
    return processRHS(grammar.getRHS(nt))

def processDisjunction(disj):
    """
    Chooses either a random disjunct (for alternatives without weights) or
    a disjunct based on defined weights. 
    """
    if type(disj.disjuncts[0]) is tuple:
        return processRHS(weightedChoice(disj.disjuncts))
    else:
        return processRHS(random.choice(disj.disjuncts))

def processOptional(opt):
    """
    Processes the optional element 50% of the time, skips it the other 50% of the time
    """
    rand = random.random()
    if rand <= 0.5:
        return ''
    else:
        return processRHS(opt.option)

def processRHS(rhs):
    if type(rhs) is list:
        return processSequence(rhs)
    elif isinstance(rhs, gram.Disjunction):
        return processDisjunction(rhs)
    elif isinstance(rhs, gram.Optional):
        return processOptional(rhs)
    elif isinstance(rhs, gram.NonTerminal):
        return processNonTerminal(rhs)
    elif type(rhs) is str:
        return rhs


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('grammarFile')
    argParser.add_argument('iterations', type=int, nargs=1, help='number of strings to generate')
    args = argParser.parse_args()
    fileStream = open(args.grammarFile)
    numIterations = args.iterations[0]
    grammar = parser.getGrammarObject(fileStream)
    if len(grammar.publicRules) != 1:
        #x = raw_input('Found more than one public rule. Generate a random string between them?\n')
        #if x == 'y':
        ### This next chunk has been de-indented
        disjuncts = []
        for rule in grammar.publicRules:
            rhs = rule.rhs
            disjuncts.append(rhs)
        newStartSymbol = gram.Disjunction(disjuncts)
        for i in range(numIterations):
            print processRHS(newStartSymbol)
        ###
        #else:
            #sys.exit('Bye')
    else:
        startSymbol = grammar.publicRules[0]
        for i in range(numIterations):
            expansions = processRHS(startSymbol.rhs)
            print expansions



