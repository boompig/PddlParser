################################
#    Written by Daniel Kats    #
#    May 10, 2013              #
################################

import json

def get_contents(fname):
	'''Return contents of the file for quick in-memory manipulation'''
	
	f = open(fname)
	contents = f.read()
	f.close()
	return contents

def print_dict(d):
	'''Output the dictionary in a human-readable format.'''
	
	for k, v in d.iteritems():
		print "{} ==> {}".format(k, v)
		
def print_nested_dict(d):
	'''Print a nested dictionary, as it would appear in json.'''
	
	print json.dumps(d, indent=4, separators=(',', ':'))