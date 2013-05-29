from lisp_utils import Node, LispParser

class PDDLNode(Node):
    '''A Node in a PDDL tree, which is has a Lisp-y syntax.'''
    
    ''' There are two types of PDDL files.'''
    PROBLEM = False
    DOMAIN = True
    
    ACTION_NAME = ":action"
    
    '''True iff C-style syntax is being converted to Lisp-style syntax by the parser.
    This affects all the getter methods for C-style keywords like :parameters
    '''
    C_SYNTAX_REPLACE_TREE = True
    
    def __init__(self, fname, fn=False):
        '''Create a new node.
        fn states whether this is a function or not - used to differentiate between (sum) and sum.'''
        
        # call to super
        Node.__init__(self, fname, fn)
        
        # lazy evaluation
        self.problem = None
        self.domain = None
        self.init_state = None
        self.goal = None
        self._type = None
        
    def __str__(self):
        '''String representation of PDDL Node.'''
        
        return self.to_lisp()
        #return self.to_light_str()
        
    def to_light_str(self):
        '''Return an 'easy-on the-eyes rep.'''
        
        if len(self.children) == 0:
            return "PDDL Node %s" % self.name
        else:        
            return "PDDL Node %s (%s)" % (self.name, self.children[0].name)
        
    def is_action_node(self):
        '''Return True iff this is an action node.'''
        
        return self.name == self.ACTION_NAME
        
    def get_action_name(self):
        '''Return the name of this action node. Return False if this is not an action node.'''
        
        if not self.is_action_node():
            return False
        
        assert len(self.children) > 0
        return self.children[0].name
    
    def seek_c_style(self, path):
        '''Seek for a C-style path. The first path[:-1] is DOM-style, but the last element is C-style.'''
        
        if len(path) > 1:
            subtree = self.seek(path[:-1])
            if subtree:
                return subtree.seek_c_style(path[-1])
            else:
                return subtree
        elif len(path) == 0:
            return self
        else:
            i = self.index_of(self.seek(path[0]))
            assert len(self.children) > i + 1 # need to be able to access element after path[0]
            subtree = self.children[i + 1]
            return subtree
        
    def _get_simple_expr_contents(self):
        '''Return a list of names of the contents of this expression. Used by getters for parameters, etc.
        Return False if this is not a simple expression.'''
        
        if not self.is_simple_expr():
            return False
        
        if self.C_SYNTAX_REPLACE_TREE:
            return [child.name for child in self.children]
        else:
            return [self.name] + [child.name for child in self.children]
    
    def get_parameters(self):
        '''Return a list of parameters of this action.
        Only relevant if this is an action node. Return False if this is not an action node.'''
        
        if not self.is_action_node():
            return False
        
        if self.C_SYNTAX_REPLACE_TREE:
            subtree = self.seek([":parameters"])
        else:
            subtree = self.seek_c_style([":parameters"])
            
        if subtree:
            return subtree._get_simple_expr_contents()
        else:
            return subtree
        
    def get_preconditions(self):
        '''Return the preconditions of this action.
        Only relevant if this is an action node. Return False if this is not an action node.'''
        
        if not self.is_action_node():
            return False
        
        if self.C_SYNTAX_REPLACE_TREE:
            subtree = self.seek([":precondition"])
        else:
            subtree = self.seek_c_style([":precondition"])
        
        return subtree
    
    def get_effects(self):
        '''Return the effects of this action.
        Only relevant if this is an action node. Return False if this is not an action node.'''
        
        if not self.is_action_node():
            return False
        
        if self.C_SYNTAX_REPLACE_TREE:
            subtree = self.seek([":effect"])
        else:
            subtree = self.seek_c_style([":effect"])
        
        return subtree
    
    def get_objects(self):
        '''Return a list of objects in this problem. Return False if this is a domain tree.'''
        
        if self.is_domain():
            return False
        
        return [child.name for child in self.seek([":objects"]).children]
        
    def get_predicates(self):
        '''Return the predicates subtree. Return False if this is a problem file.'''
        
        if self.is_problem():
            return False
        
        return self.seek([":predicates"])
        
    def get_actions(self):
        '''Return a generator over the action subtrees. Return False if this is a problem file.'''
        
        if self.is_problem():
            return False
        
        return self.seek_all([self.ACTION_NAME])
    
    def is_problem(self):
        '''Return True iff this tree represents a problem file.'''
        
        if self._type is None:
            self._classify()
            
        return self._type == self.PROBLEM
            
    def is_domain(self):
        '''Return True iff this tree represents a domain file.'''
        
        return not self.is_problem()
        
    def get_type(self):
        '''Return the string - whether this is 'problem' or 'domain' file.'''
        
        if self._type is None:
            self._classify()
        
        return ["problem", "domain"][int(self._type)]
        
    def _classify(self):
        '''Classify this tree as a problem or domain tree.
        Only classify if unclassified.'''
        
        if self._type is None:
            self._type = (PDDLNode.PROBLEM if self.seek(["problem"]) else PDDLNode.DOMAIN)
        
    def finalize(self):
        '''Once the tree is built, find all critical parts.'''
        
        self._classify()
        
        self.get_problem()
        self.get_domain()
        self.get_init_state()
        self.get_goal()
        
    def get_problem(self):
        ''''Return the name of the problem. Return False if no problem subtree found.
        Return False if problem subtree asked of does not represent a problem file.'''
        #Raise SyntaxError if the tree is from a Domain file
        
        if not self.is_problem():
            return False
        
        if self.problem is None:
            self.problem = self.seek(["problem"]).children[0].name
        
        return self.problem
    
    def get_domain(self):
        '''Return the name of the domain. Return False if no subtree found.'''
        
        if self.domain is None:
            if self.is_domain():
                self.domain = self.seek(["domain"]).children[0].name
            else:
                self.domain = self.seek([":domain"]).children[0].name
            
        return self.domain
    
    def get_init_state(self):
        '''Return the initial state subtree. Return False if initial state subtree not found.'''
        
        if self.init_state is None:
            self.init_state = self.seek([":init"])
            
        return self.init_state
    
    def get_goal(self):
        '''Return the goal state subtree. Return False if goal state subtree not found.'''
        
        if self.goal is None:
            self.goal = self.seek([":goal"])
            
        return self.goal
        
