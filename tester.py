#from lisp_utils import LispParser
from pddl_utils import PDDLParser as Parser
from pddl_utils import PDDLNode as Node
from compare import LispDiff
from utils import *

#from timeit import timeit
import time
import os

'''
This file runs tests on the PDDL parser.
'''

def profile_tree(fname):
    '''Run the PDDL parser on the given file.
    Extract and show meaningful information.'''
    
    contents = get_contents(fname)
    parser = Parser()
    tree = parser.get_tree(contents)
    
    print "==> tree-type:",
    print "'%s'" % tree.get_type()
    
    print "==> domain: '%s'" %  tree.get_domain()
    
    if tree.is_problem():
        print "==> problem: '%s'" % tree.get_problem()
    
        print "==> objects:"
        print tree.get_objects()
        
        print "==> init state:"
        print tree.get_init_state()
        
        print "==> goal:"
        print tree.get_goal()
        
    else:
        if tree.seek([":requirements"]):
            print "==> requirements:"
            print tree.seek([":requirements"])
            
        if tree.seek([":types"]):
            print "==> types:"
            print tree.seek([":types"])
        
        print "==> predicates:"
        print tree.get_predicates()
        
        print "==> actions:"
        i = 0
        
        for a in tree.get_actions():
            i += 1
            print "==> action: '%s'" % a.get_action_name()
            #a.print_tree()
            
            print "==> parameters: "
            print a.get_parameters()
            
            print "==> preconditions: "
            print a.get_preconditions()
            
            print "==> effects"
            print a.get_effects()
            
        if i == 0:
            print "[ no actions ]"
    
    #tree.print_tree()
    
def test_lisp_utils(fname):
    p = Parser()
    d = {}
    
    contents = get_contents(fname)
    
    tokens = p.get_tokens(contents)
    nl = p.nest_tokens(tokens)
    
    #print nl
    
    #d = p.get_pseudo_json(nl)
    #print d
    #
    #print_nested_dict(d)#["types"]
    
    tree = p.get_tree(contents)
    #tree.print_tree()
    d = p.tree_to_dict(tree)
    print_nested_dict(d)
    #print d
    
    return d

if __name__ == "__main__":
    ###########################################################
    #    Specify constants here:                              #
    
    f_problem = "samples/gripper-problem.pddl"
    #f_domain = "samples/logistics-adl-domain.pddl"
    f_domain = "samples/gripper-domain.pddl"
    
    f_other = "samples/storage-nested-typing-domain.pddl"
    
    #profile_tree(f_other)
    
    #test_lisp_utils(f_problem)
    d = test_lisp_utils(f_other)
    #print_nested_dict(d)
