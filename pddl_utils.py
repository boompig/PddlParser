from lisp_utils import Node, LispParser

class PDDLNode(Node):
    '''A Node in a PDDL tree, which is has a Lisp-y syntax.'''
    
    def __init__(self, fname, fn=False):
        '''Create a new node.
        fn states whether this is a function or not - used to differentiate between (sum) and sum.'''
        
        # call to super
        Node.__init__(self, fname, fn)
        self.problem = None
        self.domain = None
        self.init_state = None
        self.goal = None
        
    def finalize(self):
        '''Once the tree is built, find all critical parts.'''
        
        self.get_problem()
        self.get_domain()
        self.get_init_state()
        self.get_goal()
        
    def get_problem(self):
        ''''Return the problem subtree. Return False if no problem subtree found.'''
        
        if self.problem is None:
            self.problem = self.seek(["problem"])
        
        return self.problem
    
    def get_domain(self):
        '''Return the domain subtree. Return False if not domain subtree found.'''
        
        if self.domain is None:
            self.domain = self.seek([":domain"])
            
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