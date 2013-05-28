################################
#    Written by Daniel Kats    #
#    May 14, 2013              #
################################

import re
from utils import get_contents
import time

class Node(object):
	'''A node in the DOM-like LispTree.
	Tree is backwards-linked as well as forward-linked.'''
	
	''' The name for a node which represents the outside expression of something like ((lambda : 2 * 2)) '''
	EVAL_NAME = "eval"
	
	ROOT_NAME = "root-elem"
	
	@staticmethod
	def hash_node(fname):
		'''Creates a unique hash for each node which could be used in a tree.
		Allows for quick lookups.
		The time is used as a salt to 'guarantee' uniqueness.
		This hash is easily broken by a determined attacker, but will work if no one tries to break it on purpose.'''
		
		h = hash(fname + str(time.time()))
		return h
	
	def __init__(self, fname, fn=False):
		'''Create a new node.
		fn states whether this is a function or not - used to differentiate between (sum) and sum.'''
		
		self.name = fname
		self.parent = None
		self.children = []
		self.fn = fn
		self.hash = Node.hash_node(fname)
		
		# keep in memory whether this is the root
		self.root = (fname == self.ROOT_NAME)
			
		
	def is_root(self):
		'''Return True iff the current node is the root of the tree.'''
		
		return self.root
		
	def add_child(self, node, index=None):
		'''Add the given node (or subtree) as a child of the current tree (node).
		If index is unspecified, put it at the *END* of the child list (i.e. append).
		If index is specified, put it *after* the given index.'''
		
		node.parent = self
		
		if index is None:
			self.children.append(node)
		else:
			self.children.insert(index + 1, node)
			
	def index_of(self, subtree):
		'''Return the index of the given subtree.
		Return False if not found'''
		
		hashes = [c.hash for c in self.children]
		if subtree.hash in hashes:
			return hashes.index(subtree.hash)
		else:
			return False
		
	def merge_tree(self, tree):
		'''Slightly different from add_child because this is a fully-formed tree.
		Procedure is to remove the root node, then add everything'''
		
		if tree.is_root():
			for child in tree.children:
				self.add_child(child)
		else:
			self.add_child(tree)
			
	def seek_all(self, path):
		'''Return subtrees list if found, [] otherwise.'''
		
		if len(path) == 0:
			return [self]
		
		stop = path[0]
		results = []
		
		if isinstance(stop, tuple):
			stop, i = stop
			j = 0
			for child in self.children:
				if child.name == stop and  i == j:
					results.extend(child.seek_all(path[1:]))
					return results
				elif child.name == stop:
					j += 1
		else:
			for child in self.children:
				if child.name == stop:
					results.extend(child.seek_all(path[1:]))
						
		return results
		
	def seek(self, path):
		'''Return subtree if found, False otherwise.
		Return first match.
		The path *should not* include the root element.
		Path should look like this:
			["<name-1>", "<name-2>", ("<name-3", index), "<name-4>" ... ]
		indexing starts at 0. There is *NO* support for negative indexing.
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
			
	def print_tree(self, indent=0):
		'''Print ASCII horizontal representation of the tree.
		Functions will be prefaced and appended with '*' ''' 
		
		#print ("|---" * indent) + ('*' if self.fn else "") + self.name + ('*' if self.fn else "")
		print ("|---" * indent) + self.name
	
		for child in self.children:
			child.print_tree(indent + 1)
	
	def _nested_token_list(self):
		if self.is_root():
			return [child._nested_token_list() for child in self.children]
		elif not self.fn:
			return self.name
		else:
			l = ["("]
			if self.name != Node.EVAL_NAME:
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
			return "\n".join([Node.to_lisp_2(e, indent) for e in ntl])
		elif not any(type_list):
			return "%s(%s)" % (spacing, " ".join(ntl[1:-1]))
		else:
			expr = spacing + "(\n"
			for sublist in ntl[1:-1]:
				expr += Node.to_lisp_2(sublist, indent + 1) + "\n"
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
			if self.name != Node.EVAL_NAME:
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
				return "(%s)" % ("" if self.name == Node.EVAL_NAME else self.name)
			
			# check if it's a one-liner
			elif all([not child.fn for child in self.children]):
				return "(%s %s)" % (self.name, " ".join([child.to_lisp() for child in self.children]))
			else:
				# don't need to indent, will be indented by parent
				expr = "("
				expr += "" if self.name == Node.EVAL_NAME else self.name
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
		
	@staticmethod
	def _remove_comments(expr):
		'''Remove emacs-style comments (in the form ;[;] comments go here).
		Will not work if newlines are removed before this method is called.'''
		
		expr = re.sub(";+(.*?)$", "", expr)
		expr = re.sub(";+(.*?)(\r)?\n", "", expr)
		return expr

	@staticmethod
	def get_tokens(expr):
		'''Return a list of lisp tokens. Tokens are literals, as well as brackets, and functions/operators.'''

		return LispParser._remove_comments(expr).replace("(", " ( ").replace(")", " ) ").split()
	
	@staticmethod
	def get_tree(expr):
		'''Return a DOM-like tree structure.'''
		
		tokens = LispParser.get_tokens(expr)
		root = Node(Node.ROOT_NAME, False)
		
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
				return Node(Node.EVAL_NAME, True)
				#return None # a null-child
			
			if tokens[0] == "(":
				# a function call on the stuff inside the next expression
				root = Node(Node.EVAL_NAME, True)
			else:
				root = Node(tokens.pop(0), True)
		
			while tokens[0] != ")":
				subtree = LispParser._make_lisp_tree_helper(tokens)
				if subtree is not None:
					root.add_child(subtree)
		
			tokens.pop(0) # remove closing paren
			return root
		elif token == ")":
			raise SyntaxError("Unexpected closing paren")
		else:
			return Node(token, False)
		