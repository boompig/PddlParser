################################
#    Written by Daniel Kats    #
#    May 16, 2013              #
################################

''' Utilities used to compare 2 lisp files '''

from lisp_utils import LispParser
from utils import get_contents
import sys
import os

class LispDiff(object):
    '''A Lisp-specific diff engine.
    Has some advantages over commercial diff engines:
        - ignores whitespace
        - has better difference-tracking (down to symbol level)'''
    
    # how many symbols to show before and after
    CONTEXT_WINDOW = 6
    # how many symbols to look before and after and try to get match
    ALIGN_WINDOW = 2
    # how many shared tokens for a good alignment
    MATCH_WINDOW = 3

    @staticmethod
    def compare(f_baseline, f_generated):
        '''Compare the given generated file to the baseline file.'''
        
        baseline_tokens = LispParser().get_tokens(get_contents(f_baseline))
        generated_tokens = LispParser().get_tokens(get_contents(f_generated))
    
        i = j = 0
        len_match = token_match = True
        
        if len(baseline_tokens) != len(generated_tokens):
            print "different amount of tokens"
            len_match = False
        
        while i < len(baseline_tokens) and j < len(generated_tokens):
            if baseline_tokens[i] != generated_tokens[j]:
                token_match = False
                
                print "==> difference"
                
                print "Context for baseline:"
                print " ".join(baseline_tokens[i - LispDiff.CONTEXT_WINDOW : i + LispDiff.CONTEXT_WINDOW])
                
                print "Context for generated:"
                print " ".join(generated_tokens[j - LispDiff.CONTEXT_WINDOW : j + LispDiff.CONTEXT_WINDOW])
            
                # here we need a way to try to line them up again
                for ii in range(-1 - LispDiff.ALIGN_WINDOW, 1 + LispDiff.ALIGN_WINDOW):
                    if ii == 0: continue
                    
                    if baseline_tokens[i + ii : i + ii + LispDiff.MATCH_WINDOW + 1] == generated_tokens[j : j + LispDiff.MATCH_WINDOW + 1]:
                        if ii > 0:
                            print "===> roll forward %d chars" % ii
                        else:
                            print "===> roll back %d chars" % (-1 * ii)
                        
                        i += ii
                        break
                
            i += 1
            j += 1
            
        if token_match and not len_match:
            print "Tokens all match even though lengths are different"
            print len(baseline_tokens)
            print len(generated_tokens)
         
        return len_match and token_match

if __name__ == "__main__":
    usage = "python compare.py baseline_file generated_file"
    
    if len(sys.argv) != 3:
        if len(sys.argv) < 3:
            print >>sys.stderr, "Too few arguments"
        else:
            print >>sys.stderr, "Too many arguments"
        print >>sys.stderr, usage
        sys.exit(1)
        
    # check that files all exist
    for f in sys.argv[1:]:
        if not os.path.exists(f):
            print >>sys.stderr, "Given file does not exist: '%s'" % f
            sys.exit(1)
            
    f_baseline, f_generated = sys.argv[1:]
    
    # verbose stuff that isn't strictly-speaking necessary
    print "==> Input:"
    print "Baseline File -> %s" % f_baseline
    print "Generated File -> %s" % f_generated
    
    diff_engine = LispDiff
    
    if diff_engine.compare(f_baseline, f_generated):
        print "Files are identical"
    else:
        print "ERROR: files are different"
        sys.exit(1)