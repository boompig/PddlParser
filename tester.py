#from lisp_utils import LispParser
from pddl_utils import PDDLParser as Parser
from pddl_utils import PDDLNode as Node
from compare import LispDiff
from utils import get_contents

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
    t = tree.get_type()
    print "'%s'" % t
    
    print "==> domain: '%s'" %  tree.get_domain()
    
    if t == "problem":
        print "==> problem: '%s'" % tree.get_problem()
    
        print "==> objects:"
        print tree.get_objects()
        
        print "==> init state:"
        print tree.get_init_state()
        
        print "==> goal:"
        print tree.get_goal()
        
    else:
        print "==> predicates:"
        print tree.get_predicates()
        
        print "==> actions:"
        for a in tree.get_actions():
            print "==> action: '%s'" % a.get_action_name()
            #a.print_tree()
            
            print "==> parameters: "
            print a.get_parameters()
            
            print "==> preconditions: "
            print a.get_preconditions()
            
            print "==> effects"
            print a.get_effects()
    
    #tree.print_tree()
    
def test_lisp_utils():
    p = Parser()
    
    n1 = p.get_tree("(sum 3 5 6)")
    print n1.is_simple_expr()
    
    n2 = p.get_tree("(sum 3 (sum 5 6))")
    print n2.is_simple_expr()

###########################################################
#    Specify constants here:                              #

f_problem = "samples/gripper-problem.pddl"
f_domain = "samples/gripper-domain.pddl"
profile_tree(f_domain)
profile_tree(f_problem)
#test_lisp_utils()
