# This is part of the ImageTagger Keyword and Category management system
#
# Author::    Jesse Smith  (mailto:jesse@steelcorelabs.com.com)
# Copyright:: Copyright (c) 2012 ImageTagger

#Tools for use globally through cherrypy application

import cherrypy
from cherrypy import log as cherrylog
import config as c

#http://docs.cherrypy.org/dev/progguide/extending/customtools.html

def jsonify_tool_callback(*args, **kwargs):
	"""Prepare this response as json"""
	response = cherrypy.response
	response.headers['Content-Type'] = 'application/json'

cherrypy.tools.jsonify = cherrypy.Tool('before_finalize', jsonify_tool_callback, priority=25)

def verify_key(*args, **kwargs):
	"""
	Function used to verify the incoming request has 
	the remote_key as a parameter for controlled access to this system's calls.
	"""
	request = cherrypy.request
	params = request.body.request_params
	cherrylog ("Verifying key of http request params: " + str(params))
	if (params.has_key("remote_key")):
		param_key = params['remote_key']
		valid_remote_key = c.configs['imagetagger']['remote_key']
		if (param_key == valid_remote_key):
			#Strip the remote_key parameter once it has been verified.
			del cherrypy.request.body.request_params['remote_key']
			return True
	raise cherrypy.HTTPError("401 Unauthorized")
	
cherrypy.tools.verify_key = cherrypy.Tool('before_handler', verify_key, priority=25)