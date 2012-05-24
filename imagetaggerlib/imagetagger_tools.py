from cherrypy import log as cherrylog
import sys, os, datetime
import config as c

def print_errors(message):
	cherrylog (message)
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
	print(exc_type, fname, exc_tb.tb_lineno)
	cherrylog (str(sys.exc_info()))
	
	
def print_no_syns_to_file(no_syn_array):
	"""docstring for print_no_syns_to_file"""
	log_dir = c.configs['imagetagger']['log_dir']
	with open(log_dir + "/" + "no_syns.txt", 'a') as no_syns_file:
		for word in no_syn_array:
			no_syns_file.write(str(word) + "\n")
	no_syns_file.close()
