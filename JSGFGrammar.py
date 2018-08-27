# -*- coding: utf-8 -*-
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
# @summary: This file lays out the class structure for a JSGF Grammar
# @since: 2014/06/02

"""
This file lays out the class structure for a JSGF Grammar. 

.. module:: JSGFGrammar 

.. moduleauthor:: Pastèque Ho <timothyakho@gmail.com>
"""


class JSGFExpression():
    pass

class Disjunction(JSGFExpression):
    """
    Disjunction class stores disjuncts in a list
    """
    
    def __init__(self, disjuncts):
        self.disjuncts = disjuncts

    def __str__(self):
        return '( ' + ' | '.join(map(str,self.disjuncts)) + ' )'

    def __repr__(self):
        return str(self)

    def __getitem__(self):
        return self.disjuncts

class Optional(JSGFExpression):
    """
    Optional class stores either a JSGFExpression, list, or string 
    as its optional element
    """

    def __init__(self, option):
        self.option = option

    def __str__(self):
        return ('[ ' + str(self.option) + ' ]')

    def __repr__(self):
        return str(self)

    def __getitem__(self):
        return self.option

class NonTerminal(JSGFExpression):
    """
    NonTerminal class simply stores the label of the nonterminal
    """

    def __init__(self, ntName):
        self.name = ntName

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __getitem__(self):
        return self.name


class Rule():
    """
    Rule class, represents a JSGF rule, with a nonterminal name representing the
    left hand side, and a list of possible expansions representing the right
    hand side. 
    """

    def __init__(self):
        """
        constructor with no args
        """
        self.lhs = ''
        self.rhs = []

    def __init__(self, lhs):
        """
        constructor with nonterminal name
        """
        pass

    def __init__(self, lhs, rhs):
        """
        constructor with full rule definition
        """
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return (str(self.lhs) + ' -> ' + str(self.rhs))

    def __repr__(self):
        return str(self)

        
class Grammar(): 
    """
    Grammar class which contains a list for public rules and a list
    for all rules. 
    """

    def __init__(self): 
        self.rules = []
        self.publicRules = []

    def addRule(self, rule):
        """
        adds a rule to the list of rules
        """
        self.rules.append(rule)

    def addPublicRule(self, rule):
        """
        adds a rule to the list of public rules
        """
        self.publicRules.append(rule)

    def getRHS(self, nt):
        """
        returns rule definition
        
        :param nt: Non-Terminal (variable) whose definition to get
        """
        for rule in self.rules:
            #print 'checking', nt.name, 'and', rule.lhs, type(nt.name), rule.lhs.name
            if rule.lhs.name == nt.name:
                return rule.rhs
        raise ValueError("Rule not defined for " + str(nt))

    def __getitem__(self, nt):
        #rhsides = [] to do for multiple rhsides
        for rule in self.rules:
            if rule.lhs == nt:
                return rule.rhs
            else:
                raise ValueError('Rule not defined for ' + str(nt))

    def __str__(self):
        return 'All Rules:' + str(self.rules) + '\n' + 'Public Rules:' + str(self.publicRules)

if __name__ == "__main__":
    jgDisj = Disjunction(['hello', 'world'])
    jgOpt = Optional(jgDisj)
    jgRule = Rule("<greeting>", jgOpt)

    print(jgRule)
