About
=====
	Some general-purpose utilities that take PDDL 3.1 files as input and parse them

### Contents of this repo:
	* utils.py                -        general-purpose Python utilities.
	* lisp_utils.py           -        utilities to deal with lisp files with Python.
	* compare.py              -        diff engine for lisp files.
	* tree_hanger.py          -        utilities to merge external files with PDDL-generated tree.
	* tester.py               -        the runner, if you don't like typing command-line arguments.
	* samples                 -        a folder containing sample problem and domain files, used for benchmarking
	
### lisp_utils.py:
	* LispParser provides a tokenizer for lisp, as well as creates the Lisp DOM-like tree.
	* Node is a single node in the Lisp DOM-like tree.
	
### tree_hanger.py:
	* can be invoked from command line like this:
		python tree_hanger.py domain_file problem_file transator_output_file [problem_number].
	* does the modification of the relevant files in memory using the Lisp-DOM data structure from lisp_utils.py.
	
### compare.py
a lisp-specific diff engine
	* ignores whitespace.
	* pretty good at isolating the issues compared to commercial diff engines.
can be invoked from the command line like this:
	* python compare.py baseline_file generated_file.

tester.py
	* does the testing...

