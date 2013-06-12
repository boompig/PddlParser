################################
#    Written by Daniel Kats    #
#    May 14, 2013              #
################################

import re
from utils import get_contents
from tree import Node

class LispNode(Node):
	'''A node in the DOM-like LispTree.
	Tree is backwards-linked as well as forward-linked.'''
	
	''' The name for a node which represents the outside expression of something like ((lambda : 2 * 2)) '''
	EVAL_NAME = "eval"
	
	'''The special identifier given to the fictitious root node. Needed when there is more than one lisp expression.
	#TODO move this into the parser'''
	ROOT_NAME = "root-elem"
	
	def __init__(self, name, fn=False):
		'''Create a new node.
		fn states whether this is a function or not - used to differentiate between the following expressions:
			(sum)	-	this is a function call with no arguments (fn=True)
			sum		-	this is a variable name or literal (fn=False)
		'''
		
		Node.__init__(self, name)
		self.fn = fn
	
	def is_simple_expr(self):
		'''Return True iff this is a simple expression.
		Simple expression has no expression-children
		(sum 3 2 4) is simple
		(sum 3 (sum 2 4)) is not simple.'''
		
		return all([len(child.children) == 0 for child in self.children])
			
	def seek_all(self, path, delete=False):
		'''Return *a generator* over the subtrees found.
		The path *should not* include the root element.
		Path should look like this:
			["<name-1>", "<name-2>", ("<name-3", index), "<name-4>" ... ]
		Indexing starts at 0. There is *NO* support for negative indexing.'''
		
		assert isinstance(path, list) # path *must* be a list
		
		if len(path) == 0:
			#return [self]
			yield self
			return
		
		stop = path[0]
		#results = []
		
		if isinstance(stop, tuple):
			stop, stop_i = stop
			name_counter = i = 0
			
			while i < len(self.children):
				if child.name == stop and  stop_i == name_counter:
					#results.extend(child.seek_all(path[1:]))
					#return results
					for item in child.seek_all(path[1:], delete):
						yield item
					if delete:
						self.children.pop(i)
					else:
						i += 1
				else:
					i += 1
					if child.name == stop:
						name_counter += 1
		else:
			i = 0
			while i < len(self.children):
				child = self.children[i]
				
				if child.name == stop:
					#results.extend(child.seek_all(path[1:]))
					for item in child.seek_all(path[1:], delete):
						yield item
					if delete:
						self.children.pop(i)
					else:
						i += 1
				else:
					i += 1
							
						
		#return results
		
	def seek(self, path):
		'''Return subtree if found, False otherwise.
		Return first match.
		The path *should not* include the root element.
		Path should look like this:
			["<name-1>", "<name-2>", ("<name-3", index), "<name-4>" ... ]
		Indexing starts at 0. There is *NO* support for negative indexing.
		'''
		
		if len(path) == 0:
			return self
		
		stop = path[0]
		if isinstance(stop, tuple):
			stop, i = stop
			assert i >= 0
			j = 0
			
			for child in l:
				if child.name == stop and  i == j:
					return child.seek(path[1:])
				elif child.name == stop:
					j += 1
			return False
		else:
			for child in self.children:
				if child.name == stop:
					result = child.seek(path[1:])
					if result:
						return result
			# if nothing found
			return False
	
	def _nested_token_list(self):
		if self.is_root():
			return [child._nested_token_list() for child in self.children]
		elif not self.fn:
			return self.name
		else:
			l = ["("]
			if self.name != LispNode.EVAL_NAME:
				l.append(self.name)
			for child in self.children:
				l.append(child._nested_token_list())
			
			return l + [")"]
		
	@staticmethod
	def to_lisp_2(ntl, indent=0):
		'''Implementation of to_lisp via _nested_token_list.
		ntl is nested token list'''
		
		# simple rules
		# if it's just a list of stuff (root case)
		# 	just convert the sub-lists to lisp, and space them
		# if it's a simple expression like (city toronto)
		#	first and last are parens, join the rest with spaces
		# if it's an eval expression like ((city toronto))
		#	treat it complexly
		# if it's a complex expression like (sum (sum 2 3) (product 5 8))
		#	(
		#		sum
		#		(sum 2 3)
		#		(product 5 8)
		#	)
		
		#	seperate line (
		#	seperate line sum <-- indent + 1
		#	seperate line (sum 2 3) <-- indent + 1
		#	seperate line (product 5 8) <-- indent + 1
		# 	seperate line )
		
		spacing  = "\t" * indent
		
		if not isinstance(ntl, list):
			return spacing + ntl # <-- the base case
		
		type_list = [isinstance(e, list) for e in ntl]
		
		if all(type_list):
			return "\n".join([LispNode.to_lisp_2(e, indent) for e in ntl])
		elif not any(type_list):
			return "%s(%s)" % (spacing, " ".join(ntl[1:-1]))
		else:
			expr = spacing + "(\n"
			for sublist in ntl[1:-1]:
				expr += LispNode.to_lisp_2(sublist, indent + 1) + "\n"
			expr += spacing + ")"
			return expr
	
	def _tokenize(self):
		'''Tokenize the node and subtree.
		Return list of tokens.'''
		
		l = []
		
		if self.is_root():
			for child in self.children:
				l.extend(child._tokenize())
		elif not self.fn:
			l.append(self.name)
		else:
			l.append("(")
			if self.name != LispNode.EVAL_NAME:
				l.append(self.name)
			for child in self.children:
				l.extend(child._tokenize())
			l.append(")")
			
		return l
			
	def to_lisp(self, indent=0):
		'''Convert this tree to lisp expressions.
		Added some hacks for literals (' character), so code is a bit messy'''
		
		if self.is_root():
			return "\n".join([child.to_lisp() for child in self.children])
		elif not self.fn:
			return self.name
		else:
			if len(self.children) == 0:
				return "(%s)" % ("" if self.name == LispNode.EVAL_NAME else self.name)
			
			# check if it's a one-liner
			elif all([not child.fn for child in self.children]):
				return "(%s %s)" % (self.name, " ".join([child.to_lisp() for child in self.children]))
			else:
				# don't need to indent, will be indented by parent
				expr = "("
				expr += "" if self.name == LispNode.EVAL_NAME else self.name
				expr += "\n"
				
				prev_expr = ""
				
				for child in self.children:
					child_expr = child.to_lisp(indent + 1)
					spacing = "" if prev_expr == "'" else "\t" * (indent + 1)
					expr += spacing + child_expr + ("" if child_expr == "'" else "\n")
					prev_expr = child_expr
				expr += "\t" * (indent) + ")"
				return expr

