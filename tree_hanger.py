################################
#    Written by Daniel Kats    #
#    May 14, 2013              #
################################

from lisp_utils import LispParser
from utils import get_contents
from sconvert import partition_translator_output
import sys
import os

class TreeHanger(object):
	''' This class intelligently adds content to the domain and problem files, which are fed into the HTN Planner.
	The content to be added comes from Jorge's translator.
	
	The mechanism:
		- seperate constituent parts of Jorge's translator output into 4 files using Shirin's script
		- convert problem and domain files into trees
		- convert 4 files into trees (call these ornaments)
		- copy and hang the 4 ornaments onto the problem and domain trees
		
	Unfortunately, there may be issues with larger files, because:
		- the entire problem / domain file is loaded into memory
		- then this file is turned into a DOM tree (still in RAM)
	
	I couldn't think of a good name for this class, put I keep thinking of hanging ornaments on Christmas trees.
	'''
	
	def __init__(self, f_domain, f_problem, f_translator_out, problem_number=1):
		'''Create a new tree hanger for the given set of files.'''
		
		self.f_domain = f_domain
		self.f_problem = f_problem
		self.p_num = problem_number
		
		# seperate the translator output into 4 files
		self.tr_outfiles = partition_translator_output(f_translator_out)
		
	def modify_problem(self):
		'''Modify the problem file. Wrapper for the static method.'''
		
		problem_out = "Problem%d.lisp" % self.p_num
		TreeHanger._modify_problem(self.f_problem, problem_out, self.tr_outfiles)
		return problem_out
		
	def modify_domain(self):
		'''Modify the domain file. Wrapper for the static method.'''
		
		domain_out = "Domain%d.lisp" % self.p_num
		TreeHanger._modify_domain(self.f_domain, domain_out, self.tr_outfiles)
		return domain_out

	@staticmethod
	def add_init_state_prefs(problem_tree, pref_tree):
		'''Modify the problem tree by nesting the preference expression under it.'''
		
		path = ["defproblem", ("eval", 0)]
		subtree = problem_tree.seek(path)
		if subtree:
			subtree.merge_tree(pref_tree)
		
	@staticmethod
	def add_metric_functions(problem_tree, axiom_tree):
		'''Modify the problem tree by nesting the metric functions under it.'''
		
		function_names = ["metric", "pessimistic-metric", "optimistic-metric"]
		metric_tree = problem_tree.seek(["defun", "bestMetric"]).parent
		
		i = problem_tree.index_of(metric_tree)
		
		for f_i, function in enumerate(function_names):
			path = ["defun", function]
			subtree = axiom_tree.seek(path)
			if subtree:
				subtree = subtree.parent
				problem_tree.add_child(subtree, i + f_i) # not merge, since these do not have root node
			else:
				#error!
				print "==> failed at " + function
				
	@staticmethod
	def _modify_problem(f_problem, f_out, tr_outfiles):
		'''Modify the problem by writing it to a new file.
		Return the name of the new problem file.'''
		
		f_init_states = tr_outfiles["init_states"]
		f_axioms = tr_outfiles["axioms"]
		
		# the problem
		problem = get_contents(f_problem)
		problem_tree = LispParser.get_tree(problem)
		
		# the preferences
		init_states = get_contents(f_init_states)
		init_states_tree = LispParser.get_tree(init_states)
		TreeHanger.add_init_state_prefs(problem_tree, init_states_tree)
		
		# the axioms
		axioms = get_contents(f_axioms)
		axiom_tree = LispParser.get_tree(axioms)
		TreeHanger.add_metric_functions(problem_tree, axiom_tree)
		
		# write to the new problem file
		fp = open(f_out, "w")
		fp.write(problem_tree.to_lisp())
		fp.close()
		
		return f_out
		
	@staticmethod
	def add_add_del_effects(domain_tree, add_effect_tree, del_effect_tree):
		'''Modify the domain tree by merging in the del-effects tree and add-effects tree.'''
		
		path = ["defdomain", "eval", ":operator"]
		subtrees = domain_tree.seek_all(path)
		
		#del_effect_tree.print_tree()
	
		for i, subtree in enumerate(subtrees):
			subtree.seek([("eval", 1)]).merge_tree(del_effect_tree)
			subtree.seek([("eval", 2)]).merge_tree(add_effect_tree)
	
	@staticmethod
	def add_domain_prefs(domain_tree, pref_tree):
		'''Pin the domain preferences onto the domain tree by modifying the tree.'''
		
		domain_subtree = domain_tree.seek(["defdomain", "eval"])
		
		# syntax here is a bit weird... basically selecting anything with (:-
		for subtree in pref_tree.seek_all([":-"]):
			# not merge_tree because no root elem
			domain_subtree.add_child(subtree)
	
	@staticmethod
	def _modify_domain(f_domain, f_out, tr_outfiles):
		'''Create a new domain file. Return the name of the new file.'''
		
		f_add_effects= tr_outfiles["add_effects"]
		f_del_effects= tr_outfiles["del_effects"]
		f_axioms = tr_outfiles["axioms"]
		
		# the domain
		domain = get_contents(f_domain)
		domain_tree = LispParser.get_tree(domain)
		
		# add and del effects
		add_effects_tree = LispParser.get_tree(get_contents(f_add_effects))
		del_effects_tree = LispParser.get_tree(get_contents(f_del_effects))
		TreeHanger.add_add_del_effects(domain_tree, add_effects_tree, del_effects_tree)
		
		# domain prefs
		axioms = get_contents(f_axioms)
		axiom_tree = LispParser.get_tree(axioms)
		TreeHanger.add_domain_prefs(domain_tree, axiom_tree)
		
		# write to the new domain file
		fp = open(f_out, "w")
		fp.write(domain_tree.to_lisp())
		fp.close()
		
		return f_out

if __name__ == "__main__":
	usage = "usage: python tree_hanger.py domain_file problem_file transator_output_file [problem_number]"
	
	if not 4 <= len(sys.argv) <= 5:
		if len(sys.argv) < 4:
			print >>sys.stderr, "Too few arguments"
		else:
			print >>sys.stderr, "Too many arguments"
		print >>sys.stderr, usage
		sys.exit(1)
		
	# check that files all exist
	for f in sys.argv[1:4]:
		if not os.path.exists(f):
			print >>sys.stderr, "Given file does not exist: '%s'" % f
			sys.exit(1)
			
	f_domain, f_problem, f_translator_output = sys.argv[1:4]
	
	if len(sys.argv) == 4:
		problem_number = int(sys.argv[-1])
	else:
		problem_number = 1
	
	# verbose stuff that isn't strictly-speaking necessary
	print "==> Input:"
	print "Domain File -> %s" % f_domain
	print "Problem File -> %s" % f_problem
	print "Translator Output File -> %s" % f_translator_output
	
	hanger = TreeHanger(f_domain, f_problem, f_translator_output, problem_number)
	
	# perform operations on domain file
	domain_out = hanger.modify_domain()
	print "==> Wrote new domain file to %s" % domain_out
	
	# perform operations on problem file
	problem_out = hanger.modify_problem()
	print "==> Wrote new problem file to %s" % problem_out
	