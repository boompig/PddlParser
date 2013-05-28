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
            self.problem = self.seek([":problem"])
        
        return self.problem
    
    def get_domain(self):
        '''Return the domain subtree. Return False if not domain subtree found.'''
        
        if self.domain is None:
            self.domain = self.get_problem().seek([":domain"])
            
        return self.domain
    
    def get_init_state(self):
        '''Return the initial state subtree. Return False if initial state subtree not found.'''
        
        if self.init_state is None:
            self.init_state = self.get_problem().seek([("eval", 0)])
            # change the name
            self.init_state.name = ":init-state"
            
        return self.init_state
    
    def get_goal(self):
        '''Return the goal state subtree. Return False if goal state subtree not found.'''
        
        if self.goal is None:
            #path = (("eval", 2) if self.init_state is None else ("eval", 1))
            self.goal = self.get_problem().seek([("eval", -1)])
            # change the name
            self.goal.name = ":goal"
            
        return self.goal
        
class PDDLParser(LispParser):
    
    def __init__(self):
        
        LispParser.__init__(self)
        
    @staticmethod
    def get_tree(expr):
        '''Return a DOM-like tree structure.'''
        
        tokens = LispParser.get_tokens(expr)
        root = PDDLNode(Node.ROOT_NAME, False)
        
        while len(tokens) > 0:
            subtree = LispParser._make_lisp_tree_helper(tokens)
            if subtree is not None:
                root.add_child(subtree)
        
        return root