class PDDLParser(LispParser):
    
    def __init__(self):
        
        LispParser.__init__(self)
        
    @staticmethod
    def get_tree(expr):
        '''Return a DOM-like tree structure. 
        No need to create a fictitious root since the root element is define.'''
        
        tokens = PDDLParser.get_tokens(expr)
        #root = PDDLNode(Node.ROOT_NAME, False)
        
        # The PDDL spec is schitzoid about whether to use a Lisp syntax, or a pseudo-C syntax
        #    Lisp syntax               -        (name-of-expr arg-1 arg-2 ...)
        #    pseudo-C syntax           -        name-of-expr (arg-1 arg-2 ...)
        #
        # PDDL Lisp syntax example:
        #    PDDL syntax               -        (:predicates <predicate-1> <predicate-2> ...)
        #
        # PDDL pseudo-C example:
        #    PDDL syntax               -        :parameters (<param-1> <param-2> ...)
        #    expected Lisp syntax      -        (:parameters <param-1> <param-2> ...)
        #
        # Because of this retardation, I can't write nice, clean getters for these non-Lisp expressions
        # I have 2 choices:
        #    1. remember all the retarded expressions and handle them individually...
        #    2. change them at the token level into the expected Lisp syntax
        # 
        # I'll go for option 2.
        
        c_syntax_tokens = set([":parameters", ':precondition', ":effect"])
        
        
        i = 0
        while i < len(tokens):
            if tokens[i] in c_syntax_tokens and i < len(tokens) - 1:
                tokens[i], tokens[i + 1] = tokens[i + 1], tokens[i]
                i += 2
            else:
                i += 1
        
        return PDDLParser._make_lisp_tree_helper(tokens)
    
    @staticmethod
    def _make_lisp_tree_helper(tokens):    
        '''Helper to the make_lisp_tree function. This does most of the work.
        tokens - list of lisp tokens to make the tree out of.'''
        
        token = tokens.pop(0)
        if token == "(":
            # consider an empty expression an empty eval exression
            if tokens[0] == ")":
                tokens.pop(0)
                return PDDLNode(Node.EVAL_NAME, True)
                #return None # a null-child
            
            if tokens[0] == "(":
                # a function call on the stuff inside the next expression
                root = PDDLNode(Node.EVAL_NAME, True)
            else:
                root = PDDLNode(tokens.pop(0), True)
        
            while tokens[0] != ")":
                subtree = PDDLParser._make_lisp_tree_helper(tokens)
                if subtree is not None:
                    root.add_child(subtree)
        
            tokens.pop(0) # remove closing paren
            return root
        elif token == ")":
            raise SyntaxError("Unexpected closing paren")
        else:
            return PDDLNode(token, False)