################################
#    Written by Daniel Kats    #
#    May 10, 2013              #
################################

def get_contents(fname):
	'''Return contents of the file for quick in-memory manipulation'''
	
	f = open(fname)
	contents = f.read()
	f.close()
	return contents