###################################
#    Written by Shirin Sohrabi    #
#    Edited by Daniel Kats        #
#    May 16, 2013                 #
###################################

import sys
import os

def remove_existing_files(file_list):
    '''Delete the existing files in the given list.'''
    
    for item in file_list:
        if os.path.exists(item):
            os.remove(item)

def partition_translator_output(inputf):
    '''Take the output of the transaltor and split it into 4 files.
    Return the filenames as a dictionary:
        {'axioms'        :    axiom_file,
         'del_effects'   :    del_effects_file,
         'add_effects'   :    add_effects_file,
         'init_states    :    init_state_file
        }
    '''
    
    infile  = open(inputf, "r")
    
    outfiles = {
        "init_states" : inputf + "_initial_states",
        "add_effects" : inputf + "_add_effects",
        "del_effects" : inputf + "_del_effects",
        "axioms" : inputf + "_axioms"
    }
    remove_existing_files(outfiles.values())

    outfile = open(outfiles["init_states"], "w")
    
    for line in infile:
        org = line
        line = line.strip()
        
        if not line or line.startswith("Total No. of states"):
            continue
        if line.startswith(";;"):
            outfile.close()
            
            if line==";; initial state":
                outfile = open(outfiles["init_states"], "a")
            elif line==";; Add Effects":
                outfile = open(outfiles["add_effects"], "a")
            elif line==";; Delete Effects":
                outfile = open(outfiles["del_effects"], "a")
            else:
                outfile = open(outfiles["axioms"], "a")
        else:
            outfile.write(org)
    
    infile.close()
    outfile.close()
    return outfiles

if __name__ == "__main__":
    partition_translator_output(sys.argv[1])




