import cherrypy

class Root(object):
	
	@cherrypy.expose
	def index(self):
		'''
		We overrite the get child function so that we can handle invalid
		requests
		'''
		return ("Welcome to the ImageTaggerBackend System")
