About:
	This folder contains scripts to add Jorge's translator's output to the problem and domain files of the HTN Planner.
	Utilizes some utilities from Shirin Sohrabi (for now)
	
Written by Daniel Kats
May 16, 2013

Files in this folder:
	+ sconvert.py             -        seperates translator output into 4 files, written by Shirin Sohrabi (edited by me)
	+ utils.py                -        general-purpose Python utilities
	+ lisp_utils.py           -        utilities to deal with lisp files with Python
	+ compare.py              -        diff engine for lisp files
	+ tree_hanger.py          -        the engine
	+ tester.py               -        the runner, if you don't like typing command-line arguments
	
lisp_utils.py:
	+ LispParser provides a tokenizer for lisp, as well as creates the Lisp DOM-like tree
	+ Node is a single node in the Lisp DOM-like tree
	
tree_hanger.py:
	+ can be invoked from command line like this:
		python tree_hanger.py domain_file problem_file transator_output_file [problem_number]
	+ does the modification of the relevant files in memory using the Lisp-DOM data structure from lisp_utils.py
	
compare.py
	+ a lisp-specific diff engine
		- ignores whitespace
		- pretty good at isolating the issues compared to commercial diff engines
	+ can be invoked from the command line like this:
		python compare.py baseline_file generated_file

tester.py
	+ runs tree_hanger.py with arguments specified in the file
	+ will error-

