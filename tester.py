#from lisp_utils import LispParser
from pddl_utils import PDDLParser as Parser
from compare import LispDiff
from utils import get_contents

#from timeit import timeit
import time

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

def benchmark_seek_all():
    tree = Parser().get_tree(get_contents('samples/gripper-domain.pddl'))
    
    print "==> generator:"
    start = time.time()
    #for i in xrange(1):
    tree.seek_all([':action'])
    print (time.time() - start) #* 1000
    
    print "==> list"
    start = time.time()
    #for i in xrange(1):
    tree.seek_all_list([':action'])
    print (time.time() - start) #* 1000
   
   

###########################################################
#    Specify constants here:                              #

f_problem = "samples/gripper-problem.pddl"
f_domain = "samples/gripper-domain.pddl"

profile_tree(f_problem)
#show_domain(f_domain)
#benchmark_seek_all()