"""
This file lays out the class structure for a JSGF Grammar. 

.. module:: JSGFGrammar 

.. moduleauthor:: Timothy Ho <timothyakho@gmail.com>
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
# @summary: This file lays out the class structure for a JSGF Grammar
# @since: 2014/06/02

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

    print jgRule
