import json
from cherrypy import log as cherrylog
import cherrypy

class PageNotFoundError(object):

	@cherrypy.expose
	def index(self, *args, **kw):
		return 'Page Not Found!'