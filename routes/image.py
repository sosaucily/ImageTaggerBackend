import json
import cherrypy
from cherrypy import log as cherrylog
import sys, os, datetime
from imagetaggerlib.media import m_image as mi
import config as c

class Image(object):

	
	#Set this up with an authentication key for security
	@cherrypy.expose
	def index(self, *args, **kw):
		cherrylog("Args: " + str(kw))
		#submit a new video
#http://localhost:8080/video?submit={%22display_name%22:%22testvid%22,%22video_description%22:%22Some%20Sample%20Video%22,%22video_meta_tags%22:%22apple,banana%22,%22account_id%22:1,%22friendly_id%22:12893712}
		try:
			if 'get_images' in kw:
				get_args = json.loads(kw['get'])
				file_id = get_args['file_id']
				return ('<html><body><img src="/images/' + file_id + '" /></body></html>')
			else:
				return "Invalid Image Command"

		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
			print(exc_type, fname, exc_tb.tb_lineno)
			cherrylog (str(sys.exc_info()))
			cherrylog ("received invalid Video command")
			return "Invalid Command"
