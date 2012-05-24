import json
import cherrypy
from imagetaggerlib import imagetagger_tools as Tools
from cherrypy import log as cherrylog
import sys, os, datetime
from imagetaggerlib.media import m_video as mv
import config as c

class Video(object):
	
	#Set this up with an authentication key for security
	#@cherrypy.tools.verify_key() #This is used to change the content-type to application/json
	@cherrypy.expose
	def index(self, *args, **kw):
		cherrylog("Args: " + str(kw))
		#submit a new video
#http://localhost:8080/video?submit={%22display_name%22:%22testvid%22,%22video_description%22:%22Some%20Sample%20Video%22,%22video_meta_tags%22:%22apple,banana%22,%22account_id%22:1,%22friendly_id%22:12893712}
		try:
			#Check that the submitted request is in a valid form
			if (not mv.MVideo.validate_cmd(kw['action'])):
				return ("Unknown command for video " + str(i))
				
			if ('friendly_id' in kw):
				kw['friendly_id'] = int(kw['friendly_id'])
			
			video_action = ""
			if 'action' in kw:
				video_action = kw['action']
			cherrylog ("Getting video operation of " + video_action)
							
			if video_action == 'submit':
				submit_args = kw
				del submit_args['action']
				cherrylog( "Received video submit with parameters: " + str(submit_args))
				if (not mv.MVideo.validate_submit_params(submit_args)):
					return ("Invalid or missing parameter for Video")

				cherrylog ("Got a submit for a valid video!  Checking to make sure this video doesn't already exist")

				#Create new MVideo object, which will make an entry in mongo
				new_video = mv.MVideo()
				if (new_video.load(alt_matching={'friendly_id':submit_args['friendly_id']} )):
					return "Video already exists"
				new_video.attributes = submit_args
				new_video.create()
				return_attributes = new_video.attributes #Why does this object contain the mongo _id attribute??
				return self.clean_attributes(return_attributes)
				
			elif video_action == 'retrieve':
				retrieve_args = kw
				del retrieve_args['action']
				cherrylog( "Received request to retrieve Video with values: " + str(retrieve_args))
				if (not mv.MVideo.validate_retrieve_params(retrieve_args)):
					return ("Invalid or missing parameter for Video")

				retrieve_video = mv.MVideo()
				if (not retrieve_video.load(alt_matching={'friendly_id':retrieve_args['friendly_id']} )):
					return ("Could not find video")
				return_attributes = retrieve_video.attributes
				return self.clean_attributes(return_attributes)

			elif video_action == 'update':
				update_args = kw
				del update_args['action']
				cherrylog("Received request to update Video with values: " + str(update_args))
				if (not mv.MVideo.validate_update_params(update_args)):
					return ("Invalid or missing parameter for Video")
				update_video = mv.MVideo()
				if (not update_video.load(alt_matching={'friendly_id':update_args['friendly_id']} )):
					return ("Could not find video")
				update_video.update(merge_data=update_args, commit=True)
				return self.clean_attributes(update_video.attributes)
				
			elif video_action == 'analyze':
				analyze_args = kw
				del analyze_args['action']
				cherrylog("Received command to analyze this video in the crowd: " + str(analyze_args))
				if (not mv.MVideo.validate_analyze_params(analyze_args)):
					return ("Invalid or missing parameter for Video")
				analyze_video = mv.MVideo()
				if (not analyze_video.load(alt_matching={'friendly_id':analyze_args['friendly_id']} )):
					return ("Could not find video")

				analyze_quality = analyze_args['quality']
				if (analyze_quality != 'premium'):
					analyze_quality = 'basic'
					
				#can include the crowds to use during analysis depending on needs and send that as a parameter
				#default in CF
				result = analyze_video.send_to_providers(quality=analyze_quality)
				if (result):
					cherrylog ("Video has been submitted to sources to process")
					return ("Analyzing!")
				else:
					cherrylog ("Something went wrong when submitting process command")
					return ("Unable to process video at this time")
					
			elif video_action == 'reprocess_metadata':
				reprocess_args = kw
				del reprocess_args['action']
				cherrylog("Received command to reprocess the metadata of video with data: " + str(reprocess_args) )
				if (not mv.MVideo.validate_reprocess_metadata_params(reprocess_args)):
					return ("Invalid or missing parameter for Video")
				reprocess_video = mv.MVideo()
				if (not reprocess_video.load(alt_matching={'friendly_id':reprocess_args['friendly_id']} )):
					return ("Could not find video.")
				reprocess_video.process_imagetagger_metadata()
				return ("Done reprocessing video!")
				
			elif video_action == 'rebuild_report':
				rebuild_args = kw
				del rebuild_args['action']
				cherrylog("Received command to rebuild the report for video with data: " + str(rebuild_args) )
				if (not mv.MVideo.validate_rebuild_report_params(rebuild_args)):
					return ("Invalid or missing parameter for Video")
				rebuild_video = mv.MVideo()
				if (not rebuild_video.load(alt_matching={'friendly_id':rebuild_args['friendly_id']} )):
					return ("Could not find video.")
				rebuild_video.build_report(report_quality=rebuild_args['quality'])
				return ("Reports have been rebuilt.")
			elif video_action == 'destroy':
				destroy_args = kw
				del destroy_args['action']
				cherrylog("Received command to destroy the video from all systems: " + str(destroy_args) )
				destroy_video = mv.MVideo()
				if (not destroy_video.load(alt_matching={'friendly_id':destroy_args['friendly_id']} )):
					return ("Could not find video.")
				destroy_video.destroy()
				return ("Video has been cleared from database and deleted.")
			else:
				return "Invalid Command"

		except Exception as e:
			Tools.print_errors("Receievd Invalid Video Command in Video Route")
			return "Invalid Command"

	@cherrypy.expose
	@cherrypy.tools.jsonify() #This is used to change the content-type to application/json
	def images(self, *args, **kw):
		friendly_id = json.loads(kw['id'])
		cherrylog("Received command to get to_process images for this video: " + str(friendly_id))
		image_video = mv.MVideo()
		if (not image_video.load(alt_matching={'friendly_id':friendly_id})):
			return ("Could not find video")
		result = image_video.get_image_json()
		if (result == []):
			cherrylog ("No images have been flagged to be analyzed yet.")
			return ("No images have been flagged to be analyzed yet.")
		if (result):
			cherrylog ("Returned to_process images for this video as json")
			return (json.dumps(result))
		else:
			cherrylog ("Something went wrong when submitting process command")
			return ("Unable to retrieve images for this video at this time")
	
	@cherrypy.expose
	def accept_video(self, video_file, *args, **kwargs):
		out = "myFile length: %s\nmyFile filename: %s\nmyFile mime-type: %s"
		# Although this just counts the file length, it demonstrates
		# how to read large files in chunks instead of all at once.
		# CherryPy reads the uploaded file into a temporary file;
		# myFile.file.read reads from that.
		cherrylog ("Got args of " + str(args) + "  and " + str(kwargs))
		new_file_name = kwargs['file_id']
		size = 0
		video_file_directory = c.configs['imagetagger']['video_file_directory']
		output_file = file(video_file_directory + new_file_name, 'wb')
		while True:
			data = video_file.file.read(8192)
			if not data:
				break
			output_file.write(data)
			size += len(data)

		output_file.close()
		return out % (size, video_file.filename, video_file.content_type)
	
	def clean_attributes(self,video_attrs):
		#Don't return the mongo ID if it's there
		if (video_attrs.has_key('_id')): del video_attrs['_id']

		#Replace any Date objects with the friendly version
		for i in video_attrs.keys():
			if type(video_attrs[i]) is datetime.datetime:
				video_attrs[i] = video_attrs[i].strftime("%Y-%m-%d %H:%M")
		return json.dumps(video_attrs)
		
		