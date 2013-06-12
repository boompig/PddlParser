################################
#    Written by Daniel Kats    #
#    May 30, 2013              #
################################

import uuid

class Node(object):
    '''A Node in a typical ordered tree.
    
    Each node has:
        * a parent - another Node or None
        * children - list of zero or more Nodes
        * a name
        
    The children of a node are ordered in order of addition.
    Typical tree operations follow.
    
    Each node is hashed for uniqueness.
    '''
    
    @staticmethod
    def get_hash():
        '''Get a unique identifier, then hash it. Return the result.'''
        
        return hash(uuid.uuid4())
    
    def __init__(self, name):
        '''Create a node object in a tree with the given name.'''
        
        self.name = name
        self.hash = self.get_hash()
        self.children = []
        self.parent = None # can just specify via this method
        
    def add_child(self, child):
        '''Add this child to the list of children.'''
        
        child.parent = self
        self.children.append(child)
        
    def pop_children(self):
        '''Remove all children. Return the child list.'''
        
        c = self.children
        self.children = []
        return c
        
    def is_root(self):
        '''Return True iff this node is the root of the tree.'''
        
        return self.parent is None
    
    def is_child_of(self, other):
        '''Return True iff this node is a direct child of the other node.'''
        
        return self.hash in [child.hash for child in other.children]
    
    def is_descendant_of(self, other):
        '''Return True iff this node is a descendant of the other node.'''
        
        return self.is_child_of(other) or (not self.is_root() and self.parent.is_descendant_of(other))
    
    def is_parent_of(self, other):
        '''Return True iff this node is a direct parent of the other node.'''
        
        return other.is_child_of(self)
    
    def is_ancestor_of(self, other):
        '''Return True iff this node is an ancestor of the other node.'''
        
        return other.is_descendant_of(self)
    
    def index_of(self, other):
        '''Return the index of the other node in this tree's list of children.
        Return False if other is not a child of this node.'''
        
        if other not in self.children: 
            return False
        
        return [child.hash for child in self.children].index(other.hash)
    
    def first_child(self):
        '''Return the first child of this node.
        Return None if this node is childless.'''
        
        return None if len(self.children) == 0 else self.children[0]
    
    def last_child(self):
        '''Return the first child of this node.
        Return None if this node is childless.'''
        
        return None if len(self.children) == 0 else self.children[-1]
    
    def next_sibling(self):
        '''Return the sibling of this proceeding it in the DOM tree.
        Return False if this node is the root. 
        Return None if this node is the last sibling.'''
        
        if self.is_root():
            return False
        
        self_index = self.parent.index_of(self)
        if self_index == len(self.parent.children) - 1:
            return None
        else:
            return self.parent.children[self_index + 1]
        
    def prev_sibling(self):
        '''Return the sibling of this preceeding it in the DOM tree.
        Return False if this node is the root. 
        Return None if this node is the first sibling.'''
        
        if self.is_root():
            return False
        
        self_index = self.parent.index_of(self)
        if self_index == 0:
            return None
        else:
            return self.parent.children[self_index - 1]
        
    def print_tree(self, indent=0):
        '''Print the whole tree.'''
        
        '''Print ASCII horizontal representation of the tree.
        Functions will be prefaced and appended with '*' ''' 
        
        print ("|---" * indent) + self.name
    
        for child in self.children:
            child.print_tree(indent + 1)
            
    def __getitem__(self, item):
        '''Allow for indexing of tree.'''
        
        r = []
        
        for child in self.children:
            if child.name == item:
                r.append(child)
                
        if len(r) == 0:
            raise KeyError(item)
        elif len(r) == 1:
            return r[0]
        else:
            return r
        
    def __contains__(self, item):
        '''An aid to indexing of tree.'''
        
        return item in [c.name for c in self.children]
        
def _test_tree():
    '''Some very basic testing'''
    
    n = Node("root")
    n.add_child(Node("sum"))
    n.first_child().add_child(Node("1"))
    n.first_child().add_child(Node("2"))
    n.add_child(Node("product"))
    n.last_child().add_child(Node("3"))
    n.last_child().add_child(Node("2"))
    
    n.print_tree()
    
    sum_node = n.first_child()
    product_node = sum_node.next_sibling()
    product_node.print_tree()
    
    sum_node = product_node.prev_sibling()
    sum_node.print_tree()
        
if __name__ == "__main__":
    _test_tree()
    