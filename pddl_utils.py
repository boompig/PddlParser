from lisp_utils import Node, LispParser

class PDDLNode(Node):
    '''A Node in a PDDL tree, which is has a Lisp-y syntax.'''
    
    ''' There are two types of PDDL files.'''
    PROBLEM = False
    DOMAIN = True
    
    ACTION_NAME = ":action"
    
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
        
    def get_action_name(self):
        '''Return the name of this action node. Return False if this is not an action node.'''
        
        assert len(self.children) > 0
        return self.children[0].name
    
    def get_parameters(self):
        '''Return a list of parameters of this action.
        Only relevant if this is an action node. Return False if this is not an action node.'''
        
        if self.name != self.ACTION_NAME:
            return False
        
        # seek out the index of parameters
        i = self.index_of(self.seek([":parameters"]))
        assert len(self.children) > i + 1 #TODO what happens when no parameters?
        subtree = self.children[i + 1]
        assert not subtree.name.startswith(":") #TODO what happens when parameters clause is empty?
        return [subtree.name] + [child.name for child in subtree.children]
        
    def get_preconditions(self):
        '''Return the preconditions of this action.
        Only relevant if this is an action node. Return False if this is not an action node.'''
        
        if self.name != self.ACTION_NAME:
            return False
        
        # seek out the index of precondition
        i = self.index_of(self.seek([":precondition"]))
        assert len(self.children) > i + 1
        subtree = self.children[i + 1]
        assert not subtree.name.startswith(":") #TODO what happens when precondition clause is empty?
        return subtree
    
    def get_effects(self):
        '''Return the effects of this action.
        Only relevant if this is an action node. Return False if this is not an action node.'''
        
        # seek out the index of effect
        i = self.index_of(self.seek([":effect"]))
        assert len(self.children) > i + 1 #TODO what happens when empty effect clause?
        subtree = self.children[i + 1]
        assert not subtree.name.startswith(":") #TODO what happens when empty clause is empty?
        return subtree
        
    def get_predicates(self):
        '''Return the predicates subtree. Return False if this is a problem file.'''
        
        if self._type is None:
            self._classify()
            
        if self._type == PDDLNode.PROBLEM:
            return False
        
        return self.seek([":predicates"])
        
    def get_actions(self):
        '''Return a generator over the action subtrees. Return False if this is a problem file.'''
        
        if self._type is None:
            self._classify()
            
        if self._type == PDDLNode.PROBLEM:
            return False
        
        return self.seek_all([self.ACTION_NAME])
        
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
        Return False if problem subtree asked of domain tree'''
        #Raise SyntaxError if the tree is from a Domain file
        
        
        if self._type is not None and self._type == PDDLNode.DOMAIN:
            return False
        #    raise SyntaxError("Domain file's PDDL tree has no associated problem")
        
        if self.problem is None:
            self.problem = self.seek(["problem"]).children[0].name
        
        return self.problem
    
    def get_domain(self):
        '''Return the name of the domain. Return False if the domain subtree is not found.'''
        
        if self._type is None:
            self._classify()
        
        if self.domain is None:
            if self._type == PDDLNode.DOMAIN:
                self.domain = self.seek(["domain"]).children[0].name
            else:
                self.domain = self.seek([":domain"]).children[0].name
            
        return self.domain
    
    def get_objects(self):
        '''Return a list of objects in this problem. Return False if this is a domain tree.'''
        
        if self._type is None:
            self._classify()
            
        if self._type == PDDLNode.DOMAIN:
            return False
        
        return [child.name for child in self.seek([":objects"]).children]
    
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