class LispParser(object):
	'''Parser for the lisp language.
	Allows extracting tokens, and creating a dom-like tree.
	Also allows cleaning out junk and comments.'''
	
	KEYWORDS = set(["domain"])
	
	@staticmethod
	def tree_to_dict(tree):
		'''Translate the tree into a dict. Return the dictionary.
		If the tree is just a single element, return a string.'''
		
		if len(tree.children) == 0:
			# single name is a string
			return tree.name
		elif len(tree.children) == 1:
			# single child 
			return {tree.name : LispParser.tree_to_dict(tree.children[0])}
		elif tree.is_simple_expr():
			# simple expressions means the tree doesn't contain any intense whatever
			return {tree.name : [child.name for child in tree.children]}
		else:
			subdict = {}
			
			for child in tree.children:
				subdict.update(LispParser.tree_to_dict(child))
			return {tree.name : subdict}
		
	@staticmethod
	def _remove_comments(expr):
		'''Remove emacs-style comments: 
			;[;] <comment-word> ...
		Will not work if newlines are removed before this method is called, since there is no comment-ending character.'''
		
		expr = re.sub(";+(.*?)$", "", expr)
		expr = re.sub(";+(.*?)(\r)?\n", "", expr)
		return expr

	@staticmethod
	def get_tokens(expr):
		'''Return a list of lisp tokens. Tokens are literals, as well as brackets, and functions/operators.'''

		return LispParser._remove_comments(expr).replace("(", " ( ").replace(")", " ) ").split()
	
	@staticmethod
	def get_keywords_2(tokens, d=None):
		'''Now tokens is a nested list.
		d is the mutable dict you pass in. Optional to pass, will be created anyway'''
		
		if d is None: d = {}
		
		# we actually only care if it's a class or not
		if len(tokens) > 0:
			token = tokens[0]
			
			if token.startswith(":") or token in LispParser.KEYWORDS:
				d[token] = "keyword"
			
			# recurse on all sublists
			for sublist in filter(lambda(t) : isinstance(t, list), tokens[1:]):
				subdict = LispParser.get_keywords_2(sublist)
				d.update(sublist)
				
				# if the subdict contains elements, it means sublists contain keywords
				# which means this is a class
				# so let's add it to the list
				if len(subdict) > 0:
					d[token] = "class"
			
		return d
	
	@staticmethod
	def get_keywords(tokens):
		'''Given a list of tokens, return a generator.'''
		
		keywords = filter(lambda (t): t.startswith(":"), tokens)
		
		# tack onto this domain
		
		d = {}
		
		for k in keywords:
			c = keywords.count(k)
			if c > 1:
				
				d[k if k.endswith("s") else k + "s"] = "generator"
			else:
				d[k] = "list"
			
		return d
	
	def is_simple_expr(self, nl):
		'''nl is nested list.
		Return True iff nl is a flat list
		Flat lists correspond to simple expressions'''
		
		return not any([isinstance(item, list) for item in nl])
	
	def get_pseudo_json(self, tokens):
		'''tokens is token list'''
		
		# so we start with something like
		# [ sum 5 [ sum 4 6 ]]
		# { "sum" : [5, {"sum" : [4, 6]}}
		
		# when the first item is a list, that's not good
		# so we can create a name called eval
		
		assert isinstance(tokens, list) # literals should never be passed here
		
		if len(tokens) == 0:
			# the simple base-case
			return []
		elif isinstance(tokens[0], list):
			# throw a fake eval node in there ... 
			tokens.insert(0, "eval")
		
		if all([isinstance(sublist, list) for sublist in tokens[1:]]) and len(tokens) > 1:
			# then we create a sub-dictionary
			subdict = {}
			
			for sublist in tokens[1:]:
				sd = self.get_pseudo_json(sublist)
				print sd.viewkeys()
				subdict.update(sd)
				
			return {tokens[0] : subdict}
		elif len(tokens) == 2:
			# one child should not be placed in list
			return {tokens[0] : tokens[1]}
		else:
			# then we create a sub-list
			child_list = []
			
			for sublist in tokens[1:]:
				if not isinstance(sublist, list):
					child_list.append(sublist) # not a true sublist
				else:
					# a true sublist
					child_list.append(self.get_pseudo_json(sublist))
					
			if len(child_list) == 1:
				return {tokens[0] : child_list[0]}
			else:
				return {tokens[0] : child_list}
	
	@staticmethod
	def nest_tokens(tokens, depth = 0):
		'''Return a nested list of tokens, mimicking structure of underlying Lisp.
		tokens - a list of tokens obtained by calling get_tokens static method.
		depth - an internal parameter that is part of recursion, used for sanity checking.
		Throws SyntaxError on badly formed (i.e. non-Lisp) expressions.
		WARNING: deletes all tokens in given token list (uses it like a stack)'''
	
		l = []
		
		while len(tokens) > 0:
			token = tokens.pop(0)
			#print "[depth=%d] token = %s" % (depth, token)
			
			if token == "(":
				subexpr = LispParser.nest_tokens(tokens, depth + 1)
				l.append(subexpr)
			elif token == ")":
				if depth == 0:
					raise SyntaxError("there is an extra paren at the end of expr")
				return l
			else:
				l.append(token)
				
		if depth > 0:
			raise SyntaxError("missing matching closing paren at end of expr")
		elif len(l) == 1:
			# since any 'true' Lisp expression starts with '(' (including PDDL), algo will trigger recursion on first token
			# recursion returns a list, and this list will be appended to l, and will be the only element in l
			# so in the case of PDDL would normally return [[define ... ]], and want to instead return [define ... ]
			return l[0]
		else:
			# conversely if the structure is non-Lispy (expr-1 ...) (expr-2) with no top-level bracket, then above correction is unneeded
			# will return [[expr-1 ... ], [expr-2 ... ]] for above
			# also handles base-case of empty token list
			return l
	
	@staticmethod
	def get_tree(expr):
		'''Return a DOM-like tree structure.'''
		
		tokens = LispParser.get_tokens(expr)
		root = LispNode(LispNode.ROOT_NAME, False)
		
		while len(tokens) > 0:
			subtree = LispParser._make_lisp_tree_helper(tokens)
			if subtree is not None:
				root.add_child(subtree)
		
		return root
	
	@staticmethod
	def _make_lisp_tree_helper(tokens):	
		'''Helper to the make_lisp_tree function. This does most of the work.
		tokens - list of lisp tokens to make the tree out of.'''
		
		token = tokens.pop(0)
		if token == "(":
			# consider an empty expression an empty eval exression
			if tokens[0] == ")":
				tokens.pop(0)
				return LispNode(LispNode.EVAL_NAME, True)
				#return None # a null-child
			
			if tokens[0] == "(":
				# a function call on the stuff inside the next expression
				root = LispNode(LispNode.EVAL_NAME, True)
			else:
				root = LispNode(tokens.pop(0), True)
		
			while tokens[0] != ")":
				subtree = LispParser._make_lisp_tree_helper(tokens)
				if subtree is not None:
					root.add_child(subtree)
		
			tokens.pop(0) # remove closing paren
			return root
		elif token == ")":
			raise SyntaxError("Unexpected closing paren")
		else:
			return LispNode(token, False)
		
def _test_tree():
	'''Some very basic testing'''
	
	expr = "(sum 3 2)"
	p = LispParser()
	tree = p.get_tree(expr)
	tree.print_tree()
		
if __name__ == "__main__":
	from sys import argv
	# get command-line args
	
	if len(argv) < 2:
		print "Usage: [python] %s [ -t ] expr " % argv[0]
		exit(1)
	else:
		if "-t" in argv:
			argv.remove("-t")
		
		expr = argv[1]
		p = LispParser()
		tree = p.get_tree(expr)
		tree.print_tree()