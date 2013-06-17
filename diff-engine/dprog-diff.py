gap_penalty = 1
swap_penalty = 1
none_char = "_"

class Matrix(object):
    def __init__(self, m, n):
        '''Create an m by n matrix.
        n = # of columns
        m = # of rows'''
        
        self.matrix = []
        self.width = n
        self.height = m
        self.max = 1
        
        for i in xrange(m):
             self.matrix.append([none_char] * n)
             
    def set(self, i, j, v):
        '''Set entry (i, j) to v.'''
        
        self.matrix[i][j] = v
        self.max = max(len(str(v)), self.max)
        
    def get(self, i, j):
        return self.matrix[i][j]
        
    def __str__(self):
        '''Turn this matrix to string.'''
        
        s = ""
        for i in xrange(self.height):
            s += "| " + " | ".join([str(v).rjust(self.max) for v in self.matrix[i]]) + " |\n"
            
        return s[:-1]
             
def match_score(c1, c2):
    return (0 if c1 == c2 else swap_penalty)

def get_penalty_matrix(a, b):
    '''Return the penalty matrix associated with aligning a and b.'''
    
    M = Matrix(len(a), len(b))
    
    # fill in our gap penalties for blindly shifting
    for i in xrange(len(a)):
        M.set(i, 0, i * gap_penalty)
    
    for j in xrange(len(b)):
        M.set(0, j, j * gap_penalty)
        
    for i in xrange(1, len(a)):
        for j in xrange(1, len(b)):
            
            delete = M.get(i - 1, j) + gap_penalty # suppose that we deleted a[i - 1] 
            insert = M.get(i, j - 1) + gap_penalty # suppose that we inserted a NULL at a[i - 1]
            match = M.get(i - 1, j- 1) + match_score(a[i], b[j])
            M.set(i, j, min(delete, insert, match))
            
    return M

def get_best_path(a, b, M):
    '''Return the best path back through the penalty matrix.'''
    
    i = M.height - 1
    j = M.width - 1
    aligned_a = ""
    aligned_b = ""
    # get the best path
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and M.get(i - 1, j - 1) + match_score(a[i], b[j]) == M.get(i, j):
            aligned_a = a[i] + aligned_a
            aligned_b = b[j] + aligned_b
            i -= 1
            j -= 1
        elif i > 0 and M.get(i - 1, j) + gap_penalty == M.get(i, j):
            aligned_a = a[i] + aligned_a
            aligned_b = none_char + aligned_b
            i -= 1
        elif j > 0 and M.get(i, j - 1) + gap_penalty == M.get(i, j):
            aligned_a = none_char + aligned_a
            aligned_b = b[j] + aligned_b
            j -= 1
            
    return (aligned_a, aligned_b)
    
def test_same():
    a = list("I am from Canada.")
    return (a, a[:])
        
def test_last_char_swap():
    a = list("I am from Canada.")
    b = list("I am from Canada!")
    return (a, b)

def test_last_char_del_b():
    a = list("I am from Canada")
    b = a[:-1]
    return (a, b)

def test_last_char_del_a():
    a, b = test_last_char_del_b()
    return (b, a)

def test_del_first_char():
    a = list("I am from Canada.")
    b = a[1:]
    return (a, b)

def test_multiple_dels():
    a = list("I am from Canada.")
    b = list("I am not from Canada!")
    return (a, b)
        
def main():
    #a, b = test_last_char_swap()
    #a, b = test_last_char_del_b()
    #a, b = test_last_char_del_a()
    a, b = test_multiple_dels()

    M = get_penalty_matrix(a, b)
    print str(M)
    a_prime, b_prime = get_best_path(a, b, M)
    
    print "a = %s" % "".join(a_prime)
    print "b = %s" % "".join(b_prime)
    print "==> penalty = %d" % M.get(M.height - 1, M.width - 1)
    
if __name__ == "__main__":
    main()