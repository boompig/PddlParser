#from lisp_utils import LispParser
from pddl_utils import PDDLParser as Parser
from compare import LispDiff
from utils import get_contents

'''
This file runs tests on the PDDL parser.
'''

def show_problem(fname):
    '''Run the PDDL parser on the problem file. Show the output.'''
    
    contents = get_contents(fname)
    parser = Parser()
    tree = parser.get_tree(contents)
    tree.finalize()
    
    print "==> whole tree:"
    tree.print_tree()
    
    print "==> problem:"
    p_tree = tree.get_problem()
    p_tree.print_tree()
    
    print "==> domain:"
    d_tree = tree.get_domain()
    d_tree.print_tree()
    
    print "==> init state:"
    i_tree = tree.get_init_state()
    i_tree.print_tree()
    
    print "==> goal:"
    g_tree = tree.get_goal()
    g_tree.print_tree()
    
def show_domain(fname):
    '''Run the PDDL parser on the domain file. Show the output.'''
    
    contents = get_contents(fname)
    parser = Parser()
    tree = parser.get_tree(contents)
    #tree.finalize()
    
    tree.print_tree()

###########################################################
#    Specify constants here:                              #

f_problem = "samples/gripper-problem.pddl"
f_domain = "samples/gripper-domain.pddl"
#show_problem(f_problem)
show_domain(f_domain)