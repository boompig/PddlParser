#from lisp_utils import LispParser
from pddl_utils import PDDLParser as Parser
from compare import LispDiff
from utils import get_contents

'''
This file runs tests on the PDDL parser.
'''

def run_engine(f_pddl):
    '''Run the PDDL parser. Show the output.'''
    
    contents = get_contents(f_pddl)
    parser = Parser()
    tree = parser.get_tree(contents)
    tree.finalize()
    
    #tree.print_tree()
    
    #p_tree = tree.get_problem()
    #p_tree.print_tree()
    
    #d_tree = tree.get_domain()
    #d_tree.print_tree()
    
    #i_tree = tree.get_init_state()
    #i_tree.print_tree()
    
    g_tree = tree.get_goal()
    g_tree.print_tree()

def error_check(f_domain_baseline, f_domain_gen, f_problem_baseline, f_problem_gen):
    '''Run an error check using provided baseline files'''
    
    diff_engine = LispDiff()

    print "==> comparing domain files..."
    if diff_engine.compare(f_domain_baseline, f_domain_gen):
        print "files are identical"
    else:
        print "ERROR: files are different"
    
    print "==> comparing problem files..."
    if diff_engine.compare(f_problem_baseline, f_problem_gen):
        print "files are identical"
    else:
        print "ERROR: files are different"

###########################################################
#    Specify constants here:                              #

f_pddl = "samples/sample-problem-1.pddl"
run_engine(f_pddl)